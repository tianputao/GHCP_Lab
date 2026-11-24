"""Track A — Typical 'Vibe Coding' implementation generated from a 1-sentence prompt
WITHOUT a formal specification.

Notice how plausible it looks at first glance — and its own happy-path test passes!
Yet it silently breaks 8+ enterprise invariants (IEEE-754 floating-point currency drift,
coupon over-refunding, unpaid-order refund, missing idempotency, missing approval
threshold, missing four-eyes check, missing audit trail, and ad-hoc error shape).
"""

from __future__ import annotations

import math
from datetime import datetime, UTC
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from base_app.src.errors import AppError, error_response
from base_app.src.models import OrderDict


async def _read_json_dict(request: Request) -> dict[str, Any]:
    try:
        raw = await request.json()
    except Exception:
        return {}
    return raw if isinstance(raw, dict) else {}


def create_app() -> FastAPI:
    app = FastAPI(title="Order Service Vibe Coding (Track A)", version="2.0.0")

    orders: dict[str, OrderDict] = {}
    refunds: list[dict[str, object]] = []
    order_seq = 1
    refund_seq = 1

    @app.get("/health")
    def health() -> JSONResponse:
        return JSONResponse(status_code=200, content={"status": "ok", "service": "order-service-vibe"})

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
            if (
                not customer_id
                or not isinstance(gross, int)
                or isinstance(gross, bool)
                or gross <= 0
                or not isinstance(discount, int)
                or isinstance(discount, bool)
            ):
                raise AppError(400, "VALIDATION_ERROR", "Invalid order payload")

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

    # ── Vibe-Coded Partial Refund Endpoint (exhibits classic spec-less flaws) ──
    @app.post("/orders/{order_id}/refunds")
    async def create_refund(order_id: str, request: Request) -> JSONResponse:
        nonlocal refund_seq
        order = orders.get(order_id)
        if order is None:
            # Architectural drift: ad-hoc `{ msg }` instead of `{ error: { code, message } }`
            return JSONResponse(status_code=404, content={"msg": "order not found"})

        body = await _read_json_dict(request)
        raw_amount = body.get("amountCents")
        if (
            isinstance(raw_amount, bool)
            or not isinstance(raw_amount, (int, float))
            or not math.isfinite(raw_amount)
            or raw_amount <= 0
        ):
            # Architectural drift + accepts floats like 10.5!
            return JSONResponse(status_code=400, content={"msg": "invalid amount"})

        # Bug 1: Uses grossAmountCents instead of paidAmountCents (ignores coupon discount!)
        if order["refundedAmountCents"] + raw_amount > order["grossAmountCents"]:
            return JSONResponse(status_code=400, content={"msg": "refund exceeds order total"})

        # Bug 2: Floating-point dollar math introduces IEEE-754 precision drift
        remaining_dollars = order["remainingRefundableCents"] / 100 - raw_amount / 100
        order["refundedAmountCents"] = int(order["refundedAmountCents"] + raw_amount)
        order["remainingRefundableCents"] = remaining_dollars * 100

        # Bug 3: No state check (refunds PENDING_PAYMENT / CANCELLED orders!)
        # Bug 4: No Idempotency-Key check (network retries double-refund!)
        # Bug 5: No high-value approval threshold (auto-completes >= 50000 cents!)
        # Bug 6: No reason / actorId validation, no immutable audit log!
        order["status"] = (
            "FULLY_REFUNDED"
            if order["refundedAmountCents"] >= order["paidAmountCents"]
            else "PARTIALLY_REFUNDED"
        )

        refund: dict[str, object] = {
            "id": f"ref-{refund_seq:04d}",
            "orderId": order["id"],
            "amountCents": raw_amount,
            "status": "COMPLETED",
            "reason": body.get("reason") if isinstance(body.get("reason"), str) else None,
        }
        refund_seq += 1
        refunds.append(refund)
        return JSONResponse(status_code=201, content={"refund": refund, "order": order})

    return app
