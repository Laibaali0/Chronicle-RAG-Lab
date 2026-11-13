"""Deterministic tokenization for coding-oriented retrieval baselines."""
from collections import Counter
import re

_TOKEN = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*|[0-9]+")


def tokens(text: str) -> list[str]:
    # CamelCase and underscores become separate terms while full symbols remain
    # searchable: ProductEditSession -> producteditsession, product, edit, session.
    normalized = text.replace(".", " ").replace("/", " ")
    terms = []
    for match in _TOKEN.findall(normalized):
        full = match.casefold()
        terms.append(full)
        segments = re.sub(r"([a-z])([A-Z])", r"\1 \2", match).replace("_", " ").split()
        parts = [part.casefold() for part in segments]
        if len(parts) > 1:
            terms.extend(parts)
    return terms


def frequencies(text: str) -> Counter:
    return Counter(tokens(text))
