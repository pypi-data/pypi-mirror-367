# agentfoundry/kgraph/factory.py

"""
Singleton factory class to manage kgraph provider instances.
"""

from __future__ import annotations
from typing import Dict, Any, Optional
from agentfoundry.utils.config import Config
from agentfoundry.kgraph.base import KGraphBase
from agentfoundry.kgraph.providers.duckdb_sqlite.duck_graph import DuckSqliteGraph
import threading
import logging

logger = logging.getLogger(__name__)


class KGraphFactory:
    """
    Singleton factory to return kgraph provider instances.
    """
    _instance: Optional[KGraphFactory] = None
    _lock = threading.Lock()

    def __init__(self):
        self._providers: Dict[str, KGraphBase] = {}
        self._config = Config()
        logger.debug("KGraphFactory initialized.")

    @classmethod
    def get_instance(cls) -> KGraphFactory:
        logger.debug("KGraphFactory.get_instance called")
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    logger.debug("Creating KGraphFactory singleton instance.")
                    cls._instance = cls()
        return cls._instance

    def get_kgraph(self, config_override: Dict[str, Any] = None) -> KGraphBase:
        """
        Returns a singleton KGraphBase provider instance per backend.

        Args:
            config_override: Optional configuration overrides for the provider.

        Returns:
            KGraphBase: The graph provider instance.
        """
        backend = (config_override or {}).get("KGRAPH.BACKEND") or self._config.get("KGRAPH.BACKEND", "duckdb_sqlite")
        logger.debug("get_kgraph called backend=%s overrides=%s", backend, config_override)
        key = backend

        if key not in self._providers:
            logger.info("Instantiating new KGraph provider for backend '%s'", backend)
            if backend == "duckdb_sqlite":
                persist_path = (config_override or {}).get("DATA_DIR") or self._config.get("DATA_DIR")
                self._providers[key] = DuckSqliteGraph(persist_path=persist_path)
            else:
                raise ValueError(f"Unknown kgraph backend: {backend}")
        else:
            logger.debug("Returning cached KGraph provider for backend '%s'", backend)
        return self._providers[key]
