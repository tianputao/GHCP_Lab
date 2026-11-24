"""Track B — Specification-Driven Development (SDD) FastAPI Application.

Built strictly from `openspec/changes/add-partial-refund/` (`REQ-01`..`REQ-12`).
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from base_app.src.errors import error_response
from track_b_sdd.src.refund_service import RefundService


async def _read_json_dict(request: Request) -> dict[str, Any]:
    try:
        raw = await request.json()
    except Exception:
        return {}
    return raw if isinstance(raw, dict) else {}


def create_app(service: RefundService | None = None) -> FastAPI:
    app = FastAPI(title="Order Service SDD (Track B)", version="2.0.0")
    svc = RefundService() if service is None else service

    @app.get("/health")
    def health() -> JSONResponse:
        return JSONResponse(status_code=200, content={"status": "ok", "service": "order-service-sdd"})

    @app.get("/orders")
    def list_orders() -> JSONResponse:
        return JSONResponse(status_code=200, content={"data": svc.list_orders()})

    @app.get("/orders/{order_id}")
    def get_order(order_id: str) -> JSONResponse:
        try:
            return JSONResponse(status_code=200, content=svc.get_order(order_id))
        except Exception as err:
            return error_response(err)

    @app.post("/orders")
    async def create_order(request: Request) -> JSONResponse:
        try:
            body = await _read_json_dict(request)
            created = svc.create_order(
                customer_id=body.get("customerId"),
                gross_amount_cents=body.get("grossAmountCents"),
                coupon_discount_cents=body.get("couponDiscountCents", 0),
            )
            return JSONResponse(status_code=201, content=created)
        except Exception as err:
            return error_response(err)

    @app.post("/orders/{order_id}/pay")
    def pay_order(order_id: str) -> JSONResponse:
        try:
            return JSONResponse(status_code=200, content=svc.pay_order(order_id))
        except Exception as err:
            return error_response(err)

    @app.post("/orders/{order_id}/cancel")
    def cancel_order(order_id: str) -> JSONResponse:
        try:
            return JSONResponse(status_code=200, content=svc.cancel_order(order_id))
        except Exception as err:
            return error_response(err)

    @app.post("/orders/{order_id}/refunds")
    async def create_refund(order_id: str, request: Request) -> JSONResponse:
        try:
            body = await _read_json_dict(request)
            status_code, payload = svc.request_refund(
                order_id=order_id,
                idempotency_key=request.headers.get("Idempotency-Key"),
                amount_cents=body.get("amountCents"),
                reason=body.get("reason"),
                actor_id=body.get("actorId"),
            )
            return JSONResponse(status_code=status_code, content=payload)
        except Exception as err:
            return error_response(err)

    @app.post("/orders/{order_id}/refunds/{refund_id}/approve")
    async def approve_refund(order_id: str, refund_id: str, request: Request) -> JSONResponse:
        try:
            body = await _read_json_dict(request)
            result = svc.approve_refund(
                order_id=order_id,
                refund_id=refund_id,
                approver_id=body.get("approverId"),
            )
            return JSONResponse(status_code=200, content=result)
        except Exception as err:
            return error_response(err)

    @app.get("/orders/{order_id}/audit-log")
    def get_audit_log(order_id: str) -> JSONResponse:
        try:
            return JSONResponse(status_code=200, content=svc.get_audit_log(order_id))
        except Exception as err:
            return error_response(err)

    return app
