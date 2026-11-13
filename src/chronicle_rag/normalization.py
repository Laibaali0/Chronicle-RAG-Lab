"""Source text normalization and conservative HTML stripping without execution."""
import html
import re

_TAG = re.compile(r"<[^>]*>")
_WS = re.compile(r"\s+")


def plain_text(raw: str) -> str:
    if not isinstance(raw, str):
        raise TypeError("raw text must be a string")
    unescaped = html.unescape(_TAG.sub(" ", raw))
    return _WS.sub(" ", unescaped).strip()


def snippet(raw: str, length: int = 260) -> str:
    if length <= 0:
        raise ValueError("length must be positive")
    normalized = plain_text(raw)
    return normalized if len(normalized) <= length else normalized[:max(1, length-1)].rstrip() + "…"
