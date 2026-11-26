"""Task CRUD routes for Lab 01."""

from __future__ import annotations

import base64
import binascii
import re
from datetime import datetime
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
    def list_tasks(request: Request) -> JSONResponse:
        raw_limit = request.query_params.get("limit", "10")
        try:
            if not re.fullmatch(r"[+-]?[0-9]+", raw_limit):
                raise ValueError
            limit = int(raw_limit)
            if not 1 <= limit <= 50:
                raise ValueError
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"error": {"code": "VALIDATION_ERROR", "message": "limit must be an integer from 1 to 50"}},
            )

        tasks = sorted(
            store.list_all(),
            key=lambda task: (datetime.fromisoformat(task.created_at), task.id),
            reverse=True,
        )
        cursor = request.query_params.get("cursor")
        start = 0
        if cursor is not None:
            try:
                decoded = base64.b64decode(cursor, validate=True).decode("utf-8")
                if base64.b64encode(decoded.encode("utf-8")).decode("ascii") != cursor:
                    raise ValueError
                start = next(i + 1 for i, task in enumerate(tasks) if task.id == decoded)
            except (ValueError, UnicodeError, binascii.Error, StopIteration):
                return JSONResponse(
                    status_code=400,
                    content={"error": {"code": "VALIDATION_ERROR", "message": "cursor is invalid or unknown"}},
                )

        page = tasks[start : start + limit]
        has_more = start + limit < len(tasks)
        next_cursor = (
            base64.b64encode(page[-1].id.encode("utf-8")).decode("ascii") if has_more else None
        )
        return JSONResponse(
            status_code=200,
            content={"data": [task.to_dict() for task in page], "nextCursor": next_cursor, "hasMore": has_more},
        )

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
