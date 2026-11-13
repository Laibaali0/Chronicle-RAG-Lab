"""Hybrid BM25/feature-hash retrieval with mandatory temporal scoping."""
from .bm25 import BM25
from .fusion import reciprocal_rank_fusion, stable_rank
from .hash_vectors import cosine_scores
from .schema import Document, Hit, Question
from .temporal import filter_documents


class Retriever:
    def __init__(self, documents: list[Document], dimensions: int = 256):
        if len({doc.id for doc in documents}) != len(documents):
            raise ValueError("Document IDs must be unique")
        self.documents = list(documents)
        self.dimensions = dimensions

    def search(self, question: Question, method: str = "hybrid") -> list[Hit]:
        documents = filter_documents(self.documents, question)
        if not documents:
            return []
        baseline = BM25(documents).score(question.text)
        lexical = stable_rank(baseline)
        dense_values = cosine_scores(question.text, [doc.title + " " + doc.body for doc in documents], self.dimensions)
        dense = dict(zip((doc.id for doc in documents), dense_values))
        dense_order = stable_rank(dense)
        if method == "bm25":
            scores = baseline
        elif method == "hash":
            scores = dense
        elif method == "hybrid":
            scores = reciprocal_rank_fusion([lexical, dense_order])
        else:
            raise ValueError("method must be bm25, hash, or hybrid")
        by_id = {doc.id: doc for doc in documents}
        ranked = stable_rank(scores)[:question.k]
        return [Hit(by_id[ident], scores[ident], source=method) for ident in ranked]
