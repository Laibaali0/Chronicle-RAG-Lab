"""Strict JSONL document import/export and duplicate-ID detection."""
import json
from pathlib import Path
from .schema import Document


def load_jsonl(path: str | Path) -> list[Document]:
    docs = []
    ids = set()
    with Path(path).open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
                if not isinstance(raw, dict):
                    raise ValueError("expected JSON object")
                doc = Document.from_dict(raw)
            except (ValueError, TypeError, KeyError) as error:
                raise ValueError(f"Invalid document on line {line_number}: {error}") from error
            if doc.id in ids:
                raise ValueError(f"Duplicate document ID: {doc.id}")
            ids.add(doc.id)
            docs.append(doc)
    return docs


def write_jsonl(path: str | Path, documents: list[Document]):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as output:
        for doc in documents:
            output.write(json.dumps(doc.to_dict(), sort_keys=True) + "\n")
