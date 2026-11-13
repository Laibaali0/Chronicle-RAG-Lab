import pytest
from chronicle_rag.drift import lexical_drift
from chronicle_rag.generated_answer import validate_generated_text, parse_citations
from chronicle_rag.quality_gates import evaluate_gates
from chronicle_rag.retrieval import Retriever
from chronicle_rag.schema import Question
from chronicle_rag.temporal_metrics import violation_rate, freshness_recall_at_k


def test_drift_zero_identical_texts():
    assert lexical_drift(["apple green"], ["apple green"]) == 0.0


def test_drift_positive_when_tokens_change():
    assert lexical_drift(["apple fruit"], ["GPU inference"]) > 0


def test_citation_validation_only_allows_retrieved_ids(documents):
    q = Question("start cart", "cart-sdk", "2.0", "2025-07-01")
    hits = Retriever(documents).search(q)
    good = validate_generated_text("start the session [source:cart-v2-start]", hits)
    bad = validate_generated_text("made up [source:not-present]", hits)
    assert not good.abstained
    assert bad.abstained


def test_no_source_marker_means_abstain():
    assert validate_generated_text("No citation", []).abstained


def test_duplicate_citations_collapsed():
    assert parse_citations("[source:x] [source:x] [source:y]") == ("x", "y")


def test_version_violation_metric(documents):
    q = Question("cart", "cart-sdk", "2.0", "2025-07-01")
    hits = Retriever(documents).search(q)
    assert violation_rate([(q, hits)]) == 0
    assert 0 <= freshness_recall_at_k(q, hits, {"cart-v2-start"}) <= 1


def test_quality_gate_detects_failure():
    report = {"mean": {"ndcg": .6, "mrr": .8}}
    assert evaluate_gates(report, {"ndcg": .5})["passed"]
    assert not evaluate_gates(report, {"ndcg": .9})["passed"]


def test_quality_gate_rejects_invalid_threshold():
    with pytest.raises(ValueError):
        evaluate_gates({"mean": {}}, {"ndcg": 1.1})
