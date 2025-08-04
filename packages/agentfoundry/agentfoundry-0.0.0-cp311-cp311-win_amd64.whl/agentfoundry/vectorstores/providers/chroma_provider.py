"""ChromaDB vector-store provider implementation."""

from __future__ import annotations

from typing import Any, Dict

from .chroma_client import ChromaDBClient
from agentfoundry.utils.config import Config
from agentfoundry.utils.logger import get_logger

from agentfoundry.vectorstores.base import VectorStore
from agentfoundry.vectorstores.factory import VectorStoreFactory


@VectorStoreFactory.register_provider("chroma")
class ChromaVectorStoreProvider(VectorStore):
    """Wrap `ChromaDBClient` to fit the VectorStore provider interface."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        _ = Config()

        self.logger = get_logger(self.__class__.__name__)

        org_id = kwargs.get("org_id") or "global"

        # ChromaDBClient derives its own persistence directory from Config.
        self.client = ChromaDBClient()
        self._store = self.client.as_vectorstore(org_id=org_id)

    # ------------------------------------------------------------------
    # Provider API
    # ------------------------------------------------------------------

    def get_store(self):
        """Return the LangChain VectorStore instance."""
        self.logger.debug("ChromaVectorStoreProvider.get_store called")
        return self._store

    # ------------------------------------------------------------------
    # Helpers that memory_tools expects
    # ------------------------------------------------------------------

    @staticmethod
    def deterministic_id(text: str, user_id: str | None, org_id: str | None) -> str:  # noqa: D401,E501
        """Expose ChromaDBClient's deterministic ID helper."""

        return ChromaDBClient.get_deterministic_id(text, user_id, org_id)  # type: ignore[attr-defined]

    def purge_expired(self, retention_days: int = 90) -> None:
        self.logger.debug("ChromaVectorStoreProvider.purge_expired days=%d", retention_days)
        self.client.purge_expired(retention_days=retention_days)
        self.logger.info("ChromaVectorStoreProvider purged entries older than %d days", retention_days)
