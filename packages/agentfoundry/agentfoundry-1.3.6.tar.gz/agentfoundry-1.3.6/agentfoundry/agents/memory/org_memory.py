"""Long-term organization-level memory shared across all users in an org.

Layers used
-----------
Semantic (RAG)
    • VectorStore (Chroma/FAISS) for company docs, historic chats, etc.

Structured
    • KGraph for compliance / policy triples and any other relational facts.

All data lives under DATA_DIR/org_memory/<org_id>/ so that removing that directory wipes all org-wide memory in one go.
"""

from __future__ import annotations

import hashlib
import logging
import pathlib
from datetime import datetime, timezone
from typing import Any, Dict, List

from langchain_core.documents import Document

from agentfoundry.utils.config import Config
from agentfoundry.vectorstores.factory import VectorStoreFactory
from agentfoundry.kgraph.factory import KGraphFactory

logger = logging.getLogger(__name__)


class OrgMemory:  # pylint: disable=too-many-instance-attributes
    """Persistent, shared memory for a whole organization/team."""

    # ------------------------------------------------------------------
    def __init__(self, org_id: str, *, data_dir: str | None = None):
        self.org_id = org_id

        cfg = Config()
        root = pathlib.Path(data_dir or cfg.get("DATA_DIR", "./data")) / "org_memory" / org_id
        # Directory creation is delegated to storage providers.
        self._root = root

        # Vector store initialisation ------------------------------------------------
        self._vs_provider = VectorStoreFactory.get_provider(org_id=self.org_id)

        # KGraph provider ------------------------------------------------------------
        self._kg = KGraphFactory.get_instance().get_kgraph({"DATA_DIR": str(root)})

        logger.info("OrgMemory initialized for org=%s (path=%s)", org_id, root)

    # ------------------------------------------------------------------
    # Helper – deterministic ID (text + org)
    # ------------------------------------------------------------------
    @staticmethod
    def _det_id(text: str, org_id: str) -> str:  # noqa: D401
        return hashlib.sha256(f"{org_id}|{text}".encode()).hexdigest()

    # ------------------------------------------------------------------
    # Semantic layer
    # ------------------------------------------------------------------
    def add_semantic_item(self, text: str, metadata: Dict[str, Any] | None = None) -> str:
        """Store *text* in organisation-wide vector store."""

        doc_id = self._det_id(text, self.org_id)
        meta = {
            **(metadata or {}),
            "org_id": self.org_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            self._vs_provider.add_documents(
                [Document(page_content=text, metadata=meta, id=doc_id)], ids=[doc_id], allow_update=False
            )
            logger.debug("Org semantic item added id=%s", doc_id)
        except ValueError:
            logger.debug("Org semantic item already exists id=%s", doc_id)
        return doc_id

    def semantic_search(self, query: str, k: int = 8) -> List[str]:  # noqa: D401
        """Return docs within org where user_id==0 (public org docs)."""

        docs = self._vs_provider.similarity_search(
            query,
            org_id=self.org_id,
            caller_role_level=10,
            user_id=0,
            k=k,
        )
        logger.debug("Org semantic search '%s' returned %d hits", query, len(docs))
        return [d.page_content for d in docs]

    # ------------------------------------------------------------------
    # KGraph layer
    # ------------------------------------------------------------------
    def upsert_fact(self, subject: str, predicate: str, obj: str) -> str:  # noqa: D401
        meta = {"user_id": "", "org_id": self.org_id}
        fid = self._kg.upsert_fact(subject, predicate, obj, meta)
        logger.debug("Org fact upserted id=%s", fid)
        return fid

    def fact_search(self, query: str, k: int = 10):  # noqa: D401
        return self._kg.search(query, user_id="", org_id=self.org_id, k=k)

    # ------------------------------------------------------------------
    def summary(self, k: int = 5) -> Dict[str, Any]:  # noqa: D401
        """Quick snapshot combining both layers."""

        return {
            "sample_docs": self.semantic_search("*", k=k),
            "sample_facts": self.fact_search("*", k=k),
        }
