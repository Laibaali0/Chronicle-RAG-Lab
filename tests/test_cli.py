from pathlib import Path
from chronicle_rag.cli import main

HERE = Path(__file__).parent.parent


def test_cli_full_workflow(tmp_path, capsys):
    args = ["--db", str(tmp_path / "docs.db")]
    imported = main(args + ["ingest", str(HERE / "examples" / "synthetic_docs.jsonl")])
    assert imported["imported"] >= 10
    result = main(args + ["query", "create cart session", "--package", "cart-sdk", "--version", "2.0", "--as-of", "2025-07-01", "--answer"])
    assert not result["abstained"]
    benchmark = main(args + ["benchmark", str(HERE / "examples" / "benchmark.json")])
    assert benchmark["queries"] == 8
    comparison = main(args + ["compare", str(HERE / "examples" / "benchmark.json")])
    assert comparison["first_method"] == "hybrid"
