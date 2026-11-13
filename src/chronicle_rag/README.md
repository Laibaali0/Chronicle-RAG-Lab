# Package guide

The package separates data parsing, temporal filtering, retrieval, answering, evaluation,
and serving. No network calls are made by the baseline retrieval and extractive-answer path.
The hash-vector retrieval arm uses deterministic feature hashing **not a trained embedding model**.
The API exposes *read-only* retrieval and answer endpoints; imports use CLI.
