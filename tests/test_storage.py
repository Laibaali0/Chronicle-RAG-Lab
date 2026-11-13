import pytest
from chronicle_rag.corpus_io import load_jsonl, write_jsonl
from chronicle_rag.store import SQLiteCorpus
from chronicle_rag.provenance import dataset_manifest, content_digest
from chronicle_rag.schema import Document


def test_sqlite_roundtrip(service, documents):
    assert service.store.count() == len(documents)
    assert service.store.get("cart-v2-start").version == "2.0"
    assert service.store.get("missing") is None


def test_upsert_updates_existing(tmp_path, documents):
    store = SQLiteCorpus(tmp_path / "x.db")
    store.upsert(documents)
    store.upsert(documents[:1])
    assert store.count() == len(documents)


def test_delete_record(tmp_path, documents):
    store = SQLiteCorpus(tmp_path / "x.db")
    store.upsert(documents[:1])
    assert store.delete(documents[0].id)
    assert not store.delete(documents[0].id)


def test_duplicate_import_fails_atomically(tmp_path, documents):
    store = SQLiteCorpus(tmp_path / "x.db")
    with pytest.raises(ValueError):
        store.upsert([documents[0], documents[0]])
    assert store.count() == 0


def test_jsonl_roundtrip(tmp_path, documents):
    path = tmp_path / "docs.jsonl"
    write_jsonl(path, documents)
    assert load_jsonl(path) == documents


def test_bad_jsonl_reports_line(tmp_path):
    path = tmp_path / "invalid.jsonl"
    path.write_text('{"wrong": true}\n')
    with pytest.raises(ValueError, match="line 1"):
        load_jsonl(path)


def test_manifest_independent_of_order(documents):
    assert dataset_manifest(documents)["sha256"] == dataset_manifest(list(reversed(documents)))["sha256"]


def test_content_digest_changes_when_body_changes():
    a = Document("a", "pkg", "1", "2024-01-01", None, "Title", "A")
    b = Document("a", "pkg", "1", "2024-01-01", None, "Title", "B")
    assert content_digest(a) != content_digest(b)
