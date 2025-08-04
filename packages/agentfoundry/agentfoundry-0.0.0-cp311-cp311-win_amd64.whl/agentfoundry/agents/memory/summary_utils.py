"""Utility for summarising long-term memories using LangChain summarisation chains."""

from __future__ import annotations

from typing import List

from langchain_core.documents import Document

from agentfoundry.utils.logger import get_logger
from agentfoundry.vectorstores.factory import VectorStoreFactory

logger = get_logger(__name__)


def _estimate_tokens(text: str) -> int:
    return len(text) // 4 + 1


def summarize_memory(
    store_filter: dict | None = None,
    *,
    org_id: str | None = None,
    max_tokens: int = 32_000,
) -> str:
    """Summarise the vector-store documents that match *store_filter*.

    Parameters
    ----------
    store_filter: dict | None
        Metadata filter passed to `similarity_search`. Use `{}` to fetch all.
    max_tokens: int
        Hard cap on the returned summary size.
    """

    try:
        from langchain.chains.summarize import load_summarize_chain
        from agentfoundry.llm.llm_factory import LLMFactory

        llm = LLMFactory.get_llm_model()
    except Exception as err:  # pragma: no cover – missing deps during tests
        logger.warning("Summarisation chain unavailable: %s", err)
        load_summarize_chain = None  # type: ignore
        llm = None  # type: ignore

    # ------------------------------------------------------------------
    # Collect candidate documents from the requested organisation-level
    # store *plus* the global store so the summary reflects both.
    # ------------------------------------------------------------------

    docs: List[Document] = []

    try:
        # Org-scoped collection (or global if org_id None)
        org_store = VectorStoreFactory.get_store(org_id=org_id)
        docs.extend(org_store.similarity_search("*", k=999_999, where=store_filter or {}))

        # Add global store when org_id is provided so that summaries include
        # neutral information that may live there.
        if org_id:
            global_store = VectorStoreFactory.get_store()
            docs.extend(global_store.similarity_search("*", k=999_999, where=store_filter or {}))
    except Exception as err:  # pragma: no cover – provider issues
        logger.warning("Vector-store retrieval failed: %s", err)

    if not docs:
        return ""

    total_chars = sum(len(d.page_content) for d in docs)
    est_tokens = _estimate_tokens("x" * total_chars)

    if load_summarize_chain and llm:
        chain_type = "stuff" if est_tokens < 4000 else "map_reduce"
        try:
            summary = load_summarize_chain(llm, chain_type=chain_type).run(docs)
        except Exception as err:  # pragma: no cover
            logger.warning("Summarisation chain failed: %s", err)
            summary = "\n".join(d.page_content for d in docs)
    else:
        summary = "\n".join(d.page_content for d in docs)

    # truncate if over max_tokens
    if _estimate_tokens(summary) > max_tokens:
        summary = summary[: max_tokens * 4]
    return summary
