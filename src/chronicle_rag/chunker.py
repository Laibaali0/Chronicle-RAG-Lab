"""Sentence-aware chunking with overlap and deterministic stable chunk IDs."""
import hashlib
import re
from .schema import Document


def split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", text) if part.strip()]


def chunks(doc: Document, max_chars: int = 600, overlap: int = 80) -> list[Document]:
    if max_chars < 50 or overlap < 0 or overlap >= max_chars:
        raise ValueError("Requires max_chars >= 50 and 0 <= overlap < max_chars")
    text = " ".join(split_sentences(doc.body))
    if not text:
        return []
    result = []
    start = 0
    while start < len(text):
        stop = min(start + max_chars, len(text))
        if stop < len(text):
            boundary = text.rfind(" ", start+max_chars//2, stop)
            if boundary > start:
                stop = boundary
        body = text[start:stop].strip()
        if body:
            digest = hashlib.blake2s(f"{doc.id}:{start}:{body}".encode(), digest_size=6).hexdigest()
            result.append(Document(f"{doc.id}:{digest}", doc.package, doc.version,
                                   doc.valid_from, doc.valid_to, doc.title,
                                   body, doc.url, doc.tags))
        if stop >= len(text):
            break
        start = max(start+1, stop-overlap)
    return result
