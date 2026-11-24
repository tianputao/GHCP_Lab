"""Clean Brownfield Order API (As-Is Baseline).

Notice: No refund endpoint exists yet. Copy this folder via
`uv run python scripts/reset_playground.py` to test Vibe Coding vs SDD hands-on.
"""

from __future__ import annotations

from datetime import datetime, UTC
from typing import Any, TypeGuard

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from base_app.src.errors import AppError, error_response
from base_app.src.models import ErrorDetail, OrderDict


def _is_int(value: object) -> TypeGuard[int]:
    return isinstance(value, int) and not isinstance(value, bool)


async def _read_json_dict(request: Request) -> dict[str, Any]:
    try:
        raw = await request.json()
    except Exception:
        return {}
    return raw if isinstance(raw, dict) else {}


def create_app() -> FastAPI:
    app = FastAPI(title="Order Service Base (Brownfield)", version="2.0.0")

    orders: dict[str, OrderDict] = {}
    order_seq = 1

    @app.get("/health")
    def health() -> JSONResponse:
        return JSONResponse(status_code=200, content={"status": "ok", "service": "order-service-base"})

    @app.get("/orders")
    def list_orders() -> JSONResponse:
        return JSONResponse(status_code=200, content={"data": list(orders.values())})

    @app.get("/orders/{order_id}")
    def get_order(order_id: str) -> JSONResponse:
        try:
            order = orders.get(order_id)
            if order is None:
                raise AppError(404, "NOT_FOUND", f"Order {order_id} not found")
            return JSONResponse(status_code=200, content=order)
        except Exception as err:
            return error_response(err)

    @app.post("/orders")
    async def create_order(request: Request) -> JSONResponse:
        nonlocal order_seq
        try:
            body = await _read_json_dict(request)
            raw_customer = body.get("customerId")
            customer_id = raw_customer.strip() if isinstance(raw_customer, str) else ""
            gross = body.get("grossAmountCents")
            discount = body.get("couponDiscountCents", 0)

            details: list[ErrorDetail] = []
            if not customer_id:
                details.append({"field": "customerId", "message": "customerId is required"})
            if not _is_int(gross) or (isinstance(gross, int) and gross <= 0):
                details.append(
                    {"field": "grossAmountCents", "message": "grossAmountCents must be a positive integer"}
                )
            if (
                not _is_int(discount)
                or discount < 0
                or (_is_int(gross) and discount > gross)
            ):
                details.append(
                    {
                        "field": "couponDiscountCents",
                        "message": "couponDiscountCents must be an integer between 0 and grossAmountCents",
                    }
                )
            if details:
                raise AppError(400, "VALIDATION_ERROR", "Invalid order payload", details)

            assert isinstance(gross, int) and isinstance(discount, int)
            paid = gross - discount
            order_id = f"ord-{order_seq:04d}"
            order_seq += 1
            order: OrderDict = {
                "id": order_id,
                "customerId": customer_id,
                "grossAmountCents": gross,
                "couponDiscountCents": discount,
                "paidAmountCents": paid,
                "refundedAmountCents": 0,
                "pendingRefundAmountCents": 0,
                "remainingRefundableCents": paid,
                "status": "PENDING_PAYMENT",
                "createdAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            }
            orders[order_id] = order
            return JSONResponse(status_code=201, content=order)
        except Exception as err:
            return error_response(err)

    @app.post("/orders/{order_id}/pay")
    def pay_order(order_id: str) -> JSONResponse:
        try:
            order = orders.get(order_id)
            if order is None:
                raise AppError(404, "NOT_FOUND", f"Order {order_id} not found")
            if order["status"] != "PENDING_PAYMENT":
                raise AppError(
                    409,
                    "INVALID_ORDER_STATE",
                    f"Cannot pay order in status {order['status']}",
                )
            order["status"] = "PAID"
            return JSONResponse(status_code=200, content=order)
        except Exception as err:
            return error_response(err)

    @app.post("/orders/{order_id}/cancel")
    def cancel_order(order_id: str) -> JSONResponse:
        try:
            order = orders.get(order_id)
            if order is None:
                raise AppError(404, "NOT_FOUND", f"Order {order_id} not found")
            if order["status"] != "PENDING_PAYMENT":
                raise AppError(
                    409,
                    "INVALID_ORDER_STATE",
                    f"Cannot cancel order in status {order['status']}",
                )
            order["status"] = "CANCELLED"
            order["remainingRefundableCents"] = 0
            return JSONResponse(status_code=200, content=order)
        except Exception as err:
            return error_response(err)

    return app
