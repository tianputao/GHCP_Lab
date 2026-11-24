"""Baseline tests for the brownfield Order API."""

from __future__ import annotations

from fastapi.testclient import TestClient

from base_app.src.app import create_app


def test_order_create_pay_and_cancel_lifecycle() -> None:
    client = TestClient(create_app())

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    created = client.post(
        "/orders",
        json={"customerId": "cust-1", "grossAmountCents": 10000, "couponDiscountCents": 2000},
    )
    assert created.status_code == 201
    order = created.json()
    assert order["paidAmountCents"] == 8000
    assert order["status"] == "PENDING_PAYMENT"

    paid = client.post(f"/orders/{order['id']}/pay")
    assert paid.status_code == 200
    assert paid.json()["status"] == "PAID"

    second = client.post(
        "/orders",
        json={"customerId": "cust-2", "grossAmountCents": 5000},
    )
    second_id = second.json()["id"]
    cancelled = client.post(f"/orders/{second_id}/cancel")
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "CANCELLED"
