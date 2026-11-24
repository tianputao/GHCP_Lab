"""Track A (Vibe Coding) own happy-path tests — ALL PASS, creating a false green light!"""

from __future__ import annotations

from fastapi.testclient import TestClient

from track_a_vibe_coding.src.app import create_app


def test_vibe_happy_path_partial_refund_passes() -> None:
    client = TestClient(create_app())

    created = client.post(
        "/orders",
        json={"customerId": "cust-vibe", "grossAmountCents": 10000},
    )
    assert created.status_code == 201
    order_id = created.json()["id"]

    paid = client.post(f"/orders/{order_id}/pay")
    assert paid.status_code == 200

    refunded = client.post(
        f"/orders/{order_id}/refunds",
        json={"amountCents": 3000, "reason": "partial return"},
    )
    assert refunded.status_code == 201
    body = refunded.json()
    assert body["order"]["refundedAmountCents"] == 3000
    assert body["order"]["status"] == "PARTIALLY_REFUNDED"
