import json
import pytest
from chronicle_rag.provider import ChatCompletionProvider, ProviderError


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()

    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self, _limit): return self.payload


def test_adapter_can_parse_mocked_response():
    client = ChatCompletionProvider("https://example.invalid/v1/chat/completions", "model", "token")
    def transport(request, timeout):
        assert request.get_method() == "POST"
        assert timeout == 20
        return FakeResponse({"choices": [{"message": {"content": "Answer [source:doc1]"}}]})
    text = client.complete([{"role": "user", "content": "question"}], transport=transport)
    assert text.endswith("[source:doc1]")


def test_provider_never_sends_http_secret_remote():
    with pytest.raises(ValueError):
        ChatCompletionProvider("http://example.com/api", "model", "secret")


def test_invalid_provider_response_is_rejected():
    client = ChatCompletionProvider("https://example.invalid/v1", "model", "token")
    with pytest.raises(ProviderError):
        client.complete([{"role": "user", "content": "q"}],
                        transport=lambda r, timeout: FakeResponse({"choices": []}))
