"""Retrieval and citation metrics (independent of scoring algorithm)."""
from math import log2


def reciprocal_rank(ranked: list[str], relevant: set[str]) -> float:
    return next((1 / index for index, doc_id in enumerate(ranked, 1) if doc_id in relevant), 0.0)


def precision_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    return sum(doc_id in relevant for doc_id in ranked[:k]) / k


def recall_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    return sum(doc_id in relevant for doc_id in ranked[:k]) / len(relevant) if relevant else 0.0


def ndcg_at_k(ranked: list[str], judgments: dict[str, int], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    if any(value < 0 for value in judgments.values()):
        raise ValueError("relevance cannot be negative")
    dcg = sum((2**judgments.get(doc_id, 0)-1)/log2(index+1)
              for index, doc_id in enumerate(ranked[:k], 1))
    sorted_grades = sorted(judgments.values(), reverse=True)[:k]
    ideal = sum((2**grade-1)/log2(index+1) for index, grade in enumerate(sorted_grades, 1))
    return dcg / ideal if ideal else 0.0


def citation_precision(citations: list[str], eligible: set[str]) -> float:
    return sum(c in eligible for c in citations)/len(citations) if citations else 0.0
