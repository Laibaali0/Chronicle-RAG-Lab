"""Content hashes and import provenance for transparent corpus tracking."""
import hashlib
import json
from .schema import Document


def content_digest(document: Document) -> str:
    canonical = json.dumps(document.to_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def dataset_manifest(documents: list[Document]) -> dict:
    docs = sorted(documents, key=lambda doc: doc.id)
    hashes = [f"{doc.id}:{content_digest(doc)}" for doc in docs]
    digest = hashlib.sha256("\n".join(hashes).encode()).hexdigest()
    return {"documents": len(docs), "sha256": digest,
            "document_digests": {doc.id: content_digest(doc) for doc in docs}}
