# Architecture and data flow

1. **Source contract.** `Document` validates an ID, package name, exact version, `valid_from` inclusive and optional `valid_to` exclusive. All dates are ISO-8601 calendar dates. `corpus_io` refuses duplicate IDs and malformed JSONL rows.
2. **Storage.** `SQLiteCorpus` ingests a validated batch with transactional upsert. Each row stores a JSON payload, sha256 digest, and ingestion timestamp. A dataset hash enables deterministic comparisons across reruns.
3. **Scope first.** A `Question` always supplies a package, version and as-of date. `Retriever` excludes evidence outside all three dimensions *before* calculating ranking scores.
4. **Retrieval.** Scoped documents are scored by BM25 and a deterministic stable-feature-hash cosine baseline. Reciprocal rank fusion can combine rankings without miscalibrating score scales.
5. **Answer construction.** The default response copies a relevant sentence from an eligible document and attaches its exact document ID. When evidence is unavailable, it abstains. Citations are checked against retrieval outputs before returning.
6. **Evaluation.** A JSON fixture stores query metadata and graded relevance judgments. Query-level metrics are reported per baseline, with query-paired bootstrap deltas for exploratory comparisons.
7. **Operations.** FastAPI read-only endpoints use optional key authentication, rate-limit requests in-process, and validate typed bodies. Request audit logging is available but disabled by default.

## API boundary

The HTTP service **does not expose document ingestion, deletion, arbitrary file access or tool execution**. Operational imports must be run locally through the CLI. This keeps the public-facing example read-only by design.

## Concurrency

SQLite's serializable write path is provided by transactions. The in-memory LRU and token bucket use process-local locks; neither offers a guarantee across replicated workers. A real deployment would need shared cache invalidation, identity-aware authorization, globally enforced quotas and ingestion job orchestration.
