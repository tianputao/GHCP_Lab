"""Composition root for Lab 02 Task API."""

from __future__ import annotations

from dataclasses import dataclass

from api.routes.task_routes import Route, create_task_routes
from src.repositories.task_repository import TaskRepository


@dataclass(frozen=True)
class TaskApp:
    repo: TaskRepository
    routes: list[Route]


def create_app() -> TaskApp:
    """Create a TaskApp wired with an in-memory TaskRepository and routes."""
    repo = TaskRepository()
    routes = create_task_routes(repo)
    return TaskApp(repo=repo, routes=routes)
