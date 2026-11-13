from fastapi.testclient import TestClient
from chronicle_rag.api import create_app


def payload(version="2.0", as_of="2025-07-01"):
    return {"question": "start cart session", "package": "cart-sdk",
            "version": version, "as_of": as_of, "k": 3}


def test_health_and_search(tmp_path, documents):
    app = create_app(str(tmp_path / "api.db"), api_key="secret")
    app.state.rag.import_documents(documents)
    client = TestClient(app)
    assert client.get("/health").json()["stored_documents"] == len(documents)
    assert client.post("/v1/search", json=payload(), headers={"x-api-key":"secret"}).status_code == 200


def test_key_required_when_configured(tmp_path):
    app = create_app(str(tmp_path / "api.db"), api_key="secret")
    client = TestClient(app)
    assert client.post("/v1/search", json=payload()).status_code == 401


def test_invalid_dates_return_422(tmp_path):
    app = create_app(str(tmp_path / "api.db"), api_key="")
    client = TestClient(app)
    assert client.post("/v1/search", json=payload(as_of="yesterday")).status_code == 422


def test_invalid_method_rejected(tmp_path):
    app = create_app(str(tmp_path / "api.db"), api_key="")
    client = TestClient(app)
    assert client.post("/v1/search", json={**payload(), "method":"untrusted"}).status_code == 422


def test_abstention_over_http(tmp_path, documents):
    app = create_app(str(tmp_path / "api.db"), api_key="")
    app.state.rag.import_documents(documents)
    client = TestClient(app)
    result = client.post("/v1/answer", json=payload(version="9.0"))
    assert result.status_code == 200 and result.json()["abstained"]
