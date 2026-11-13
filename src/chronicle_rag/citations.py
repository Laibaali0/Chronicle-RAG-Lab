"""Citation assembly and validation for answer context grounding."""
from .schema import Answer, Hit
from .normalization import snippet


def format_context(hits: list[Hit], max_chars: int = 3000) -> str:
    if max_chars < 100:
        raise ValueError("max_chars must be >= 100")
    parts = []
    remaining = max_chars
    for hit in hits:
        doc = hit.document
        header = f"[source:{doc.id}] {doc.title} ({doc.package} {doc.version}, {doc.valid_from}..{doc.valid_to or 'current'})\n"
        if len(header) + 20 > remaining:
            break
        body = snippet(doc.body, remaining - len(header))
        chunk = header + body
        parts.append(chunk)
        remaining -= len(chunk) + 2
        if remaining < 80:
            break
    return "\n\n".join(parts)


def validate_citations(answer: Answer, hits: list[Hit]) -> bool:
    valid = {hit.document.id for hit in hits}
    return set(answer.cited_ids).issubset(valid) and (bool(answer.cited_ids) or answer.abstained)


def source_rows(hits: list[Hit]) -> list[dict]:
    return [{"id": hit.document.id, "title": hit.document.title,
             "url": hit.document.url, "version": hit.document.version,
             "valid_from": hit.document.valid_from, "valid_to": hit.document.valid_to}
            for hit in hits]
