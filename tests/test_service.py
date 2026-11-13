from chronicle_rag.schema import Question


def test_service_invalidate_search_cache(service, documents):
    question = Question("cart session", "cart-sdk", "2.0", "2025-07-01", 2)
    assert len(service.search(question)) == 2
    service.import_documents(documents)
    assert len(service.search(question)) == 2


def test_service_returns_source_metadata(service):
    response = service.answer(Question("cancel session", "cart-sdk", "2.0", "2025-07-01"))
    assert "sources" in response
    assert response["generator"] == "deterministic_extractive_baseline"
