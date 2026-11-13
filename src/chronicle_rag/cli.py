"""Command-line interface for reproducible, version-aware retrieval experiments."""
import argparse
import json
from pathlib import Path
from .benchmark import evaluate, load_questions
from .comparison import compare
from .corpus_io import load_jsonl
from .experiments import ExperimentRegistry
from .provenance import dataset_manifest
from .schema import Question
from .service import RagService
from .store import SQLiteCorpus


def parser():
    root = argparse.ArgumentParser(prog="chronicle-rag")
    root.add_argument("--db", default="chronicle.sqlite3", help="SQLite corpus path")
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("status")
    ingest = commands.add_parser("ingest")
    ingest.add_argument("path", type=Path)
    query = commands.add_parser("query")
    query.add_argument("text")
    query.add_argument("--package", required=True)
    query.add_argument("--version", required=True)
    query.add_argument("--as-of", required=True)
    query.add_argument("-k", type=int, default=5)
    query.add_argument("--method", choices=("bm25", "hash", "hybrid"), default="hybrid")
    query.add_argument("--answer", action="store_true")
    benchmark = commands.add_parser("benchmark")
    benchmark.add_argument("questions", type=Path)
    benchmark.add_argument("--method", choices=("bm25", "hash", "hybrid"), default="hybrid")
    benchmark.add_argument("--save-runs", type=Path)
    baseline = commands.add_parser("compare")
    baseline.add_argument("questions", type=Path)
    baseline.add_argument("--first", choices=("bm25", "hash", "hybrid"), default="hybrid")
    baseline.add_argument("--second", choices=("bm25", "hash", "hybrid"), default="bm25")
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    service = RagService(SQLiteCorpus(args.db))
    if args.command == "ingest":
        result = service.import_documents(load_jsonl(args.path))
    elif args.command == "status":
        result = {"documents": service.store.count(),
                  "manifest": dataset_manifest(service.store.list_documents())}
    elif args.command == "query":
        q = Question(args.text, args.package, args.version, args.as_of, args.k)
        if args.answer:
            result = service.answer(q, args.method)
        else:
            hits = service.search(q, args.method)
            result = {"hits": [hit.to_dict() for hit in hits], "count": len(hits)}
    elif args.command == "benchmark":
        result = evaluate(service.store.list_documents(), load_questions(args.questions), args.method)
        if args.save_runs:
            run_id = ExperimentRegistry(args.save_runs).record("retrieval", result,
                                                                 {"method": args.method})
            result["saved_run_id"] = run_id
    elif args.command == "compare":
        result = compare(service.store.list_documents(), load_questions(args.questions),
                         a=args.first, b=args.second)
    else:
        raise RuntimeError("Unhandled command")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    main()
