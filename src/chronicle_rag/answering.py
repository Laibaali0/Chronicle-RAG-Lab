"""Conservative deterministic extractive baseline (not a generative model)."""
import re
from .schema import Answer, Hit, Question
from .tokenize import tokens


def answer_extractively(question: Question, hits: list[Hit], min_overlap: float = 0.15) -> Answer:
    if not 0 <= min_overlap <= 1:
        raise ValueError("min_overlap must be between 0 and 1")
    query = set(tokens(question.text))
    if not hits or not query:
        return Answer("Insufficient eligible evidence for this version and date.", abstained=True)
    candidates = []
    for hit in hits:
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", hit.document.body):
            sentence = sentence.strip()
            if not sentence:
                continue
            terms = set(tokens(sentence))
            overlap = len(query & terms) / len(query)
            candidates.append((overlap, hit.score, hit.document.id, sentence))
    if not candidates:
        return Answer("No extractable evidence was found.", abstained=True)
    overlap, _, source, best = max(candidates, key=lambda row: (row[0], row[1], row[2]))
    if overlap < min_overlap:
        return Answer("Unable to answer from the available evidence.", abstained=True)
    return Answer(best, cited_ids=(source,))
