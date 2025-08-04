"""Long-term per-user memory combining semantic, graph and profile stores."""

from __future__ import annotations

import hashlib
import json
import logging
import pathlib
from datetime import datetime
from typing import Any, Dict, List

import duckdb
from langchain_core.documents import Document

from agentfoundry.utils.config import Config
from agentfoundry.vectorstores.factory import VectorStoreFactory
from agentfoundry.kgraph.factory import KGraphFactory

logger = logging.getLogger(__name__)


class UserMemory:  # pylint: disable=too-many-instance-attributes
    """Unified long-term user memory.

    Layers:
        • VectorStore  – semantic search across all user documents/utterances.
        • KGraph       – structured triples (facts, relationships).
        • Profile DB   – typed key/value records (preferences, settings …).
    """

    def __init__(self, user_id: str, org_id: str | None = None, *, data_dir: str | None = None):
        self.user_id = user_id
        # Resolve organisation id – mandatory for namespacing collections/facts
        if org_id is None:
            org_id = Config().get("ORG_ID")
        if not org_id:
            raise ValueError("UserMemory initialization requires org_id (either parameter or config ORG_ID)")
        self.org_id = str(org_id)

        cfg = Config()
        if org_id is None:
            org_id = cfg.get("ORG_ID", None)
        if org_id is None:
            raise ValueError("UserMemory initialisation requires org_id (either parameter or config ORG_ID)")

        root = pathlib.Path(data_dir or cfg.get("DATA_DIR", "./data")) / "user_memory" / user_id
        root.mkdir(parents=True, exist_ok=True)
        self._root = root

        # ---------------- Profile DB (DuckDB) ------------------- #
        self._db_path = root / "profile.duckdb"
        self._conn = duckdb.connect(str(self._db_path))
        self._ensure_profile_schema()

        # ---------------- Vector store --------------------------- #
        self._vs_provider = VectorStoreFactory.get_provider(org_id=self.org_id)

        # ---------------- Knowledge graph ----------------------- #
        self._kg = KGraphFactory.get_instance().get_kgraph({"DATA_DIR": str(root)})

        logger.info("UserMemory initialised for %s (at %s)", user_id, root)

    # ------------------------------------------------------------------
    # Semantic layer helpers
    # ------------------------------------------------------------------

    def _det_id(self, text: str) -> str:
        h = hashlib.sha256()
        h.update(f"{self.user_id}|{text}".encode())
        return h.hexdigest()

    def add_semantic_item(self, text: str, *, role_level: int = 0, metadata: Dict[str, Any] | None = None,) -> str:
        """Store *text* with given role_level (default 0) for this user."""

        doc_id = self._det_id(text)
        meta = {
            **(metadata or {}),
            "user_id": self.user_id,
            "org_id": self.org_id,
            "role_level": role_level,
            "created_at": datetime.utcnow().isoformat(),
        }
        try:
            self._vs_provider.add_documents(
                [Document(page_content=text, metadata=meta, id=doc_id)], ids=[doc_id], allow_update=False
            )
            logger.debug("Semantic item added id=%s", doc_id)
        except ValueError:  # duplicate id
            logger.debug("Semantic item already existed id=%s", doc_id)
        return doc_id

    def semantic_search(self, query: str, *, caller_role_level: int = 0, k: int = 5) -> List[str]:
        """Return docs with role_level ≤ caller_role_level for this user."""

        results = self._vs_provider.similarity_search(
            query,
            org_id=self.org_id,
            caller_role_level=caller_role_level,
            user_id=self.user_id,
            k=k,
        )
        logger.debug("Semantic search '%s' returned %d hits", query, len(results))
        return [d.page_content for d in results]

    # ------------------------------------------------------------------
    # Structured knowledge-graph helpers
    # ------------------------------------------------------------------

    def upsert_fact(self, subject: str, predicate: str, obj: str) -> str:
        meta = {"user_id": self.user_id, "org_id": self.org_id}
        fid = self._kg.upsert_fact(subject, predicate, obj, meta)
        logger.debug("Fact upserted id=%s", fid)
        return fid

    def fact_search(self, query: str, k: int = 5):  # noqa: D401
        return self._kg.search(query, user_id=self.user_id, org_id=self.org_id, k=k)

    # ------------------------------------------------------------------
    # Profile helpers
    # ------------------------------------------------------------------

    def _ensure_profile_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS profile (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )

    def set_profile_field(self, key: str, value: Any) -> None:  # noqa: D401
        self._conn.execute("INSERT OR REPLACE INTO profile VALUES (?, ?)", [key, json.dumps(value)])
        logger.debug("Profile field set %s=%s", key, value)

    def get_profile_field(self, key: str, default: Any | None = None) -> Any:  # noqa: D401
        row = self._conn.execute("SELECT value FROM profile WHERE key = ?", [key]).fetchone()
        return json.loads(row[0]) if row else default

    def profile_dict(self) -> Dict[str, Any]:  # noqa: D401
        rows = self._conn.execute("SELECT key, value FROM profile").fetchall()
        return {k: json.loads(v) for k, v in rows}

    # ------------------------------------------------------------------
    # Summary/utility
    # ------------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:  # noqa: D401
        return {
            "profile": self.profile_dict(),
            "facts": self.fact_search("*", k=10),
        }
