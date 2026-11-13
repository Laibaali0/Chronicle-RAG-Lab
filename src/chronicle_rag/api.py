"""HTTP service with FastAPI, strongly validated requests, and read-only defaults.

A write API is intentionally not exposed: dataset imports are CLI-only. Configure
CHRONICLE_API_KEY for authenticated access before listening on public networks.
"""
import os
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from .rate_limit import TokenBucket
from .schema import Question
from .service import RagService
from .store import SQLiteCorpus


class QueryPayload(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    package: str = Field(min_length=1, max_length=100)
    version: str = Field(min_length=1, max_length=100)
    as_of: str
    k: int = Field(ge=1, le=50, default=5)
    method: str = Field(pattern="^(bm25|hash|hybrid)$", default="hybrid")


def create_app(db_path: str | None = None, api_key: str | None = None) -> FastAPI:
    path = db_path or os.getenv("CHRONICLE_DB", "chronicle.sqlite3")
    secret = api_key if api_key is not None else os.getenv("CHRONICLE_API_KEY", "")
    service = RagService(SQLiteCorpus(path))
    bucket = TokenBucket(capacity=60, refill_per_second=2)
    app = FastAPI(title="Chronicle RAG Lab", version="0.1.0")

    @app.middleware("http")
    async def enforce_budget(request: Request, call_next):
        if not bucket.allow():
            return JSONResponse({"detail": "Too many requests"}, status_code=429)
        return await call_next(request)

    def require_auth(x_api_key: str | None = Header(default=None)):
        if secret and x_api_key != secret:
            raise HTTPException(status_code=401, detail="Unauthorized")

    @app.get("/health")
    def health():
        return {"status": "ok", "stored_documents": service.store.count()}

    @app.post("/v1/search", dependencies=[Depends(require_auth)])
    def search(payload: QueryPayload):
        try:
            query = Question(payload.question, payload.package, payload.version, payload.as_of, payload.k)
            hits = service.search(query, payload.method)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return {"hits": [hit.to_dict() for hit in hits], "count": len(hits),
                "method": payload.method}

    @app.post("/v1/answer", dependencies=[Depends(require_auth)])
    def answer(payload: QueryPayload):
        try:
            query = Question(payload.question, payload.package, payload.version, payload.as_of, payload.k)
            return service.answer(query, payload.method)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    app.state.rag = service
    return app


app = create_app()
