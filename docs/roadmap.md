# Engineering roadmap

## Near-term improvements

- [ ] Add public, licensed versioned documentation with source revision history.
- [ ] Define and evaluate an **unscoped baseline** to isolate the benefit of temporal filtering.
- [ ] Add an actual sentence-transformers embedding adapter with a documented model identifier and exact version.
- [ ] Build a genuine cross-encoder reranking experiment and compare with BM25 under matched query sets.
- [ ] Add a schema to represent explicit SDK semantic-version compatibility ranges.
- [ ] Add an answer-support verification benchmark using independent human labels.
- [ ] Add group-aware query bootstrap and report confidence intervals on real evaluation sets.
- [ ] Add a secure multi-tenant authorization boundary before considering deployment.

## Research opportunities

Evaluate temporal stale-source failures under controlled API deprecations, ambiguous versions and migration guides. Study interactions between retrieval relevance, temporal correctness, citation support and abstention policies. Track negative results and costs alongside any improvements.
