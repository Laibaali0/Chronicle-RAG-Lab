"""Checks that retrieval respects scoped API versions and effective dates."""
from .schema import Document, Question, Hit
from .temporal import eligible


def violation_rate(pairs: list[tuple[Question, list[Hit]]]) -> float:
    if not pairs:
        raise ValueError("at least one query/result pair required")
    examined = [(q, hit.document) for q, hits in pairs for hit in hits]
    if not examined:
        return 0.0
    return sum(not eligible(doc, q) for q, doc in examined) / len(examined)


def freshness_recall_at_k(question: Question, hits: list[Hit],
                          expected: set[str]) -> float:
    if not expected:
        return 0.0
    seen = {hit.document.id for hit in hits[:question.k] if eligible(hit.document, question)}
    return len(expected & seen) / len(expected)
