"""In-memory deterministic task store for Lab 01."""

from __future__ import annotations

from datetime import datetime, timedelta, UTC

from src.models import Task, TaskPriority, TaskStatus

PRIORITIES: tuple[TaskPriority, ...] = ("low", "medium", "high")
STATUSES: tuple[TaskStatus, ...] = ("todo", "in_progress", "done")


def create_seed_tasks(count: int = 25) -> list[Task]:
    """Generate deterministic seeded tasks so pagination and filtering exercises behave identically."""
    base_dt = datetime(2026, 10, 1, 9, 0, 0, tzinfo=UTC)
    tasks: list[Task] = []
    for i in range(1, count + 1):
        created_at = (base_dt + timedelta(minutes=i)).isoformat().replace("+00:00", "Z")
        tasks.append(
            Task(
                id=f"task-{i:03d}",
                title=f"Work item #{i}: Implement module checkpoint {i}",
                status=STATUSES[i % len(STATUSES)],
                priority=PRIORITIES[i % len(PRIORITIES)],
                created_at=created_at,
            )
        )
    return tasks


class TaskStore:
    """In-memory store holding Task entities."""

    def __init__(self, initial_tasks: list[Task] | None = None) -> None:
        source = create_seed_tasks(25) if initial_tasks is None else initial_tasks
        self._tasks: list[Task] = [
            Task(
                id=t.id,
                title=t.title,
                status=t.status,
                priority=t.priority,
                created_at=t.created_at,
            )
            for t in source
        ]

    def list_all(self) -> list[Task]:
        return [
            Task(
                id=t.id,
                title=t.title,
                status=t.status,
                priority=t.priority,
                created_at=t.created_at,
            )
            for t in self._tasks
        ]

    def find_by_id(self, task_id: str) -> Task | None:
        for item in self._tasks:
            if item.id == task_id:
                return Task(
                    id=item.id,
                    title=item.title,
                    status=item.status,
                    priority=item.priority,
                    created_at=item.created_at,
                )
        return None

    def create(self, title: str, priority: TaskPriority = "medium") -> Task:
        next_num = len(self._tasks) + 1
        now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        task = Task(
            id=f"task-{next_num:03d}",
            title=title,
            status="todo",
            priority=priority,
            created_at=now,
        )
        self._tasks.append(task)
        return Task(
            id=task.id,
            title=task.title,
            status=task.status,
            priority=task.priority,
            created_at=task.created_at,
        )

    def update(
        self,
        task_id: str,
        *,
        title: str | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
    ) -> Task | None:
        for target in self._tasks:
            if target.id == task_id:
                if title is not None:
                    target.title = title
                if status is not None:
                    target.status = status
                if priority is not None:
                    target.priority = priority
                return Task(
                    id=target.id,
                    title=target.title,
                    status=target.status,
                    priority=target.priority,
                    created_at=target.created_at,
                )
        return None

    def delete(self, task_id: str) -> bool:
        before = len(self._tasks)
        self._tasks = [t for t in self._tasks if t.id != task_id]
        return len(self._tasks) < before
