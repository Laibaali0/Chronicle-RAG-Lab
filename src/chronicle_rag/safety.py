"""Answer validation and failure-safe fallback before returning results."""
from .schema import Answer, Hit
from .citations import validate_citations


def enforce_grounding(answer: Answer, hits: list[Hit]) -> Answer:
    if answer.abstained:
        return answer
    if not validate_citations(answer, hits):
        return Answer("Answer withheld: citations could not be verified.", abstained=True)
    return answer
