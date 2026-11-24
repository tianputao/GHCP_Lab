"""Domain models for the Lab 01 Task API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypedDict

TaskStatus = Literal["todo", "in_progress", "done"]
TaskPriority = Literal["low", "medium", "high"]

VALID_STATUSES: frozenset[str] = frozenset({"todo", "in_progress", "done"})
VALID_PRIORITIES: frozenset[str] = frozenset({"low", "medium", "high"})


class TaskDict(TypedDict):
    id: str
    title: str
    status: TaskStatus
    priority: TaskPriority
    createdAt: str


@dataclass
class Task:
    id: str
    title: str
    status: TaskStatus
    priority: TaskPriority
    created_at: str

    def to_dict(self) -> TaskDict:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "priority": self.priority,
            "createdAt": self.created_at,
        }
