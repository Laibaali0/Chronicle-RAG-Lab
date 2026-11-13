# HTTP API reference

The service is read-only. Use CLI ingestion before querying.

## `GET /health`

Returns `status` and the number of stored documents. This endpoint is unauthenticated; restrict network exposure appropriately.

## `POST /v1/search`

Example JSON:

```json
{"question":"start cart session", "package":"cart-sdk", "version":"2.0", "as_of":"2025-07-01", "k":3, "method":"hybrid"}
```

Returns a `hits` array of scored, eligible documents and a `count`.

## `POST /v1/answer`

Takes the same JSON and returns an extractive answer, cited source IDs, source metadata, an abstention boolean and stage timing information. The default generator **does not call an LLM**.

If the service is configured with `CHRONICLE_API_KEY`, send an `x-api-key` header. Invalid dates, unsupported ranking methods and incorrectly typed input fields result in HTTP 422. Requests may receive HTTP 429 when the process-local token budget is exhausted.
