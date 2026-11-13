"""Optional OpenAI-compatible completion adapter.

This adapter is deliberately inactive in the baseline CLI/API. Calling it
requires an explicit endpoint, model and API key. No secrets are logged.
"""
import json
from urllib.request import Request, urlopen
from urllib.parse import urlparse


class ProviderError(RuntimeError):
    pass


class ChatCompletionProvider:
    def __init__(self, endpoint: str, model: str, api_key: str, timeout: float = 20):
        parsed = urlparse(endpoint)
        if parsed.scheme != "https" and not (parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1"}):
            raise ValueError("Provider endpoint must use HTTPS, except localhost")
        if not model or not api_key or timeout <= 0:
            raise ValueError("model, API key and positive timeout are required")
        self.endpoint, self.model, self._key, self.timeout = endpoint, model, api_key, timeout

    def complete(self, messages: list[dict], transport=urlopen) -> str:
        if not messages or any(item.get("role") not in {"system", "user", "assistant"} for item in messages):
            raise ValueError("messages must use standard chat roles")
        body = json.dumps({"model": self.model, "messages": messages, "temperature": 0}).encode()
        request = Request(self.endpoint, data=body, method="POST", headers={
            "Authorization": f"Bearer {self._key}", "Content-Type": "application/json"})
        try:
            with transport(request, timeout=self.timeout) as response:
                # Guard against accidentally processing huge responses.
                payload = json.loads(response.read(2_000_001))
                content = payload["choices"][0]["message"]["content"]
                if not isinstance(content, str):
                    raise ProviderError("Provider returned non-text content")
                return content
        except (KeyError, IndexError, ValueError, TypeError) as error:
            raise ProviderError("Provider returned an invalid response") from error
        except OSError as error:
            raise ProviderError("Provider request failed") from error
