"""Validated domain types shared by ingestion, retrieval, and evaluation."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import Any


def as_date(raw: str) -> date:
    if not isinstance(raw, str):
        raise ValueError("date must be an ISO date string")
    try:
        return date.fromisoformat(raw)
    except ValueError as error:
        raise ValueError(f"invalid ISO date: {raw}") from error


@dataclass(frozen=True)
class Document:
    id: str
    package: str
    version: str
    valid_from: str
    valid_to: str | None
    title: str
    body: str
    url: str = ""
    tags: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.id.strip() or not self.package.strip() or not self.version.strip():
            raise ValueError("document id, package, and version cannot be empty")
        if not self.title.strip() or not self.body.strip():
            raise ValueError("title and body cannot be empty")
        start = as_date(self.valid_from)
        if self.valid_to and as_date(self.valid_to) <= start:
            raise ValueError("valid_to must be after valid_from (exclusive interval)")
        if self.url and not self.url.startswith(("https://", "http://")):
            raise ValueError("source URL must use HTTP(S)")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Document":
        fields = {key: data[key] for key in ("id", "package", "version", "valid_from", "valid_to", "title", "body") if key in data}
        fields["url"] = data.get("url", "")
        fields["tags"] = tuple(data.get("tags", ()))
        return cls(**fields)

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "package": self.package, "version": self.version,
                "valid_from": self.valid_from, "valid_to": self.valid_to,
                "title": self.title, "body": self.body, "url": self.url, "tags": list(self.tags)}


@dataclass(frozen=True)
class Question:
    text: str
    package: str
    version: str
    as_of: str
    k: int = 5

    def __post_init__(self):
        if not self.text.strip() or not self.package.strip() or not self.version.strip():
            raise ValueError("question, package, and version required")
        as_date(self.as_of)
        if not 1 <= self.k <= 50:
            raise ValueError("k must be 1..50")


@dataclass(frozen=True)
class Hit:
    document: Document
    score: float
    source: str = "hybrid"

    def to_dict(self) -> dict[str, Any]:
        return {"document": self.document.to_dict(), "score": round(self.score, 8), "source": self.source}


@dataclass(frozen=True)
class Answer:
    text: str
    cited_ids: tuple[str, ...] = field(default_factory=tuple)
    abstained: bool = False

    def to_dict(self):
        return {"answer": self.text, "citations": list(self.cited_ids), "abstained": self.abstained}
