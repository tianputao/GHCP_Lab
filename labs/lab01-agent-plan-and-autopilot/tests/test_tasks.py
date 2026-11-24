"""Baseline contract tests for Lab 01 Task API."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.app import create_app
from src.store import TaskStore


def test_health_returns_ok() -> None:
    client = TestClient(create_app(TaskStore()))
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_list_tasks_returns_seeded_tasks() -> None:
    client = TestClient(create_app(TaskStore()))
    res = client.get("/tasks")
    assert res.status_code == 200
    body = res.json()
    assert len(body["data"]) == 25
    assert body["total"] == 25


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

    deleted = client.delete(f"/tasks/{task['id']}")
    assert deleted.status_code == 204
