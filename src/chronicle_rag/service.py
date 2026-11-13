"""Application service: persistent corpus, cache, retrieval, grounding and audit."""
from uuid import uuid4
from .answering import answer_extractively
from .cache import LRUCache
from .citations import source_rows
from .injection import inspect_documents
from .retrieval import Retriever
from .safety import enforce_grounding
from .schema import Document, Question
from .store import SQLiteCorpus
from .tracing import Timings


class RagService:
    def __init__(self, store: SQLiteCorpus, audit=None, cache_size=128):
        self.store = store
        self.audit = audit
        self.cache = LRUCache(cache_size)

    def import_documents(self, documents: list[Document]):
        if len(documents) > 10000:
            raise ValueError("batch import limited to 10,000 documents")
        count = self.store.upsert(documents)
        self.cache.clear()
        return {"imported": count, "stored": self.store.count(),
                "suspicious_documents": inspect_documents(documents)}

    def search(self, question: Question, method="hybrid"):
        key = (question, method)
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        hits = Retriever(self.store.list_documents()).search(question, method)
        self.cache.put(key, hits)
        return hits

    def answer(self, question: Question, method="hybrid") -> dict:
        request_id = uuid4().hex
        timings = Timings()
        with timings.record("retrieval"):
            hits = self.search(question, method)
        with timings.record("grounded_answer"):
            result = enforce_grounding(answer_extractively(question, hits), hits)
        payload = {**result.to_dict(), "sources": source_rows(hits),
                   "timings_ms": timings.measured,
                   "generator": "deterministic_extractive_baseline"}
        if self.audit:
            self.audit.emit("answer", request_id, status="ok", method=method,
                            hit_count=len(hits), abstained=result.abstained,
                            latency_ms=sum(timings.measured.values()))
        return payload
