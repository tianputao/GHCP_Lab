"""Domain models for the Lab 02 Task API.

Intentionally small and strictly typed so Copilot has clean examples to follow
once custom instructions are added during Demo 1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypedDict

TaskStatus = Literal["todo", "in_progress", "done"]


class FieldErrorDetail(TypedDict):
    field: str
    message: str


class ApiErrorPayload(TypedDict, total=False):
    code: str
    message: str
    details: list[FieldErrorDetail]


class ApiErrorBody(TypedDict):
    error: ApiErrorPayload


class TaskDict(TypedDict):
    id: str
    title: str
    description: str | None
    status: TaskStatus
    tags: list[str]
    createdAt: str
    updatedAt: str


@dataclass
class Task:
    """A task owned by a user."""

    id: str
    title: str
    description: str | None
    status: TaskStatus
    created_at: str
    updated_at: str
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> TaskDict:
        """Serialize the task to its canonical JSON representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "tags": list(self.tags),
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


@dataclass(frozen=True)
class CreateTaskInput:
    """Validated input accepted when creating a task."""

    title: str
    description: str | None = None


@dataclass(frozen=True)
class UpdateTaskInput:
    """Validated input accepted when updating a task (partial update)."""

    title: str | None = None
    has_description: bool = False
    description: str | None = None
    status: TaskStatus | None = None
