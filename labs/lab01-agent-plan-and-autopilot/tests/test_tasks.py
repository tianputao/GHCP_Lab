"""Baseline contract tests for Lab 01 Task API."""

from __future__ import annotations

import base64

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.models import Task
from src.store import TaskStore


def test_health_returns_ok() -> None:
    client = TestClient(create_app(TaskStore()))
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_list_tasks_paginates_seeded_tasks() -> None:
    client = TestClient(create_app(TaskStore()))
    cursor: str | None = None
    for expected_ids in (range(25, 15, -1), range(15, 5, -1), range(5, 0, -1)):
        res = client.get("/tasks", params={"cursor": cursor} if cursor is not None else {})
        assert res.status_code == 200
        body = res.json()
        assert set(body) == {"data", "nextCursor", "hasMore"}
        assert [task["id"] for task in body["data"]] == [
            f"task-{number:03d}" for number in expected_ids
        ]
        cursor = body["nextCursor"]
        assert body["hasMore"] is (len(body["data"]) == 10)
        if cursor is not None:
            assert base64.b64decode(cursor).decode() == body["data"][-1]["id"]

    assert cursor is None


def test_list_tasks_limit_boundaries_and_empty_store() -> None:
    client = TestClient(create_app(TaskStore()))
    first = client.get("/tasks", params={"limit": 1}).json()
    assert len(first["data"]) == 1
    assert first["hasMore"] is True
    last = client.get("/tasks", params={"limit": 50}).json()
    assert len(last["data"]) == 25
    assert last["hasMore"] is False
    assert last["nextCursor"] is None
    exact = client.get("/tasks", params={"limit": 25}).json()
    assert exact["hasMore"] is False
    assert exact["nextCursor"] is None

    empty = TestClient(create_app(TaskStore([]))).get("/tasks")
    assert empty.json() == {"data": [], "nextCursor": None, "hasMore": False}


def test_list_tasks_sorts_ties_and_fractional_timestamps() -> None:
    tasks = [
        Task(id="a", title="A", status="todo", priority="low", created_at="2026-01-01T00:00:00Z"),
        Task(id="b", title="B", status="todo", priority="low", created_at="2026-01-01T00:00:00Z"),
        Task(id="c", title="C", status="todo", priority="low", created_at="2026-01-01T00:00:00.1Z"),
    ]
    client = TestClient(create_app(TaskStore(tasks)))
    first = client.get("/tasks", params={"limit": 2}).json()
    assert [task["id"] for task in first["data"]] == ["c", "b"]
    second = client.get("/tasks", params={"limit": 2, "cursor": first["nextCursor"]}).json()
    assert [task["id"] for task in second["data"]] == ["a"]
    assert second["nextCursor"] is None
    assert second["hasMore"] is False


@pytest.mark.parametrize("limit", ["0", "-1", "51", "1.5", "abc", "", "1e1"])
def test_list_tasks_rejects_invalid_limit(limit: str) -> None:
    client = TestClient(create_app(TaskStore()))
    res = client.get("/tasks", params={"limit": limit})
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"
    assert res.json()["error"]["message"]


@pytest.mark.parametrize("cursor", ["", "%%%", "dGFzay0wMDE", "/w==", "dGFzay05OTk="])
def test_list_tasks_rejects_invalid_cursor(cursor: str) -> None:
    client = TestClient(create_app(TaskStore()))
    res = client.get("/tasks", params={"cursor": cursor})
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"
    assert res.json()["error"]["message"]


def test_create_validate_and_delete_task() -> None:
    client = TestClient(create_app(TaskStore()))

    bad = client.post("/tasks", json={"title": "   "})
    assert bad.status_code == 400
    assert bad.json()["error"]["code"] == "VALIDATION_ERROR"

    created = client.post(
        "/tasks",
        json={"title": "Verify Plan -> Agent loop", "priority": "high"},
    )
    assert created.status_code == 201
    task = created.json()
    assert task["title"] == "Verify Plan -> Agent loop"
    assert task["priority"] == "high"

    fetched = client.get(f"/tasks/{task['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == task

    updated = client.patch(f"/tasks/{task['id']}", json={"status": "done"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "done"

    deleted = client.delete(f"/tasks/{task['id']}")
    assert deleted.status_code == 204
    assert client.get(f"/tasks/{task['id']}").status_code == 404
