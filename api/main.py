"""FastAPI application entrypoint."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import forecasting, metadata, policy, questions, spatial, trends
from api.services.data_loader import cache_keys, load_all_data


@asynccontextmanager
async def lifespan(_: FastAPI):
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


@app.get("/api/health")
def health() -> dict[str, object]:
    return {"ok": True, "loaded_keys": cache_keys()}


app.include_router(trends.router, prefix="/api/v1")
app.include_router(spatial.router, prefix="/api/v1")
app.include_router(policy.router, prefix="/api/v1")
app.include_router(forecasting.router, prefix="/api/v1")
app.include_router(questions.router, prefix="/api/v1")
app.include_router(metadata.router, prefix="/api/v1")
