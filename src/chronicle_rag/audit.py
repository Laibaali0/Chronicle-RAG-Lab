"""Structured request audit events with no raw question or secret content."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from threading import Lock


class JsonlAudit:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def emit(self, kind: str, request_id: str, **fields):
        if not kind or not request_id:
            raise ValueError("kind and request_id required")
        event = {"at": datetime.now(timezone.utc).isoformat(),
                 "kind": kind, "request_hash": hashlib.sha256(request_id.encode()).hexdigest()[:16]}
        # Explicit allowlist prevents accidental free-form prompts in audit files.
        for key in ("status", "hit_count", "latency_ms", "abstained", "method"):
            if key in fields:
                event[key] = fields[key]
        with self._lock:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(event, sort_keys=True)+"\n")
        return event
