import json
import pytest
from pathlib import Path
from chronicle_rag.benchmark import evaluate, load_questions
from chronicle_rag.bootstrap import paired_interval
from chronicle_rag.comparison import compare
from chronicle_rag.metrics import reciprocal_rank, recall_at_k, precision_at_k, ndcg_at_k

FIXTURE = Path(__file__).parent.parent / "examples" / "benchmark.json"


def test_known_ranking_metrics():
    assert reciprocal_rank(["x", "a"], {"a"}) == .5
    assert recall_at_k(["x", "a"], {"a", "b"}, 2) == .5
    assert precision_at_k(["x", "a"], {"a"}, 2) == .5
    assert ndcg_at_k(["a", "b"], {"a": 3, "b": 1}, 2) == pytest.approx(1)


def test_benchmark_contains_questions():
    rows = load_questions(FIXTURE)
    assert len(rows) == 8


def test_methods_generate_reports(documents):
    for method in ("bm25", "hash", "hybrid"):
        report = evaluate(documents, load_questions(FIXTURE), method)
        assert report["queries"] == 8
        assert all(0 <= value <= 1 for value in report["mean"].values())
        assert report["corpus"]["documents"] == len(documents)


def test_paired_bootstrap_deterministic():
    args = ([.1,.5,.9], [.2,.3,.7])
    assert paired_interval(*args, seed=4) == paired_interval(*args, seed=4)


def test_known_paired_delta():
    result = paired_interval([.5,.6], [.2,.3], resamples=20)
    assert result["mean_difference"] == pytest.approx(.3)
    assert result["ci_low"] == pytest.approx(.3)


def test_paired_rejects_different_sizes():
    with pytest.raises(ValueError):
        paired_interval([.5], [.1,.2])


def test_comparison_reports_methods(documents):
    result = compare(documents, load_questions(FIXTURE), "hybrid", "bm25")
    assert result["first_method"] == "hybrid"
    assert "paired_query_bootstrap" in result


def test_benchmark_rejects_empty(documents):
    with pytest.raises(ValueError):
        evaluate(documents, [])
