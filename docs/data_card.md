# Synthetic documentation dataset card

**Provenance:** Hand-authored, fabricated versioned SDK documentation created solely for this repository. There is no affiliation with a real software platform, no customer data, and no third-party model weights.

**Format:** JSON Lines. Every row includes `id`, `package`, `version`, `valid_from`, `valid_to`, `title`, `body` and optional tags and URL.

**Packages:** The fictitious `cart-sdk`, `inventory-sdk`, and `billing-sdk`. API names intentionally change between 1.0 and 2.0 to exercise temporal/version filters.

**Labels:** Eight hand-authored benchmark questions with graded relevance judgments, stored in `examples/benchmark.json`.

**Intended uses:** Unit tests, demonstrations of date-scoped retrieval and citation validation, introductory retrieval evaluation and reproducibility tutorials.

**Not intended for:** Generalizable empirical claims about coding assistants, actual product documentation, quantitative statements about customer behavior, production information retrieval, model training, or a job application claiming real-world benchmark impact.

**Limitations:** Tiny size, simple language, a small number of packages, no annotator disagreement measures, narrow query coverage, and no negative/adversarial user query distribution.
