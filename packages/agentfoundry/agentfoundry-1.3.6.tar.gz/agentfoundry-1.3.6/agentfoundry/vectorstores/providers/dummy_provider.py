"""In-memory fallback vector-store provider for lightweight test runs.

This dummy implementation avoids heavyweight dependencies (FAISS, Chroma,
etc.) while still satisfying the subset of the LangChain VectorStore API
that AgentFoundry’s unit-tests exercise.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from langchain_core.documents import Document

from agentfoundry.vectorstores.base import VectorStore
from agentfoundry.vectorstores.factory import VectorStoreFactory


@VectorStoreFactory.register_provider("dummy")
class DummyVectorStoreProvider(VectorStore):
    """Very small in-process vector store using naive substring matching."""

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._docs: List[Document] = []

    # ------------------------------------------------------------------
    # Minimal API expected by memory_tools & kgraph layers
    # ------------------------------------------------------------------

    # The provider doubles as *its own* VectorStore instance so get_store just
    # returns *self* – this keeps the implementation compact.
    def get_store(self) -> "DummyVectorStoreProvider":
        return self

    # ---- Indexing ----------------------------------------------------- #
    def add_documents(self, documents: List[Document], **kwargs):  # type: ignore[override]
        self._docs.extend(documents)
        return []  # upstream returns list of IDs – not used in tests

    def add_texts(self, texts: List[str], *, metadatas: List[Dict] | None = None, ids: List[str] | None = None, **kwargs):  # noqa: E501
        metadatas = metadatas or [{}] * len(texts)
        for text, meta, doc_id in zip(texts, metadatas, ids or [None] * len(texts)):
            if doc_id:
                meta = dict(meta or {})
                meta.setdefault("id", doc_id)
            self._docs.append(Document(page_content=text, metadata=meta))
        return ids or []

    # ---- Search ------------------------------------------------------- #
    def similarity_search(self, query: str, k: int = 4, filter: Dict | None = None, **kwargs):  # type: ignore[override]  # noqa: D401,E501
        hits = [d for d in self._docs if _match(d, query, filter)]
        # Return the *documents* only – LangChain’s API for this method
        # ignores distance/score.
        return hits[:k]

    def similarity_search_with_score(self, query: str, k: int = 4, filter: Dict | None = None, **kwargs):  # noqa: E501
        results: List[Tuple[Document, float]] = []
        for d in self._docs:
            if not _match(d, query, filter):
                continue
            # Crude scoring: inverse of position index – adequate for tests
            score = 1.0 / (len(results) + 1)
            results.append((d, score))
            if len(results) >= k:
                break
        return results

    # ---- Maintenance -------------------------------------------------- #
    def delete(self, ids: List[str] | None = None, **kwargs):  # type: ignore[override]
        if ids is None:
            self._docs.clear()
            return 0
        before = len(self._docs)
        self._docs = [d for d in self._docs if d.metadata.get("id") not in ids]
        return before - len(self._docs)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _match(doc: Document, query: str, filter: Dict | None) -> bool:  # noqa: D401
    if filter:
        for k, v in filter.items():
            if doc.metadata.get(k) != v:
                return False
    return query.lower() in doc.page_content.lower()

