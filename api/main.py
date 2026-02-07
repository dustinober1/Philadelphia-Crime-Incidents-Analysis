"""FastAPI application entrypoint."""

from __future__ import annotations

import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import Response

from api.routers import forecasting, metadata, policy, questions, spatial, trends
from api.services.data_loader import cache_keys, contract_status, load_all_data

logger = logging.getLogger("crime_api")
if not logger.handlers:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


@asynccontextmanager
async def lifespan(_: FastAPI) -> Any:
    load_all_data()
    yield


app = FastAPI(
    title="Philadelphia Crime Explorer API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

allowed_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,https://philly-crime-explorer.web.app,https://philly-crime-explorer.firebaseapp.com",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next: Any) -> Response:
    request_id = uuid.uuid4().hex[:12]
    started_at = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        logger.exception(
            "request_failed method=%s path=%s request_id=%s elapsed_ms=%.2f",
            request.method,
            request.url.path,
            request_id,
            elapsed_ms,
        )
        raise

    elapsed_ms = (time.perf_counter() - started_at) * 1000
    logger.info(
        "request method=%s path=%s status=%s request_id=%s elapsed_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        request_id,
        elapsed_ms,
    )
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
    logger.warning(
        "http_error method=%s path=%s status=%s detail=%s",
        request.method,
        request.url.path,
        exc.status_code,
        detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "http_error", "message": detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.warning(
        "validation_error method=%s path=%s errors=%s",
        request.method,
        request.url.path,
        exc.errors(),
    )
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Request validation failed",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "unhandled_error method=%s path=%s message=%s",
        request.method,
        request.url.path,
        str(exc),
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "An unexpected server error occurred.",
        },
    )


@app.get("/api/health")
def health() -> dict[str, object]:
    status = contract_status()
    return {
        "ok": status["ok"],
        "loaded_keys": cache_keys(),
        "data_dir": status["data_dir"],
        "missing_exports": status["missing_exports"],
    }


app.include_router(trends.router, prefix="/api/v1")
app.include_router(spatial.router, prefix="/api/v1")
app.include_router(policy.router, prefix="/api/v1")
app.include_router(forecasting.router, prefix="/api/v1")
app.include_router(questions.router, prefix="/api/v1")
app.include_router(metadata.router, prefix="/api/v1")
