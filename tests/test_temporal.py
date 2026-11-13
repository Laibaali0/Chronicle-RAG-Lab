from datetime import date
import pytest
from chronicle_rag.schema import Document, Question
from chronicle_rag.temporal import valid_on, eligible, filter_documents, conflicting_versions


def doc():
    return Document("x", "cart-sdk", "1.0", "2024-01-01", "2025-01-01", "Name", "Body")


def test_validity_interval_includes_start_excludes_end():
    assert valid_on(doc(), "2024-01-01")
    assert valid_on(doc(), date(2024, 12, 31))
    assert not valid_on(doc(), "2025-01-01")


def test_wrong_version_and_package_are_rejected():
    assert eligible(doc(), Question("how", "cart-sdk", "1.0", "2024-06-01"))
    assert not eligible(doc(), Question("how", "cart-sdk", "2.0", "2024-06-01"))
    assert not eligible(doc(), Question("how", "billing-sdk", "1.0", "2024-06-01"))


def test_incompatible_date_range_raises():
    with pytest.raises(ValueError):
        Document("x", "pkg", "1", "2025-01-01", "2024-01-01", "Title", "Content")


def test_missing_version_returns_empty(documents):
    q = Question("create cart", "cart-sdk", "3.0", "2025-07-01")
    assert filter_documents(documents, q) == []


def test_concurrent_versions_identified(documents):
    assert conflicting_versions(documents, "cart-sdk", "2024-06-01") == {"1.0"}
    assert conflicting_versions(documents, "cart-sdk", "2025-07-01") == {"2.0"}


def test_date_validation_is_strict():
    with pytest.raises(ValueError):
        Question("q", "pkg", "v1", "tomorrow")


def test_version_2_feature_not_retroactive(documents):
    first = Question("receipt", "cart-sdk", "2.0", "2025-03-01")
    second = Question("receipt", "cart-sdk", "2.0", "2025-07-01")
    assert "cart-v2-refunds" not in {d.id for d in filter_documents(documents, first)}
    assert "cart-v2-refunds" in {d.id for d in filter_documents(documents, second)}


def test_open_ended_document_remains_valid_after_start():
    evergreen = Document(
        "ongoing", "cart-sdk", "2.0", "2025-01-01", None,
        "Current API", "This reference has no scheduled end date."
    )
    assert not valid_on(evergreen, "2024-12-31")
    assert valid_on(evergreen, "2025-01-01")
    assert valid_on(evergreen, "2027-01-01")


def test_filter_does_not_mutate_source_order():
    current = Document(
        "current", "cart-sdk", "2.0", "2025-01-01", None,
        "Current API", "Use the current API."
    )
    old = doc()
    originals = [old, current]
    filtered = filter_documents(
        originals, Question("cart", "cart-sdk", "2.0", "2025-04-01")
    )
    assert filtered == [current]
    assert originals == [old, current]
