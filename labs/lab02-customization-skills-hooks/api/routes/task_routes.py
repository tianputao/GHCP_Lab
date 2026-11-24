"""RESTful task endpoints (the API-layer canonical example for Lab 02)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from api.http import ApiRequest, ApiResponse, RouteHandler, send_error
from api.validation import validate_create_task, validate_update_task
from src.repositories.task_repository import TaskRepository

HttpMethod = Literal["GET", "POST", "PUT", "DELETE"]


@dataclass(frozen=True)
class Route:
    """A registered route: HTTP method + path pattern + handler."""

    method: HttpMethod
    path: str
    handler: RouteHandler


def create_task_routes(repo: TaskRepository) -> list[Route]:
    """Build task routes against an injected TaskRepository."""

    def list_tasks(req: ApiRequest, res: ApiResponse) -> None:
        try:
            tag = req.query.get("tag")
            res.status(200).json([t.to_dict() for t in repo.find_all(tag)])
        except Exception as err:
            send_error(res, err)

    def get_one(req: ApiRequest, res: ApiResponse) -> None:
        try:
            res.status(200).json(repo.get_by_id(req.params.get("id", "")).to_dict())
        except Exception as err:
            send_error(res, err)

    def create(req: ApiRequest, res: ApiResponse) -> None:
        try:
            payload = validate_create_task(req.body)
            res.status(201).json(repo.create(payload).to_dict())
        except Exception as err:
            send_error(res, err)

    def update(req: ApiRequest, res: ApiResponse) -> None:
        try:
            payload = validate_update_task(req.body)
            res.status(200).json(repo.update(req.params.get("id", ""), payload).to_dict())
        except Exception as err:
            send_error(res, err)

    def remove(req: ApiRequest, res: ApiResponse) -> None:
        try:
            repo.delete(req.params.get("id", ""))
            res.status(204).end()
        except Exception as err:
            send_error(res, err)

    return [
        Route(method="GET", path="/tasks", handler=list_tasks),
        Route(method="GET", path="/tasks/:id", handler=get_one),
        Route(method="POST", path="/tasks", handler=create),
        Route(method="PUT", path="/tasks/:id", handler=update),
        Route(method="DELETE", path="/tasks/:id", handler=remove),
    ]
