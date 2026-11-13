# Developer notes

Install: `python -m pip install -e '.[dev]'`. Run `pytest -q` after changing retrieval or temporal validity logic. Tests are isolated by temporary SQLite paths and do not require external APIs.

The default API imports a local SQLite store at import time. Avoid running the module under a directory containing sensitive files or credentials. Use a temporary database in tests via `create_app(db_path=...)`.

When extending retrieval, preserve the **filter before rank** invariant. The baseline branch ordering and reference corpus must remain deterministic under a fixed input set.

When adding a model provider, do not store API keys or raw prompts in logs. Make generated responses pass citation checks and explicitly label the limitations of source-ID verification.
