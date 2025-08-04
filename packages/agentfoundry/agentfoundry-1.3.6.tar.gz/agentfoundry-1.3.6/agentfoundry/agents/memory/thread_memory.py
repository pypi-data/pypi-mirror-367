"""Short-term per-thread memory based on a dedicated FAISS index.

Each (user_id, thread_id) pair gets its own FAISS vector index persisted
beneath   DATA_DIR/memory_cache/threads/<user>/<thread>/.

Only *ephemeral* context is stored – typically the last few dozen messages –
so the index stays tiny and similarity search remains fast.
"""

from __future__ import annotations

import hashlib
import json
import logging
import pathlib
from datetime import datetime
from typing import Any, List

# ---------------------------------------------------------------------------
# Optional DuckDB dependency
# ---------------------------------------------------------------------------

try:
    import duckdb  # type: ignore
except ModuleNotFoundError:  # pragma: no cover – fallback for minimal installs
    import sqlite3 as _sqlite3  # type: ignore

    class _SQLiteDuckCompatConnection:
        """Very small compatibility shim – exposes duckdb’s .execute API subset
        using the builtin sqlite3 module. Only supports the statements used
        in ThreadMemory (CREATE TABLE, INSERT, DELETE, SELECT)."""

        def __init__(self, path: str):
            self._conn = _sqlite3.connect(path)

        def execute(self, sql: str, params: list | tuple | None = None):  # noqa: D401
            cur = self._conn.cursor()
            cur.execute(sql, params or [])
            self._conn.commit()
            return cur

        def fetchone(self):  # type: ignore[override]
            raise RuntimeError("fetchone not called directly on connection")

        def fetchall(self):  # type: ignore[override]
            raise RuntimeError("fetchall not called directly on connection")

    class duckdb:  # type: ignore
        """Shim module exposing connect(...) like duckdb but backed by sqlite."""

        @staticmethod
        def connect(path: str):  # noqa: D401
            return _SQLiteDuckCompatConnection(path)
from langchain_core.documents import Document
# Embedding backend – default to OpenAI, fallback to FakeEmbeddings when the
# environment lacks an API key (common in local development / CI).
from langchain_openai.embeddings import OpenAIEmbeddings

# Gracefully handle environments without openai package.
try:
    from openai import OpenAIError  # type: ignore
except Exception:  # pragma: no cover
    class OpenAIError(Exception):
        """Fallback dummy when openai lib unavailable."""

        pass

# Resolve embeddings instance lazily below
from langchain_community.vectorstores import FAISS

from agentfoundry.utils.config import Config

logger = logging.getLogger(__name__)


class ThreadMemory:  # pylint: disable=too-many-instance-attributes
    """Per-conversation short-term memory using FAISS + DuckDB."""

    try:
        _EMBEDDINGS = OpenAIEmbeddings()  # shared across instances – light weight
    except (OpenAIError, ValueError):  # pragma: no cover – missing API key etc.
        from langchain_community.embeddings import FakeEmbeddings

        _EMBEDDINGS = FakeEmbeddings(size=1536)

    # ------------------------------------------------------------------
    def __init__(self, *, user_id: str, thread_id: str, org_id: str | None = None, data_dir: str | None = None,) -> None:
        self.user_id = user_id
        self.thread_id = thread_id
        if org_id is None:
            org_id = Config().get("ORG_ID")
        if not org_id:
            raise ValueError("ThreadMemory requires org_id (param or config ORG_ID)")
        self.org_id = str(org_id)

        cfg = Config()
        root = (
            pathlib.Path(data_dir or cfg.get("DATA_DIR", "./data"))
            / "memory_cache"
            / "threads"
            / f"org_{self.org_id}"
            / user_id
            / thread_id
        )
        root.mkdir(parents=True, exist_ok=True)

        self._db_path = root / "context.duckdb"
        self._index_path = root / "faiss.idx"

        self._conn = duckdb.connect(str(self._db_path))
        self._ensure_schema()

        self._index = self._load_index()

        logger.info("ThreadMemory initialised user=%s thread=%s", user_id, thread_id)

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def add(self, text: str, metadata: dict[str, Any] | None = None) -> str:
        """Add *text* to this thread-memory if not already present."""

        meta = {
            **(metadata or {}),
            "user_id": self.user_id,
            "thread_id": self.thread_id,
            "org_id": self.org_id,
            "created_at": datetime.utcnow().isoformat(),
            "role_level": 0,
        }
        doc_id = self._det_id(text)

        if self._doc_exists(doc_id):
            logger.debug("skip duplicate message id=%s", doc_id)
            return doc_id

        self._index.add_documents([Document(page_content=text, metadata=meta, id=doc_id)], ids=[doc_id])
        self._persist_index()

        self._conn.execute("INSERT INTO turns VALUES (?, ?, ?)",[doc_id, text, json.dumps(meta)])
        logger.debug("added message id=%s", doc_id)
        return doc_id

    def similarity_search(self, query: str, k: int = 5) -> List[str]:
        docs = self._index.similarity_search(
            query,
            k=k,
            filter={"user_id": self.user_id, "thread_id": self.thread_id},
        )
        return [d.page_content for d in docs]

    def clear(self):  # noqa: D401
        self._conn.execute("DELETE FROM turns")
        self._index = FAISS.from_documents([], self._EMBEDDINGS)
        self._persist_index()
        logger.info("ThreadMemory cleared for %s/%s", self.user_id, self.thread_id)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _ensure_schema(self):
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS turns (
                   id TEXT PRIMARY KEY,
                   text TEXT,
                   meta TEXT
               )"""
        )

    def _det_id(self, text: str) -> str:
        return hashlib.sha256(f"{self.user_id}|{self.thread_id}|{text}".encode()).hexdigest()

    def _doc_exists(self, doc_id: str) -> bool:
        row = self._conn.execute("SELECT 1 FROM turns WHERE id=?", [doc_id]).fetchone()
        return row is not None

    # ---------- FAISS persistence ------------------------------------
    def _load_index(self) -> FAISS:
        if self._index_path.exists():
            try:
                return FAISS.load_local(str(self._index_path), self._EMBEDDINGS)
            except Exception as exc:  # pragma: no cover
                logger.warning(
                    "Failed to load FAISS index for %s/%s: %s; recreating", self.user_id, self.thread_id, exc
                )

        # Work-around for langchain_community.faiss which raises IndexError
        # when initialising an empty index (no embeddings). We create a tiny
        # placeholder doc without user/thread metadata so that later
        # similarity_search calls filtered by these fields will never return
        # it, effectively giving us an empty index but with a valid FAISS
        # structure.
        from langchain_core.documents import Document  # local import to avoid cycle

        placeholder = Document(page_content="", metadata={"_placeholder": True})
        return FAISS.from_documents([placeholder], self._EMBEDDINGS)

    def _persist_index(self):
        self._index.save_local(str(self._index_path))
