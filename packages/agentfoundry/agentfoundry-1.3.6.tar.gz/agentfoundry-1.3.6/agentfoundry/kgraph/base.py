
# agentfoundry/kgraph/base.py

from abc import ABC, abstractmethod
from typing import Dict, List

class KGraphBase(ABC):
    """Abstract knowledge-graph interface shielding clients from providers."""

    @abstractmethod
    def upsert_fact(self, subject: str, predicate: str, obj: str,
                    metadata: Dict) -> str:
        pass

    @abstractmethod
    def search(self, query: str, *, user_id: str, org_id: str,
               k: int = 5) -> List[Dict]:
        pass

    @abstractmethod
    def get_neighbours(self, entity: str, depth: int = 2) -> List[Dict]:
        pass

    @abstractmethod
    def purge_expired(self, days: int = 90) -> None:
        pass

