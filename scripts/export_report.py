"""Create a JSON report with synthetic baseline scores, never hard-coded lifts."""
import json
from pathlib import Path
from chronicle_rag.benchmark import evaluate, load_questions
from chronicle_rag.comparison import compare
from chronicle_rag.corpus_io import load_jsonl


def main():
    root = Path(__file__).resolve().parent.parent
    docs = load_jsonl(root / "examples/synthetic_docs.jsonl")
    questions = load_questions(root / "examples/benchmark.json")
    results = {
        "dataset": "hand-authored synthetic versioned SDK docs",
        "baseline_metrics": {method: evaluate(docs, questions, method)["mean"]
                             for method in ("bm25", "hash", "hybrid")},
        "comparison": compare(docs, questions),
    }
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
