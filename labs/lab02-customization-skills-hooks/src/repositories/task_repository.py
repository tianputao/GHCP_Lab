"""Repository pattern for tasks (canonical good example for Lab 02)."""

from __future__ import annotations

from datetime import datetime, UTC
from uuid import uuid4

from src.db import InMemoryTable
from src.errors import NotFoundError
from src.models import CreateTaskInput, Task, UpdateTaskInput


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


class TaskRepository:
    """Centralized data access for Task records."""

    def __init__(self) -> None:
        self._table: InMemoryTable[Task] = InMemoryTable()

    def find_all(self, tag: str | None = None) -> list[Task]:
        """Return every task, optionally filtered by tag.

        Args:
            tag: When provided, only tasks containing this tag are returned.

        Returns:
            Matching tasks (possibly empty).

        Production SQL:
            SELECT * FROM tasks WHERE (? IS NULL OR id IN
              (SELECT task_id FROM task_tags WHERE tag = ?))
        """
        if tag is None:
            return self._table.find_all()
        return self._table.find_all(lambda t: tag in t.tags)

    def get_by_id(self, task_id: str) -> Task:
        """Return a single task by id.

        Args:
            task_id: The task id.

        Returns:
            The matching Task.

        Raises:
            NotFoundError: When no task has the given id.

        Production SQL:
            SELECT * FROM tasks WHERE id = ?
        """
        task = self._table.find_by_id(task_id)
        if task is None:
            raise NotFoundError("Task", task_id)
        return task

    def create(self, payload: CreateTaskInput) -> Task:
        """Create a new task with server-assigned id, status, and timestamps.

        Args:
            payload: Validated creation input.

        Returns:
            The newly created Task.

        Production SQL:
            INSERT INTO tasks (id, title, description, status, created_at, updated_at)
              VALUES (?, ?, ?, ?, ?, ?)
        """
        now = _utc_now_iso()
        task = Task(
            id=str(uuid4()),
            title=payload.title,
            description=payload.description,
            status="todo",
            tags=[],
            created_at=now,
            updated_at=now,
        )
        self._table.insert(task)
        return task

    def update(self, task_id: str, payload: UpdateTaskInput) -> Task:
        """Apply a partial update to an existing task.

        Args:
            task_id: The task id.
            payload: Fields to update.

        Returns:
            The updated Task.

        Raises:
            NotFoundError: When no task has the given id.

        Production SQL:
            UPDATE tasks SET title = ?, description = ?, status = ?, updated_at = ?
              WHERE id = ?
        """
        existing = self.get_by_id(task_id)
        updated = Task(
            id=existing.id,
            title=payload.title if payload.title is not None else existing.title,
            description=payload.description if payload.has_description else existing.description,
            status=payload.status if payload.status is not None else existing.status,
            tags=list(existing.tags),
            created_at=existing.created_at,
            updated_at=_utc_now_iso(),
        )
        self._table.update(updated)
        return updated

    def delete(self, task_id: str) -> None:
        """Delete a task by id.

        Args:
            task_id: The task id.

        Raises:
            NotFoundError: When no task has the given id.

        Production SQL:
            DELETE FROM tasks WHERE id = ?
        """
        changes = self._table.remove(task_id)
        if changes == 0:
            raise NotFoundError("Task", task_id)
