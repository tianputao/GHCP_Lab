"""FastAPI application factory for Lab 01."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.routes.tasks import create_tasks_router
from src.store import TaskStore


def create_app(store: TaskStore | None = None) -> FastAPI:
    app = FastAPI(title="Lab 01 Task API", version="2.0.0")
    task_store = TaskStore() if store is None else store

    @app.get("/health")
    def health() -> JSONResponse:
        return JSONResponse(status_code=200, content={"status": "ok", "service": "lab01-task-api"})

    app.include_router(create_tasks_router(task_store))
    return app
