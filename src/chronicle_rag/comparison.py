"""Fair same-corpus baseline comparisons with paired uncertainty summaries."""
from .benchmark import evaluate
from .bootstrap import paired_interval


def compare(documents, labeled_queries, a="hybrid", b="bm25", metric="ndcg", seed=42):
    first = evaluate(documents, labeled_queries, method=a)
    second = evaluate(documents, labeled_queries, method=b)
    valid = ("precision", "recall", "mrr", "ndcg")
    if metric not in valid:
        raise ValueError(f"metric must be one of {valid}")
    interval = paired_interval([row[metric] for row in first["per_query"]],
                               [row[metric] for row in second["per_query"]], seed=seed)
    return {"first": first["mean"], "second": second["mean"],
            "first_method": a, "second_method": b, "metric": metric,
            "paired_query_bootstrap": interval,
            "caveat": "Results describe hand-authored synthetic data only"}
