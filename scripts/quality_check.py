"""Offline correctness gates for the synthetic benchmark (not real-world targets)."""
from pathlib import Path
from chronicle_rag.benchmark import evaluate, load_questions
from chronicle_rag.corpus_io import load_jsonl
from chronicle_rag.quality_gates import evaluate_gates
from chronicle_rag.temporal_metrics import violation_rate
from chronicle_rag.retrieval import Retriever


def main():
    root = Path(__file__).resolve().parent.parent
    docs = load_jsonl(root / "examples/synthetic_docs.jsonl")
    questions = load_questions(root / "examples/benchmark.json")
    engine = Retriever(docs)
    report = evaluate(docs, questions)
    pairs = [(question, engine.search(question)) for question, _ in questions]
    if violation_rate(pairs) != 0:
        raise SystemExit("Temporal scope leakage detected")
    # The threshold is intentionally weak and tied only to the toy corpus.
    result = evaluate_gates(report, {"recall": .25})
    if not result["passed"]:
        raise SystemExit(f"Baseline failed synthetic retrieval gate: {result}")
    print(f"Synthetic checks passed: {len(questions)} questions, no version/date leakage")


if __name__ == "__main__":
    main()
