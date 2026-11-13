import pytest
from chronicle_rag.bm25 import BM25
from chronicle_rag.fusion import reciprocal_rank_fusion
from chronicle_rag.hash_vectors import vector, cosine_scores
from chronicle_rag.retrieval import Retriever
from chronicle_rag.schema import Question, Document
from chronicle_rag.tokenize import tokens



def test_camel_case_tokenization():
    terms = tokens("CartSession.create_cart")
    assert "cartsession" in terms
    assert "cart" in terms
    assert "session" in terms
    assert "create" in terms


def test_bm25_matches_unique_term(documents):
    valid = [doc for doc in documents if doc.package == "cart-sdk" and doc.version == "2.0"]
    scores = BM25(valid).score("currency total_amount")
    assert max(scores, key=scores.get) == "cart-v2-total"


def test_hash_vectors_are_deterministic():
    import numpy as np
    np.testing.assert_array_equal(vector("hello world"), vector("hello world"))
    assert cosine_scores("hello", ["hello world", "nonsense"])[0] > 0


def test_rank_fusion_tie_breaks_deterministically():
    scores = reciprocal_rank_fusion([["a", "b"], ["b", "a"]])
    assert scores["a"] == scores["b"]


def test_no_cross_version_leakage(documents):
    q = Question("create cart", "cart-sdk", "2.0", "2025-07-01")
    hits = Retriever(documents).search(q)
    assert hits and all(hit.document.version == "2.0" for hit in hits)
    assert "cart-v1-create" not in [hit.document.id for hit in hits]


@pytest.mark.parametrize("method", ["hybrid", "bm25", "hash"])
def test_each_retriever_returns_bounded_hits(documents, method):
    q = Question("stock", "inventory-sdk", "2.0", "2025-07-01", k=1)
    hits = Retriever(documents).search(q, method)
    assert len(hits) == 1
    assert hits[0].document.package == "inventory-sdk"


def test_unknown_method_rejected(documents):
    with pytest.raises(ValueError):
        Retriever(documents).search(Question("q", "cart-sdk", "2.0", "2025-07-01"), "magic")


def test_duplicate_doc_ids_rejected():
    doc = Document("same", "a", "1", "2025-01-01", None, "Title", "Text")
    with pytest.raises(ValueError):
        Retriever([doc, doc])


def test_invalid_feature_dimensions():
    with pytest.raises(ValueError):
        vector("hello", dimensions=4)
