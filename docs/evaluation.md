# Evaluation methodology

## Research question

Does filtering by the documented API version and effective time prevent retrieval of no-longer-applicable technical guidance, while preserving the ability to retrieve relevant in-scope documentation?

## Controlled benchmark

`examples/synthetic_docs.jsonl` contains fabricated documentation for `cart-sdk`, `inventory-sdk`, and `billing-sdk`. Both legacy and current versions exist. Effective dates deliberately overlap API naming conventions and include a later feature addition to the same major version. `examples/benchmark.json` defines eight human-readable questions with graded relevance judgments.

### Baselines

- `bm25`: traditional lexical BM25 scoring of **eligible** docs.
- `hash`: deterministic signed feature-hash vectors, not neural embeddings.
- `hybrid`: reciprocal rank fusion of both rankings.

Every method uses the **same query set**, the **same package/version/date constraints**, and the **same relevance labels**. Any comparison measures ranking behavior, not the value of temporal filtering alone. To isolate the impact of temporal filtering, future work should compare against a separate unrestricted baseline.

### Metrics

Precision@K, Recall@K, mean reciprocal rank, and nDCG@K. The report includes per-query rankings so errors can be inspected rather than hidden behind averages. A paired bootstrap resamples queries and reports confidence intervals for method differences, but **eight toy queries are far too few to justify a real-world significance claim**.

### Leakage and boundaries

- `valid_from` is inclusive and `valid_to` is exclusive.
- API version matching is deliberately exact.
- No answer should cite documents excluded by these filters.
- The derived citation validator proves only that a cited ID appeared in the retrieved set; it does not measure semantic support.
- API-specific `expected_answer_terms` are not defined here, avoiding misleading automatic hallucination scoring.

## Reproduction

Use the commands in the root README and report the exact package version and document manifest digest. A real study should use public licensed documentation, documented annotation policies, multiple independent annotators, source revision history, and query sampling that reflects actual developer needs.


## Time-boundary regression checklist

The temporal filter is intentionally conservative. When adding new SDK
examples or changing eligibility code, verify these cases:

1. A document is eligible on its `valid_from` date, but not on its
   `valid_to` date because that endpoint is exclusive.
2. A document with no `valid_to` remains eligible after its start date.
3. A query requesting an unknown package or version returns no evidence
   rather than silently falling back to another version.
4. Filtering leaves the original corpus order and documents unchanged.
5. A feature introduced partway through a version's lifetime must not
   appear in answers about earlier dates.

Run `python -m pytest tests/test_temporal.py -q` before changing retrieval
eligibility. These checks cover *date and version consistency*, not whether
the retrieved explanation is semantically correct.
