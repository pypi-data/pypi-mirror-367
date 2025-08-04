"""FAISS vector-store provider implementation."""

from __future__ import annotations

import os

from agentfoundry.utils.config import Config
from agentfoundry.utils.logger import get_logger

from agentfoundry.vectorstores.base import VectorStore
from agentfoundry.vectorstores.factory import VectorStoreFactory


@VectorStoreFactory.register_provider("faiss")
class FAISSVectorStoreProvider(VectorStore):
    """Local persistent FAISS index wrapped as a LangChain VectorStore."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        from langchain_community.vectorstores import FAISS  # local import to delay heavy deps
        from langchain_openai.embeddings import OpenAIEmbeddings
        from langchain_core.documents import Document

        cfg = Config()

        index_path: str = cfg.get("FAISS.INDEX_PATH", "./faiss_index")
        embeddings = OpenAIEmbeddings()

        logger = get_logger(self.__class__.__name__)

        if os.path.exists(index_path):
            logger.info("Loading FAISS index from %s", index_path)
            self._store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        else:
            logger.info("Creating new FAISS index at %s", index_path)
            self._store = FAISS.from_documents(
                [Document(page_content="Initial page", metadata={"system": True})], embeddings
            )
            self._store.save_local(index_path)

    # ------------------------------------------------------------------
    def get_store(self):
        logger = get_logger(self.__class__.__name__)
        logger.debug("FAISSVectorStoreProvider.get_store called")
        return self._store
