# Local deployment guide

## Recommended developer workflow

Install locally, import the synthetic docs into a local SQLite file, configure `CHRONICLE_API_KEY`, and serve only on loopback:

```bash
python -m pip install -e '.[dev]'
chronicle-rag --db demo.db ingest examples/synthetic_docs.jsonl
CHRONICLE_DB=demo.db CHRONICLE_API_KEY=local-dev-secret \
  uvicorn chronicle_rag.api:app --host 127.0.0.1 --port 8000
```

`GET /health` checks the service. `POST /v1/search` returns eligible document hits, and `POST /v1/answer` returns a conservative extractive answer plus sources.

## Containers

The provided Dockerfile is a **build example**, not hardened deployment advice. Pass a nonempty API key when running it and restrict exposure to a local development environment. The service will not import sample data automatically.

## Operational caveats

Back up or recreate the SQLite dataset. API-level writes are disabled. Cache invalidation runs when the application's `RagService.import_documents` is used, but cross-worker imports and replicas are not automatically synchronized. Production deployment requires workload identity, persistent logs, shared rate limits, source-level ACLs, observability, encryption, and a review of licensing and data retention.
