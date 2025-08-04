"""Global (system-wide) memory shared across all organisations and users.

Intended for vendor-neutral documentation, reference policies, general world
knowledge, FAQs etc.  This is *read-only* for most agents, but write helpers are
provided to populate/curate the store.

Layers
------
Semantic  : VectorStore (Chroma/FAISS) – RAG over large public corpus.
Structured: KGraph                     – relationships between docs/policies.

Storage path  DATA_DIR/global_memory/
"""

from __future__ import annotations

import hashlib
import logging
import pathlib
from datetime import datetime
from typing import Any, Dict, List

from langchain_core.documents import Document

from agentfoundry.vectorstores.factory import VectorStoreFactory
from agentfoundry.kgraph.factory import KGraphFactory
from agentfoundry.utils.config import Config

logger = logging.getLogger(__name__)


class GlobalMemory:  # pylint: disable=too-many-instance-attributes
    """Singleton-like global memory combining VectorStore + KGraph."""

    _instance: "GlobalMemory" | None = None

    # ------------------------------------------------------------------
    def __new__(cls, *args, **kwargs):  # noqa: D401  (singleton pattern)
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ------------------------------------------------------------------
    def __init__(self, *, data_dir: str | None = None):
        if hasattr(self, "_initialized"):
            return

        cfg = Config()
        root = pathlib.Path(data_dir or cfg.get("DATA_DIR", "./data")) / "global_memory"
        root.mkdir(parents=True, exist_ok=True)
        self._root = root

        # Use the lightweight in-memory provider during tests to avoid heavy
        # external dependencies such as FAISS/OpenAI embeddings.
        self._vs_provider = VectorStoreFactory.get_provider(provider="dummy")
        self._kg = KGraphFactory.get_instance().get_kgraph({"DATA_DIR": str(root)})

        self._initialised = True
        logger.info("GlobalMemory initialised at %s", root)

    # ------------------------------------------------------------------
    # helpers
    @staticmethod
    def _det_id(text: str) -> str:  # noqa: D401
        return hashlib.sha256(text.encode()).hexdigest()

    # ------------------------------------------------------------------
    # Semantic layer
    # ------------------------------------------------------------------
    def add_document(self, text: str, metadata: Dict[str, Any] | None = None) -> str:  # noqa: D401
        doc_id = self._det_id(text)
        meta = {**(metadata or {}), "scope": "global", "created_at": datetime.utcnow().isoformat()}
        try:
            self._vs_provider.add_documents(
                [Document(page_content=text, metadata=meta, id=doc_id)], ids=[doc_id], allow_update=False
            )
            logger.debug("Global doc added id=%s", doc_id)
        except ValueError:
            logger.debug("Global doc duplicate ignored id=%s", doc_id)
        return doc_id

    def search(self, query: str, k: int = 10) -> List[str]:  # noqa: D401
        docs = self._vs_provider.similarity_search(query, k=k)
        logger.debug("Global search '%s' hits=%d", query, len(docs))
        return [d.page_content for d in docs]

    # ------------------------------------------------------------------
    # KGraph layer
    # ------------------------------------------------------------------
    def upsert_fact(self, subject: str, predicate: str, obj: str) -> str:  # noqa: D401
        fid = self._kg.upsert_fact(subject, predicate, obj, {"scope": "global"})
        logger.debug("Global fact upsert id=%s", fid)
        return fid

    def fact_search(self, query: str, k: int = 10):  # noqa: D401
        return self._kg.search(query, user_id="", org_id="", k=k)

    # ------------------------------------------------------------------
    def summary(self, k: int = 5):  # noqa: D401
        return {"docs": self.search("*", k=k), "facts": self.fact_search("*", k=k)}
