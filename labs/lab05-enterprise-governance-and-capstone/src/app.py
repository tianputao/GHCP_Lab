"""FastAPI application factory for Lab 05 Capstone."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.routes.orders import create_orders_router


def create_app() -> FastAPI:
    app = FastAPI(title="Lab 05 Capstone API", version="2.0.0")

    @app.get("/health")
    def health() -> JSONResponse:
        return JSONResponse(status_code=200, content={"status": "ok", "service": "lab05-capstone"})

    app.include_router(create_orders_router())
    return app
