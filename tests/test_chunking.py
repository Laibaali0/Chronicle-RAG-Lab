import pytest
from chronicle_rag.chunker import chunks
from chronicle_rag.normalization import plain_text, snippet
from chronicle_rag.schema import Document


def test_chunks_keep_provenance():
    doc = Document("x", "pkg", "1", "2024-01-01", None, "Title", "First sentence. " * 50)
    parts = chunks(doc, max_chars=100, overlap=20)
    assert len(parts) > 1
    assert all(p.package == "pkg" and p.id.startswith("x:") for p in parts)


def test_short_doc_is_single_chunk():
    doc = Document("x", "pkg", "1", "2024-01-01", None, "Title", "A short sentence.")
    assert len(chunks(doc)) == 1


def test_invalid_overlap_rejected():
    doc = Document("x", "pkg", "1", "2024-01-01", None, "Title", "Words")
    with pytest.raises(ValueError):
        chunks(doc, 80, 80)


def test_html_normalization():
    assert plain_text("<div>hello &amp; goodbye</div>") == "hello & goodbye"
    assert len(snippet("long " * 200, length=30)) <= 30
