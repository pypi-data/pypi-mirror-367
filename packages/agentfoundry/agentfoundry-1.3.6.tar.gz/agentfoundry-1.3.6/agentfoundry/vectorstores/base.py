"""Abstract base-class for vector-store providers.

Moved out of *providers/__init__.py* to follow the guideline that classes
belong in their own dedicated modules.
"""

from __future__ import annotations

from typing import Any, List


class VectorStore:  # noqa: D101  (minimal doc)
    """Base class for concrete vector-store provider wrappers."""

    def __init__(self, **kwargs: Any):
        self.kwargs = kwargs

    # ------------------------------------------------------------------
    # Basic operations expected by *memory_tools* and other call-sites.
    # ------------------------------------------------------------------

    def get_store(self):  # pragma: no cover
        raise NotImplementedError

    def add_documents(self, documents, **kwargs):  # type: ignore[no-self-use]
        return self.get_store().add_documents(documents, **kwargs)

    def similarity_search(self, query: str, k: int = 4, **kwargs):  # type: ignore[no-self-use]
        """Proxy to underlying store ensuring non-standard kwargs become filters.

        LangChain-compatible vector stores typically expose the signature

            similarity_search(query, k=4, filter=None, **kwargs)

        Internal AgentFoundry callers historically passed arbitrary metadata
        keywords (``org_id``, ``user_id`` …) directly – expecting the provider
        to interpret them as filter constraints.  Newer upstream versions,
        however, raise ``TypeError`` for unexpected parameters.  To stay
        backward-compatible we convert *unknown* kwargs into the ``filter``
        dict accepted by modern stores before delegating.
        """

        store = self.get_store()

        # Extract existing filter dict or create empty one.
        flt = kwargs.pop("filter", {}) or {}

        # Any remaining keyword arguments are treated as filter criteria.
        flt.update(kwargs)

        return store.similarity_search(query, k=k, filter=flt)

    def delete(self, *args, **kwargs):  # type: ignore[no-self-use]
        return self.get_store().delete(*args, **kwargs)

    # ------------------------------------------------------------------
    # Helper utilities that concrete providers often expose.
    # ------------------------------------------------------------------

    @staticmethod
    def deterministic_id(text: str, user_id: str | None, org_id: str | None) -> str:  # noqa: D401
        raise NotImplementedError

    def purge_expired(self, retention_days: int = 0) -> None:  # noqa: D401
        # Optional – providers may override.
        return None
