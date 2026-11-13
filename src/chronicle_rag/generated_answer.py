"""Conservative validation of an optional LLM-generated answer's source markers.

A valid citation only proves that a claimed source was among the retrieved
hits; it does NOT prove the answer is logically supported by that source.
"""
import re
from .schema import Answer, Hit
from .safety import enforce_grounding

_SOURCE = re.compile(r"\[source:([A-Za-z0-9_.:-]+)\]")


def parse_citations(text: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(_SOURCE.findall(text)))


def validate_generated_text(text: str, hits: list[Hit], require_citation=True) -> Answer:
    if not isinstance(text, str) or not text.strip():
        return Answer("No answer returned.", abstained=True)
    references = parse_citations(text)
    if require_citation and not references:
        return Answer("Answer withheld: no verifiable source markers.", abstained=True)
    answer = Answer(text, references)
    return enforce_grounding(answer, hits)
