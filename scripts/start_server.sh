#!/bin/sh
set -eu
if [ -z "${CHRONICLE_API_KEY:-}" ]; then
  echo "CHRONICLE_API_KEY must be set before exposing the service" >&2
  exit 1
fi
exec uvicorn chronicle_rag.api:app --host 0.0.0.0 --port 8000
