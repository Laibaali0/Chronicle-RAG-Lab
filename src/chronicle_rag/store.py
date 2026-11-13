"""Transactional SQLite corpus store with deterministic import/export semantics."""
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from .schema import Document
from .provenance import content_digest


class SQLiteCorpus:
    def __init__(self, path: str | Path):
        self.path = str(path)
        with self.connection() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY, payload TEXT NOT NULL,
                digest TEXT NOT NULL, ingested_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
            db.execute("CREATE INDEX IF NOT EXISTS document_digest ON documents(digest)")

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=10)
        try:
            db.execute("PRAGMA busy_timeout = 10000")
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def upsert(self, documents: list[Document]) -> int:
        if len({doc.id for doc in documents}) != len(documents):
            raise ValueError("duplicate IDs in import batch")
        rows = [(doc.id, json.dumps(doc.to_dict(), sort_keys=True), content_digest(doc))
                for doc in documents]
        with self.connection() as db:
            db.executemany("""INSERT INTO documents(id,payload,digest) VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET payload=excluded.payload,
                digest=excluded.digest, ingested_at=CURRENT_TIMESTAMP""", rows)
        return len(rows)

    def list_documents(self) -> list[Document]:
        with self.connection() as db:
            rows = db.execute("SELECT payload FROM documents ORDER BY id").fetchall()
        return [Document.from_dict(json.loads(row[0])) for row in rows]

    def get(self, document_id: str) -> Document | None:
        with self.connection() as db:
            result = db.execute("SELECT payload FROM documents WHERE id=?", (document_id,)).fetchone()
        return Document.from_dict(json.loads(result[0])) if result else None

    def delete(self, document_id: str) -> bool:
        with self.connection() as db:
            result = db.execute("DELETE FROM documents WHERE id=?", (document_id,))
            return result.rowcount > 0

    def count(self) -> int:
        with self.connection() as db:
            return db.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
