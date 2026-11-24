"""Orders endpoints for Lab 05 Capstone."""

from __future__ import annotations

from typing import TypedDict

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.lib.discount import apply_discount


class OrderDict(TypedDict, total=False):
    id: int
    customer: str
    amount: float
    discountRule: str


def create_orders_router() -> APIRouter:
    orders: list[OrderDict] = [
        {"id": 1, "customer": "Ada Lovelace", "amount": 100.0},
        {"id": 2, "customer": "Alan Turing", "amount": 250.0, "discountRule": "10"},
    ]

    router = APIRouter(prefix="/orders")

    @router.get("")
    def list_orders() -> JSONResponse:
        result = [
            {
                **order,
                "total": apply_discount(order["amount"], order.get("discountRule", "0")),
            }
            for order in orders
        ]
        return JSONResponse(status_code=200, content=result)

    # ───────────────────────────────────────────────────────────────────────────
    # Lab 05 Capstone · Agent Mode & Governance Exercise (Step 5)
    #
    # TODO: Add a "POST /orders" endpoint that creates a new order.
    #   - Accept { "customer": str, "amount": float, "discountRule"?: str }
    #   - Validate: customer non-empty, amount > 0 and <= 1_000_000
    #   - Return 201 with the created order (assign next id)
    #   - Return 400 with a clear error object when validation fails
    #   - Add tests in tests/test_orders_smoke.py covering happy path & validation errors
    # ───────────────────────────────────────────────────────────────────────────

    return router
