"""BM25 lexical ranking; indexes are rebuilt per eligible version/date scope."""
from collections import Counter
from math import log
from .schema import Document
from .tokenize import tokens


class BM25:
    def __init__(self, documents: list[Document], k1: float = 1.5, b: float = 0.75):
        if not 0 <= b <= 1 or k1 <= 0:
            raise ValueError("BM25 needs k1 > 0 and b within [0,1]")
        self.documents = list(documents)
        self.k1, self.b = k1, b
        self.rows = [Counter(tokens(doc.title + " " + doc.body)) for doc in documents]
        self.lengths = [sum(row.values()) for row in self.rows]
        self.avg_length = sum(self.lengths) / len(documents) if documents else 1.0
        self.df = Counter(term for row in self.rows for term in row)

    def score(self, question: str) -> dict[str, float]:
        scores = {doc.id: 0.0 for doc in self.documents}
        total = len(self.documents)
        for term in set(tokens(question)):
            freq = self.df.get(term, 0)
            if not freq:
                continue
            idf = log(1 + (total - freq + 0.5) / (freq + 0.5))
            for doc, row, length in zip(self.documents, self.rows, self.lengths):
                count = row.get(term, 0)
                if count:
                    normalizer = count + self.k1 * (1-self.b + self.b*length / max(self.avg_length, 1))
                    scores[doc.id] += idf * count * (self.k1+1) / normalizer
        return scores
