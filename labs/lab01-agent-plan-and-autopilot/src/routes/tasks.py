"""Task CRUD routes for Lab 01."""

from __future__ import annotations

from typing import Any, cast

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from src.models import VALID_PRIORITIES, VALID_STATUSES, TaskPriority, TaskStatus
from src.store import TaskStore


async def _read_json_dict(request: Request) -> dict[str, Any]:
    try:
        raw = await request.json()
    except Exception:
        return {}
    return raw if isinstance(raw, dict) else {}


def create_tasks_router(store: TaskStore) -> APIRouter:
    router = APIRouter(prefix="/tasks")

    @router.get("")
    def list_tasks() -> JSONResponse:
        """GET /tasks — currently returns all seeded tasks without pagination.

        Lab 01 Exercise 1: Ask Plan -> Agent/Autopilot to add cursor-based pagination here.
        """
        tasks = [t.to_dict() for t in store.list_all()]
        return JSONResponse(status_code=200, content={"data": tasks, "total": len(tasks)})

    @router.get("/{task_id}")
    def get_task(task_id: str) -> JSONResponse:
        task = store.find_by_id(task_id)
        if task is None:
            return JSONResponse(
                status_code=404,
                content={"error": {"code": "NOT_FOUND", "message": f"Task {task_id} not found"}},
            )
        return JSONResponse(status_code=200, content=task.to_dict())

    @router.post("")
    async def create_task(request: Request) -> JSONResponse:
        body = await _read_json_dict(request)
        title = body.get("title")
        if not isinstance(title, str) or not title.strip():
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "title must be a non-empty string",
                    }
                },
            )

        priority = body.get("priority", "medium")
        if not isinstance(priority, str) or priority not in VALID_PRIORITIES:
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "priority must be low, medium, or high",
                    }
                },
            )

        created = store.create(title.strip(), cast(TaskPriority, priority))
        return JSONResponse(status_code=201, content=created.to_dict())

    @router.patch("/{task_id}")
    async def update_task(task_id: str, request: Request) -> JSONResponse:
        body = await _read_json_dict(request)
        title_patch: str | None = None
        status_patch: TaskStatus | None = None
        priority_patch: TaskPriority | None = None

        if "title" in body:
            raw_title = body["title"]
            if not isinstance(raw_title, str) or not raw_title.strip():
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "message": "title must be a non-empty string",
                        }
                    },
                )
            title_patch = raw_title.strip()

        if "status" in body:
            raw_status = body["status"]
            if not isinstance(raw_status, str) or raw_status not in VALID_STATUSES:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "message": "status must be todo, in_progress, or done",
                        }
                    },
                )
            status_patch = cast(TaskStatus, raw_status)

        if "priority" in body:
            raw_priority = body["priority"]
            if not isinstance(raw_priority, str) or raw_priority not in VALID_PRIORITIES:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "message": "priority must be low, medium, or high",
                        }
                    },
                )
            priority_patch = cast(TaskPriority, raw_priority)

        updated = store.update(
            task_id,
            title=title_patch,
            status=status_patch,
            priority=priority_patch,
        )
        if updated is None:
            return JSONResponse(
                status_code=404,
                content={"error": {"code": "NOT_FOUND", "message": f"Task {task_id} not found"}},
            )
        return JSONResponse(status_code=200, content=updated.to_dict())

    @router.delete("/{task_id}", response_model=None)
    def delete_task(task_id: str) -> Response:
        removed = store.delete(task_id)
        if not removed:
            return JSONResponse(
                status_code=404,
                content={"error": {"code": "NOT_FOUND", "message": f"Task {task_id} not found"}},
            )
        return Response(status_code=204)

    return router
