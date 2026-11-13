"""Reproducible offline retrieval evaluation over a labeled JSON benchmark."""
import json
from pathlib import Path
from statistics import mean
from .metrics import reciprocal_rank, recall_at_k, precision_at_k, ndcg_at_k
from .retrieval import Retriever
from .schema import Document, Question
from .provenance import dataset_manifest


def load_questions(path: str | Path) -> list[tuple[Question, dict[str, int]]]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("benchmark must be an array")
    result = []
    for item in raw:
        query = Question(**item["question"])
        judgments = item["judgments"]
        if not isinstance(judgments, dict) or not judgments:
            raise ValueError("each benchmark query requires judgments")
        if any(not isinstance(v, int) or v < 0 for v in judgments.values()):
            raise ValueError("judgments must be non-negative integers")
        result.append((query, judgments))
    return result


def evaluate(documents: list[Document], rows: list[tuple[Question, dict[str, int]]], method="hybrid") -> dict:
    if not rows:
        raise ValueError("benchmark cannot be empty")
    engine = Retriever(documents)
    observations = []
    for q, judgments in rows:
        ids = [hit.document.id for hit in engine.search(q, method)]
        relevant = {doc_id for doc_id, grade in judgments.items() if grade > 0}
        observations.append({
            "question": q.text, "package": q.package, "version": q.version,
            "as_of": q.as_of, "ranking": ids,
            "precision": precision_at_k(ids, relevant, q.k),
            "recall": recall_at_k(ids, relevant, q.k),
            "mrr": reciprocal_rank(ids, relevant),
            "ndcg": ndcg_at_k(ids, judgments, q.k),
        })
    summary = {metric: float(mean(row[metric] for row in observations))
               for metric in ("precision", "recall", "mrr", "ndcg")}
    return {"method": method, "queries": len(rows), "corpus": dataset_manifest(documents),
            "mean": summary, "per_query": observations,
            "warning": "Toy synthetic benchmark; not real production performance"}
