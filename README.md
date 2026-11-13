# Chronicle RAG Lab

**Version-aware document retrieval, grounded-answer baselines, and reproducible ML evaluation.**

Chronicle RAG is a complete, CPU-runnable reference application for a common failure mode in AI coding assistants: retrieving documentation that is semantically relevant but out of date for the API version or date the developer is using.

> **Portfolio / research prototype.** The sample SDKs, API changes, documentation and relevance judgments are **synthetic** and intentionally fabricated for controlled evaluation. This is not deployed at Shopify or any other employer, not a production coding assistant, and not a publication or real-user benchmark. Developed with AI assistance; verify and understand the design before representing it in an application.

## What it does

- **Scopes evidence by time and version before ranking.** Documents declare an inclusive start date, exclusive end date, exact package and exact API version.
- **Ranks eligible documents** using BM25, stable feature-hashed vector similarity, or reciprocal-rank fusion. The hashed vectors are *not pretrained neural embeddings*.
- **Produces grounded, extractive responses** with source IDs; abstains when evidence is missing or citations cannot be verified.
- **Exposes a read-only FastAPI service** with input validation, optional API-key authentication and process-local rate limiting.
- **Persists corpora and experiment runs** transactionally in SQLite and records content hashes for reproducibility.
- **Evaluates retrieval** with Precision@K, Recall@K, MRR, nDCG and paired query bootstrap comparisons.
- **Checks reliability failure modes** including stale API evidence, invalid citations, prompt-injection indicators and missing data.
- **Provides an optional OpenAI-compatible client adapter**, tested with mocked network calls only. It is not used automatically by the baseline CLI or HTTP API.

## Architecture

```text
documentation -> JSONL validation -> SQLite corpus
                                   |
                         package/version/as-of filter
                                   |
                   +---------------+--------------+
                   |                              |
                BM25                      hashed lexical vectors
                   |                              |
                   +----------- RRF --------------+
                                   |
                        cited, scoped evidence
                                   |
                extractive answer / abstention
                                   |
                    evaluation + run registry
```

The code is a reference system with small datasets and deterministic experiments. See [architecture](docs/architecture.md) and [limitations](docs/evaluation.md).

## Getting started

Requirements: Python 3.10 or later. A GPU, external model, and API key are **not** needed for the baseline.

```bash

git clone https://github.com/Laibaali0/Chronicle-RAG-Lab.git
cd chronicle-rag-lab
python -m venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\activate
python -m pip install -e '.[dev]'
pytest -q
```

> The clone URL above will work once this package is published under the proposed repository name.

## Load synthetic documentation

```bash
chronicle-rag --db demo.db ingest examples/synthetic_docs.jsonl
chronicle-rag --db demo.db status
chronicle-rag --db demo.db query "how do I start a cart?" --package cart-sdk --version 2.0 --as-of 2025-07-01 --answer
chronicle-rag --db demo.db query "create a cart" --package cart-sdk --version 1.0 --as-of 2024-06-01 --method bm25
```

The first query can cite `cart-v2-start`; the second only searches `cart-sdk` 1.0 documents valid in June 2024. A query for version 3.0 should abstain because no eligible evidence is available.

## Reproduce the offline benchmark

```bash
chronicle-rag --db demo.db benchmark examples/benchmark.json --method bm25
chronicle-rag --db demo.db benchmark examples/benchmark.json --method hash
chronicle-rag --db demo.db benchmark examples/benchmark.json --method hybrid --save-runs runs.db
chronicle-rag --db demo.db compare examples/benchmark.json --first hybrid --second bm25
```

`examples/benchmark.json` contains eight **hand-authored synthetic** queries with relevance judgments. Scores only characterize that fixture. Do not report results as production lift or a public benchmark.

## Serve the HTTP API

```bash
export CHRONICLE_DB=demo.db
export CHRONICLE_API_KEY=change-me-to-a-long-random-secret
uvicorn chronicle_rag.api:app --host 127.0.0.1 --port 8000

Example request:

curl http://127.0.0.1:8000/v1/answer \
  -H 'Content-Type: application/json' \
  -H 'x-api-key: change-me-to-a-long-random-secret' \
  -d '{"question":"start a cart session","package":"cart-sdk","version":"2.0","as_of":"2025-07-01","k":3}'
```

Interactive API documentation appears at `/docs`. In-memory rate limiting is process-local, not distributed. Before exposing the API beyond localhost, add a reverse proxy, TLS, request limits, authentication for health information as needed, and persistent shared rate limiting. See [deployment notes](docs/deployment.md).

## Testing and checks

```bash
python -m pip install -e '.[dev]'
pytest -q
bash scripts/smoke.sh
```

CI tests supported Python versions on GitHub Actions. All samples are constructed without private customer data or external credentials.

## Project map

| Area | Main modules |
|---|---|
| Document schema and imports | `schema.py`, `corpus_io.py`, `store.py`, `provenance.py`, `chunker.py` |
| Retrieval | `temporal.py`, `bm25.py`, `hash_vectors.py`, `fusion.py`, `retrieval.py` |
| Grounded answers | `answering.py`, `citations.py`, `safety.py`, `generated_answer.py`, `prompt.py` |
| Evaluation | `metrics.py`, `benchmark.py`, `comparison.py`, `bootstrap.py`, `temporal_metrics.py`, `quality_gates.py` |
| Operations | `api.py`, `cache.py`, `rate_limit.py`, `audit.py`, `tracing.py`, `experiments.py` |
| Optional model adapter | `provider.py` (disabled in the default workflow) |

## Current limitations and roadmap

- The ranker uses BM25 and deterministic hashed lexical features, not fine-tuned semantic embeddings.
- Exact version matching does not support semantic version ranges; this deliberately avoids silently mixing incompatible API documentation.
- The extractive baseline does not establish semantic entailment. Citation existence **does not prove the claim is supported**.
- The corpus is small, hand-authored, synthetic, and unsuitable for generalization claims.
- Real deployments would require ACL-scoped retrieval, hardened content sanitization, concurrency review, and stronger monitoring.

See [roadmap](docs/roadmap.md), [evaluation methodology](docs/evaluation.md), and [threat model](docs/security.md).
