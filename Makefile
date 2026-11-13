.PHONY: install test smoke lint demo
install:
	python -m pip install -e '.[dev]'
test:
	python -m pytest -q
smoke:
	bash scripts/smoke.sh
lint:
	python -m compileall -q src tests
demo:
	python -m chronicle_rag.cli --db demo.db ingest examples/synthetic_docs.jsonl
	python -m chronicle_rag.cli --db demo.db benchmark examples/benchmark.json
