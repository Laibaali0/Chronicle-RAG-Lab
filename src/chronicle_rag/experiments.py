"""Persistent, append-only benchmark run registry."""
import json
from datetime import datetime, timezone
import sqlite3
from pathlib import Path
from uuid import uuid4


class ExperimentRegistry:
    def __init__(self, path: str | Path):
        self.path = str(path)
        with sqlite3.connect(self.path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY, created_at TEXT NOT NULL, name TEXT NOT NULL,
                metadata TEXT NOT NULL, report TEXT NOT NULL)""")

    def record(self, name: str, report: dict, metadata: dict | None = None) -> str:
        if not name.strip():
            raise ValueError("experiment name required")
        ident = uuid4().hex
        now = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT INTO runs VALUES (?,?,?,?,?)", (
                ident, now, name, json.dumps(metadata or {}, sort_keys=True),
                json.dumps(report, sort_keys=True, allow_nan=False)))
        return ident

    def list_runs(self, name: str | None = None, limit: int = 100) -> list[dict]:
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be 1..1000")
        with sqlite3.connect(self.path) as db:
            if name:
                rows = db.execute("SELECT id,created_at,name,metadata,report FROM runs WHERE name=? ORDER BY created_at DESC LIMIT ?", (name, limit)).fetchall()
            else:
                rows = db.execute("SELECT id,created_at,name,metadata,report FROM runs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [{"id": r[0], "created_at": r[1], "name": r[2], "metadata": json.loads(r[3]), "report": json.loads(r[4])} for r in rows]
