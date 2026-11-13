"""Heuristic indicators for malicious instructions embedded in retrieved text.

This is an instrumentation aid, NOT a comprehensive prompt injection defense.
"""
import re

_PATTERNS = {
    "role_spoof": re.compile(r"(?:^|\n)\s*(?:system|developer)\s*:", re.I),
    "ignore_instructions": re.compile(r"ignore (?:all )?(?:previous|earlier|above) instructions", re.I),
    "exfiltration": re.compile(r"(?:send|upload|post).{0,90}(?:api[_ -]?key|token|secret|password)", re.I),
    "tool_request": re.compile(r"(?:execute|run)\s+(?:this\s+)?(?:shell|terminal|bash|command)", re.I),
}


def flags(content: str) -> list[str]:
    return sorted(name for name, pattern in _PATTERNS.items() if pattern.search(content))


def inspect_documents(documents) -> dict[str, list[str]]:
    return {doc.id: found for doc in documents if (found := flags(doc.body))}
