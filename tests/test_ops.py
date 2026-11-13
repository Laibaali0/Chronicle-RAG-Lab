from chronicle_rag.audit import JsonlAudit
from chronicle_rag.cache import LRUCache
from chronicle_rag.rate_limit import TokenBucket
from chronicle_rag.tracing import Timings
from chronicle_rag.experiments import ExperimentRegistry


def test_lru_eviction():
    cache = LRUCache(2)
    cache.put("a", 1); cache.put("b", 2)
    assert cache.get("a") == 1
    cache.put("c", 3)
    assert cache.get("b") is None


def test_token_bucket_refills():
    now = [0.0]
    bucket = TokenBucket(capacity=2, refill_per_second=1, clock=lambda: now[0])
    assert bucket.allow() and bucket.allow()
    assert not bucket.allow()
    now[0] = 1.0
    assert bucket.allow()


def test_audit_does_not_store_raw_prompt(tmp_path):
    log = JsonlAudit(tmp_path / "audit.jsonl")
    log.emit("answer", "private-key-string", status="ok", raw_question="secret prompt")
    text = (tmp_path / "audit.jsonl").read_text()
    assert "private-key-string" not in text
    assert "secret prompt" not in text


def test_timing_context_records_stage():
    timer = Timings()
    with timer.record("retrieve"):
        pass
    assert timer.measured["retrieve"] >= 0


def test_registry_round_trip(tmp_path):
    db = ExperimentRegistry(tmp_path / "runs.db")
    ident = db.record("experiment", {"mean": .5}, {"seed": 7})
    result = db.list_runs()
    assert result[0]["id"] == ident
    assert result[0]["metadata"] == {"seed": 7}
