from pathlib import Path
import pytest
from chronicle_rag.corpus_io import load_jsonl
from chronicle_rag.store import SQLiteCorpus
from chronicle_rag.service import RagService


@pytest.fixture
def documents():
    return load_jsonl(Path(__file__).parent.parent / "examples" / "synthetic_docs.jsonl")


@pytest.fixture
def service(tmp_path, documents):
    result = RagService(SQLiteCorpus(tmp_path / "docs.db"))
    result.import_documents(documents)
    return result
