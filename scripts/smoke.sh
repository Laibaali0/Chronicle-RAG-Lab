#!/usr/bin/env bash
set -euo pipefail
DB="$(mktemp /tmp/chronicle-rag-XXXXXX.db)"
trap 'rm -f "$DB"' EXIT
python -m chronicle_rag.cli --db "$DB" ingest examples/synthetic_docs.jsonl
python -m chronicle_rag.cli --db "$DB" query 'how do I start a cart?' --package cart-sdk --version 2.0 --as-of 2025-07-01 --answer
python -m chronicle_rag.cli --db "$DB" benchmark examples/benchmark.json
python -m chronicle_rag.cli --db "$DB" compare examples/benchmark.json
