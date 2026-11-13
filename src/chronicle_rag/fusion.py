"""Rank-level fusion avoids assuming BM25/vector scores share a scale."""


def reciprocal_rank_fusion(rankings: list[list[str]], offset: int = 60) -> dict[str, float]:
    if offset < 0:
        raise ValueError("offset must be non-negative")
    scores: dict[str, float] = {}
    for ranking in rankings:
        if len(ranking) != len(set(ranking)):
            raise ValueError("duplicate identifiers within ranking")
        for index, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1 / (index + offset)
    return scores


def stable_rank(scores: dict[str, float]) -> list[str]:
    return sorted(scores, key=lambda ident: (-scores[ident], ident))
