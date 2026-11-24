"""Baseline smoke tests for Lab 05 Capstone API."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.app import create_app


def test_health_and_orders_baseline() -> None:
    client = TestClient(create_app())

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    orders_res = client.get("/orders")
    assert orders_res.status_code == 200
    orders = orders_res.json()
    assert len(orders) == 2
    assert orders[0]["total"] == 100.0
    assert orders[1]["total"] == 225.0
