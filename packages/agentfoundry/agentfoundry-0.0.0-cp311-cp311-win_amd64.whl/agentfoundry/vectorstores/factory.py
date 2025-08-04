"""VectorStoreFactory – central point to obtain vector-store instances."""

from __future__ import annotations

from agentfoundry.utils.config import Config
from agentfoundry.utils.logger import get_logger

# The registry was previously kept in providers.__init__; it now lives directly
# inside this Factory class for a single authoritative source of truth.

logger = get_logger(__name__)


class VectorStoreFactory:
    """Return a LangChain VectorStore instance from the configured provider."""

    # --------------------------------------------------------------
    # Provider registry helpers (moved from providers.__init__)
    # --------------------------------------------------------------

    _REGISTRY: dict[str, type] = {}

    @classmethod
    def register_provider(cls, name: str):
        """Decorator to register *provider class* under the given name."""

        def decorator(provider_cls):  # type: ignore[missing-return-type-doc]
            lower = name.lower()
            if lower in cls._REGISTRY:
                raise ValueError(f"Provider '{name}' already registered")
            cls._REGISTRY[lower] = provider_cls
            logger.debug("Registered vector-store provider '%s' -> %s", lower, provider_cls)
            return provider_cls

        return decorator

    @classmethod
    def get_provider_cls(cls, name: str):  # noqa: D401
        return cls._REGISTRY.get(name.lower())

    @classmethod
    def available_providers(cls):  # noqa: D401
        return list(cls._REGISTRY.keys())

    # --------------------------------------------------------------
    # Public factory methods
    # --------------------------------------------------------------

    @classmethod
    def get_store(cls, provider: str | None = None, *, org_id: str | None = None, **kwargs):
        """Instantiate provider and return the underlying LangChain VectorStore."""
        # Delegate to get_provider then return its store to avoid duplication
        return cls.get_provider(provider, org_id=org_id, **kwargs).get_store()

    @classmethod
    def get_provider(
        cls,
        provider: str | None = None,
        *,
        org_id: str | None = None,
        **kwargs,
    ):
        """Instantiate and return a VectorStore provider (abstract base type)."""
        provider_name = (provider or Config().get("VECTORSTORE.PROVIDER", "dummy")).lower()
        provider_cls = cls.get_provider_cls(provider_name)
        if provider_cls is None:
            raise ValueError(
                f"Unknown vector-store provider '{provider_name}'. Available providers: {cls.available_providers()}"
            )

        # Propagate *org_id* to the provider if it was explicitly supplied –
        # most back-ends (e.g. Chroma) rely on it to derive collection names
        # and to enforce security boundaries.
        if org_id is not None:
            kwargs.setdefault("org_id", org_id)

        # Determine a sensible default collection when talking to the global
        # store so that callers do not need to care.
        if "collection_name" not in kwargs and org_id is None:
            kwargs["collection_name"] = "global_memory"

        logger.debug(
            "VectorStoreFactory.get_provider called with provider=%s org_id=%s kwargs=%s",
            provider_name,
            org_id,
            kwargs,
        )
        logger.info(
            "VectorStoreFactory initialising provider '%s' (collection=%s)",
            provider_name,
            kwargs.get("collection_name"),
        )
        # Cache instantiated providers so that repeated calls for the same
        # (provider, org_id) tuple share the underlying store – this mirrors
        # the singleton-esque behaviour expected by higher-level memory
        # classes.

        cache_key = (provider_name, org_id)
        if not hasattr(cls, "_CACHE"):
            cls._CACHE = {}  # type: ignore[attr-defined]

        if cache_key not in cls._CACHE:
            cls._CACHE[cache_key] = provider_cls(**kwargs)

        return cls._CACHE[cache_key]

# ---------------------------------------------------------------------------
# Auto-import default provider modules so they self-register.
# ---------------------------------------------------------------------------

from importlib import import_module as _import_module  # noqa: E402

for _mod in (
    "agentfoundry.vectorstores.providers.faiss_provider",
    "agentfoundry.vectorstores.providers.chroma_provider",
    "agentfoundry.vectorstores.providers.dummy_provider",
):
    try:
        _import_module(_mod)
    except ModuleNotFoundError as _err:  # pragma: no cover
        logger.warning("Optional vector-store provider '%s' could not be imported: %s", _mod, _err)

# (duplicate public methods removed – now defined earlier inside the class)
