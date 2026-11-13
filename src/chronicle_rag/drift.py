"""Smoothed Jensen-Shannon divergence of token frequencies between corpora.

A lexical drift signal, not a statistical demonstration of model drift.
"""
from collections import Counter
from math import log2
from .tokenize import tokens


def _distribution(rows: list[str], vocabulary: list[str], alpha: float):
    counts = Counter(term for row in rows for term in tokens(row))
    denominator = sum(counts.values()) + alpha * len(vocabulary)
    return {term: (counts.get(term, 0) + alpha) / denominator for term in vocabulary}


def lexical_drift(before: list[str], after: list[str], smoothing=0.1) -> float:
    if not before or not after or smoothing <= 0:
        raise ValueError("both corpora must be populated; smoothing must be positive")
    vocab = sorted(set(term for row in before + after for term in tokens(row)))
    if not vocab:
        return 0.0
    p, q = _distribution(before, vocab, smoothing), _distribution(after, vocab, smoothing)
    m = {term: (p[term] + q[term]) / 2 for term in vocab}
    kl_p = sum(p[term] * log2(p[term] / m[term]) for term in vocab)
    kl_q = sum(q[term] * log2(q[term] / m[term]) for term in vocab)
    return (kl_p + kl_q) / 2
