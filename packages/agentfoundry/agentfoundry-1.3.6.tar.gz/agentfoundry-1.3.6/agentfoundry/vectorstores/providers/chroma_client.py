# Moved from agentfoundry/chroma/client.py

from __future__ import annotations

import datetime
import pathlib
import sys

# Ensure the project root (one level above the *agentfoundry* package) is on
# sys.path when this file is executed directly ("python .../chroma_client.py").
# This avoids `ModuleNotFoundError: agentfoundry` in such ad-hoc runs while
# having no effect when the package is imported normally.
_project_root = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_project_root))

import os
import hashlib
import shutil
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, Dict, List

from chromadb import HttpClient, PersistentClient
from chromadb.types import Collection
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from chromadb.errors import NotFoundError
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

from agentfoundry.utils.config import Config
from agentfoundry.utils.logger import get_logger


# ---------------------------------------------------------------------------
# ChromaDBClient
# ---------------------------------------------------------------------------

class ChromaDBClient:
    """Single client capable of handling multiple organisation collections."""

    def __init__(
        self,
        *,
        persist_directory: str | None = None,
        settings: Dict[str, Any] | None = None,
    ):
        self.logger = get_logger(self.__class__.__name__)
        cfg = Config()

        # ------------------------------------------------------------------
        # Connection mode priority:
        #   1. Explicit URL in config key "CHROMA.URL" (e.g., https://example.org)
        #   2. Separate host/port keys (legacy)
        #   3. Local embedded DuckDB persistence directory.
        # ------------------------------------------------------------------

        chroma_url = cfg.get("CHROMA.URL")
        print(f"Connecting to chroma at: {chroma_url}")

        if chroma_url:  # ---- remote via URL ---------------------------------
            from urllib.parse import urlparse

            # Accept both bare hostnames ("example.com") and full URLs ("https://example.com:443/")
            parsed = urlparse(chroma_url if "://" in chroma_url else f"https://{chroma_url}")

            host = parsed.hostname or chroma_url  # fallback to the raw value
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
            use_ssl = parsed.scheme == "https"

            self.logger.info(
                "Connecting to remote ChromaDB via URL %s (resolved %s:%s, ssl=%s)",
                chroma_url,
                host,
                port,
                use_ssl,
            )
            headers = cfg.get("CHROMA.HEADERS", None)
            # The chromadb.HttpClient exposes an `ssl` boolean flag; pass it so that
            # HTTPS endpoints (typically port 443) work instead of failing with the
            # "plain HTTP request was sent to HTTPS port" error.
            self.client = HttpClient(host=host, port=port, ssl=use_ssl, headers=headers)  # type: ignore[assignment]

        else:  # ---- no URL; try legacy host/port or fallback to local -------
            host = cfg.get("CHROMA.HOST")
            port = int(cfg.get("CHROMA.PORT", 8000))
            # Allow explicit SSL override with CHROMA.SSL=true, else infer from port 443
            use_ssl = bool(cfg.get("CHROMA.SSL", str(port) == "443"))
            headers = cfg.get("CHROMA.HEADERS", None)

            if host:  # legacy remote mode
                self.logger.info(
                    "Connecting to remote ChromaDB at %s:%s (ssl=%s)", host, port, use_ssl
                )
                self.client = HttpClient(
                    host=host, port=port, ssl=use_ssl, headers=headers  # type: ignore[assignment]
                )
            else:
                data_dir = cfg.get("DATA_DIR") or "."
                # Prefer generic PERSISTENCE_DIR override else fall back to legacy CHROMA.PERSIST_DIR
                persist_directory = persist_directory or cfg.get(
                    "PERSISTENCE_DIR", cfg.get("CHROMA.PERSIST_DIR", os.path.join(data_dir, "chromadb"))
                )
                os.makedirs(persist_directory, exist_ok=True)
                self.logger.info("Connecting to local ChromaDB at %s", persist_directory)
                print(f"Connecting to local ChromaDB at {persist_directory}")
                self.client = PersistentClient(path=persist_directory, settings=settings)  # type: ignore[assignment]

        # ---- Embeddings -------------------------------------------- #
        # SentenceTransformerEmbeddingFunction dropped *use_auth_token* in
        # sentence-transformers ≥ 3.0.  Pass it only when present in the
        # function signature to avoid the deprecation warning.

        _model_name = cfg.get("EMBEDDING.MODEL_NAME", "paraphrase-MiniLM-L6-v2")
        _hf_token = cfg.get("HF_TOKEN")

        try:
            import inspect

            sig = inspect.signature(SentenceTransformerEmbeddingFunction)
            if "use_auth_token" in sig.parameters and _hf_token:
                self.embedding_function = SentenceTransformerEmbeddingFunction(
                    model_name=_model_name, use_auth_token=_hf_token
                )
            else:
                self.embedding_function = SentenceTransformerEmbeddingFunction(model_name=_model_name)
        except Exception:
            # Fallback: instantiate without optional args
            self.embedding_function = SentenceTransformerEmbeddingFunction(model_name=_model_name)

        # ------------------------------------------------------------------
        # Compatibility shim – older versions of `SentenceTransformerEmbeddingFunction`
        # exposed an ``embed_documents`` helper that LangChain expects, whereas
        # newer releases only implement ``__call__``.  Provide a thin alias so
        # that downstream code works regardless of the installed version.
        # ------------------------------------------------------------------

        if not hasattr(self.embedding_function, "embed_documents"):
            self.embedding_function.embed_documents = self.embedding_function  # type: ignore[attr-defined]
        if not hasattr(self.embedding_function, "embed_query"):
            self.embedding_function.embed_query = self.embedding_function  # type: ignore[attr-defined]

        # Cache for per-organisation collections
        self._collections: Dict[str, Collection] = {}

        # Ensure a global collection exists
        self._collections["global"] = self.client.get_or_create_collection(
            "global_memory", embedding_function=self.embedding_function
        )

    def get_collections(self):
        """Get all collections from the ChromaDB client.

        Returns:
            List[Collection]: List of ChromaDB collections
        """
        self.logger.info("Called")
        return self.client.list_collections()

    def create_collection(self, collection_name: str):
        """Create a new collection in the ChromaDB client.

        Args:
            collection_name (str): Name of the collection to create

        Returns:
            Collection: The created ChromaDB collection
        """
        self.logger.info(f"Creating collection '{collection_name}'")
        return self.client.get_or_create_collection(collection_name, embedding_function=self.embedding_function)
    
    def delete_collection(self, collection_name: str):
        """Delete a collection from the ChromaDB client.

        Args:
            collection_name (str): Name of the collection to delete
        """
        self.logger.info(f"Deleting collection '{collection_name}'")
        try:
            self.client.delete_collection(collection_name)
        except NotFoundError as e:
            self.logger.warning(f"Collection: {collection_name} not found for deletion.")

    # -------------------------- Helpers ----------------------------- #
    def get_collection(self, org_id: str) -> Collection:  # noqa: D401
        """Return (and cache) the collection for *org_id*."""

        if org_id not in self._collections:
            coll_name = f"{org_id}_memory"
            self._collections[org_id] = self.client.get_or_create_collection(
                coll_name, embedding_function=self.embedding_function
            )
        return self._collections[org_id]

    @staticmethod
    def get_deterministic_id(text: str, user_id: str | None, org_id: str | None) -> str:
        h = hashlib.sha256()
        h.update(text.encode("utf-8"))
        h.update((user_id or "").encode("utf-8"))
        h.update((org_id or "").encode("utf-8"))
        return h.hexdigest()

    # ---------------------- Public helpers ------------------------- #
    @lru_cache(maxsize=128)
    def as_vectorstore(
        self,
        *,
        org_id: str | None = None,
        collection: str | None = None,
        embeddings: Embeddings | None = None,
    ) -> Chroma:
        """Return a LangChain-Chroma wrapper for the requested collection.

        If *org_id* is given and *collection* is not, the collection is named
        "<org_id>_memory".  When both are None the provider's default
        collection is used – suitable for unit tests.
        """

        if collection is None:
            if org_id:
                collection = f"{org_id}_memory"
            else:
                collection = self.collection.name

        emb_fn = embeddings or self.embedding_function

        # make sure collection exists when org_id path used
        if org_id:
            self.get_collection(org_id)

        return Chroma(client=self.client, collection_name=collection, embedding_function=emb_fn)

    def purge_expired(self, retention_days: int = 90) -> None:
        cutoff = (datetime.now(datetime.UTC) - timedelta(days=retention_days)).isoformat()
        for coll in self.client.list_collections():
            coll.delete(where={"created_at": {"$lt": cutoff}})

    # Simple proxy to the underlying collection's similarity_search so that
    # example harnesses (and callers) can use the client directly without
    # going through as_vectorstore().
    def similarity_search(
        self,
        query: str,
        *,
        org_id: str,
        caller_role_level: int = 0,
        user_id: str | None = None,
        k: int = 4,
    ):
        """Return similar docs filtered by role/user within *org_id* collection."""

        coll = self.get_collection(org_id)

        where: Dict[str, Any] = {"role_level": {"$lte": caller_role_level}}
        if user_id is not None:
            where["user_id"] = user_id

        return coll.query(query_texts=[query], n_results=k, where=where).get("documents", [[]])[0]

    # Legacy-compatible API (store_results etc.) kept identical ------ #
    def store_results(self, results: List[Dict[str, Any]], *, org_id: str) -> None:
        new_ids: List[str] = []
        new_docs: List[str] = []
        new_metas: List[Dict[str, Any]] = []

        for res in results:
            text = res.get("text", "").strip()
            if not text:
                self.logger.warning("Result missing 'text'; skipping")
                continue

            meta = res.get("metadata", {})
            user_id = meta.get("user_id")
            org_id = meta.get("org_id")
            deterministic_id = self.get_deterministic_id(text, user_id, org_id)

            coll = self.get_collection(org_id)
            already = coll.get(ids=[deterministic_id])
            if already.get("ids"):
                continue

            new_ids.append(deterministic_id)
            new_docs.append(text)
            new_metas.append(meta)

        if new_ids:
            coll.add(ids=new_ids, documents=new_docs, metadatas=new_metas)


if __name__ == '__main__':
    # Example usage and basic test
    client = ChromaDBClient()
    print("Collections:", client.get_collections())
    client.create_collection('TestCollection')
    print("Collections:", client.get_collections())
    client.delete_collection('TestCollection')
    print("Collections:", client.get_collections())

    # Test deterministic ID generation
    text = "Hello, world!"
    user_id = "test_user"
    org_id = "agentfoundry"
    det_id = client.get_deterministic_id(text, user_id, org_id)
    print("Deterministic ID:", det_id)

    result = [{"text": text, "metadata": {"user_id": user_id, "org_id": org_id}}]
    client.store_results(result, org_id=org_id)

    similar_text = "Hi, planet!"
    retrieved = client.similarity_search(similar_text, org_id=org_id, k=1)
    print("Retrieved via similar text (Hi, planet):", retrieved[0].page_content if retrieved else "Not found")

    retrieved = client.similarity_search("quantum computing", org_id=org_id, k=1)
    print("Retrieved via similar text (quantum computing):", retrieved[0].page_content if retrieved else "Not found")
