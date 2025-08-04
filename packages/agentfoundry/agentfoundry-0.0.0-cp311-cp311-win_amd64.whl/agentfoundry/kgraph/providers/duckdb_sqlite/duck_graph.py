from pathlib import Path
import duckdb
import logging
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List

from adbc_driver_duckdb.dbapi import DATETIME

from agentfoundry.kgraph.base import KGraphBase
from agentfoundry.vectorstores import VectorStoreFactory

logger = logging.getLogger(__name__)


class DuckSqliteGraph(KGraphBase):
    """Knowledge‑graph implementation backed by DuckDB.

    *Facts* are stored relationally while the accompanying text triple is sent
    to the configured `vector_store` for similarity search.  A light JSON column
    keeps arbitrary metadata keyed by the caller (e.g. `user_id`, `org_id`, etc.).
    """

    def __init__(self, persist_path: str):
        path = Path(persist_path)
        path.mkdir(parents=True, exist_ok=True)
        self.db_path = str(path / "kgraph.duckdb")
        self.conn = duckdb.connect(self.db_path)
        self._ensure_schema()
        self.vector_store = VectorStoreFactory.get_store()
        logger.info("DuckSqliteGraph initialised at %s", self.db_path)

    # ---------------------------------------------------------------------
    # Schema & helpers
    # ---------------------------------------------------------------------
    def _ensure_schema(self) -> None:
        """Create tables / indexes if they do not already exist."""
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS facts (
                id TEXT PRIMARY KEY,
                subject TEXT,
                predicate TEXT,
                obj TEXT,
                user_id TEXT,
                org_id TEXT,
                created_at TIMESTAMP DEFAULT current_timestamp,
                metadata JSON
            )
            """
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_user ON facts(user_id, org_id)"
        )

    @staticmethod
    def _det_id(triple: str, user_id: str, org_id: str) -> str:
        """Deterministically derive the SHA‑256 id from the triple+actor."""
        h = hashlib.sha256()
        h.update(triple.encode())
        h.update(user_id.encode())
        h.update(org_id.encode())
        return h.hexdigest()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def upsert_fact(
        self,
        subject: str,
        predicate: str,
        obj: str,
        metadata: Dict,
    ) -> str:
        """Insert or update a fact and mirror it into the vector store."""
        user_id = metadata.get("user_id", "")
        org_id = metadata.get("org_id", "")
        triple = f"{subject}|{predicate}|{obj}"
        fact_id = self._det_id(triple, user_id, org_id)

        logger.debug("Upserting fact id=%s triple=%s", fact_id, triple)

        metadata_json = json.dumps(metadata, separators=(",", ":"))
        self.conn.execute(
            "INSERT OR REPLACE INTO facts VALUES (?, ?, ?, ?, ?, ?, current_timestamp, ?)",
            [fact_id, subject, predicate, obj, user_id, org_id, metadata_json],
        )

        # Vector store may throw if the id is already present – swallow and carry on
        try:
            self.vector_store.add_texts([triple], metadatas=[metadata], ids=[fact_id])
        except ValueError:
            pass

        return fact_id

    def search(
        self,
        query: str,
        *,
        user_id: str,
        org_id: str,
        k: int = 5,
    ) -> List[Dict]:
        logger.debug(
            "KG search query='%s' user=%s org=%s k=%d", query, user_id, org_id, k
        )
        docs = self.vector_store.similarity_search_with_score(
            query, k=k, filter={"user_id": user_id, "org_id": org_id}
        )

        results = []
        for doc, score in docs:
            subj, pred, obj = doc.page_content.split("|", 2)
            results.append(
                {"subject": subj, "predicate": pred, "object": obj, "score": score}
            )
        logger.info("KG search returned %d results", len(results))
        return results

    def get_neighbours(self, entity: str, depth: int = 2) -> List[Dict]:
        """Breadth‑first traversal up to *depth* hops from *entity*."""
        q = """
        WITH RECURSIVE hop(n, s, p, o) AS (
            SELECT 1, subject, predicate, obj FROM facts
            WHERE subject = ? OR obj = ?
            UNION ALL
            SELECT n + 1, f.subject, f.predicate, f.obj
            FROM facts f
            JOIN hop h ON f.subject = h.o
            WHERE n < ?
        )
        SELECT s, p, o FROM hop;
        """
        logger.debug("Fetching neighbours for %s depth=%d", entity, depth)
        rows = self.conn.execute(q, [entity, entity, depth]).fetchall()
        return [
            {"subject": s, "predicate": p, "object": o} for s, p, o in rows
        ]

    def purge_expired(self, days: int = 90) -> None:
        """Remove facts whose *created_at* is older than *days*."""
        logger.info("Purging facts older than %d days", days)
        cutoff = datetime.now(DATETIME.UTC) - timedelta(days=days)
        self.conn.execute("DELETE FROM facts WHERE created_at < ?", [cutoff])
