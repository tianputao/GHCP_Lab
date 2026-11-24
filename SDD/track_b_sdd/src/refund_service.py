"""Spec-Driven Partial Refund Ledger Service implementing REQ-01..REQ-12
from `openspec/changes/add-partial-refund/specs/refunds/spec.md`.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import TypeGuard

from base_app.src.errors import AppError
from base_app.src.models import ErrorDetail, OrderDict
from track_b_sdd.src.models import (
    AuditEventDict,
    AuditEventType,
    RefundRecordDict,
    RefundResponsePayload,
)

HIGH_VALUE_APPROVAL_THRESHOLD_CENTS = 50_000


def _is_int(value: object) -> TypeGuard[int]:
    return isinstance(value, int) and not isinstance(value, bool)


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class _IdempotencyEntry:
    fingerprint: str
    status_code: int
    refund_id: str


class RefundService:
    """In-memory financial ledger enforcing OpenSpec REQ-01..REQ-12."""

    def __init__(self) -> None:
        self._orders: dict[str, OrderDict] = {}
        self._refunds: dict[str, RefundRecordDict] = {}
        self._audit_logs: dict[str, list[AuditEventDict]] = {}
        self._idempotency_store: dict[str, _IdempotencyEntry] = {}
        self._order_seq = 1
        self._refund_seq = 1
        self._audit_seq = 1

    def list_orders(self) -> list[OrderDict]:
        return [OrderDict(**o) for o in self._orders.values()]

    def get_order(self, order_id: str) -> OrderDict:
        order = self._orders.get(order_id)
        if order is None:
            raise AppError(404, "NOT_FOUND", f"Order {order_id} not found")
        return OrderDict(**order)

    def create_order(
        self,
        *,
        customer_id: object,
        gross_amount_cents: object,
        coupon_discount_cents: object = 0,
    ) -> OrderDict:
        customer = customer_id.strip() if isinstance(customer_id, str) else ""
        discount = 0 if coupon_discount_cents is None else coupon_discount_cents

        details: list[ErrorDetail] = []
        if not customer:
            details.append({"field": "customerId", "message": "customerId is required"})
        if not _is_int(gross_amount_cents) or (
            isinstance(gross_amount_cents, int) and gross_amount_cents <= 0
        ):
            details.append(
                {
                    "field": "grossAmountCents",
                    "message": "grossAmountCents must be a positive integer",
                }
            )
        if (
            not _is_int(discount)
            or discount < 0
            or (_is_int(gross_amount_cents) and discount > gross_amount_cents)
        ):
            details.append(
                {
                    "field": "couponDiscountCents",
                    "message": "couponDiscountCents must be an integer between 0 and grossAmountCents",
                }
            )
        if details:
            raise AppError(400, "VALIDATION_ERROR", "Invalid order payload", details)

        assert isinstance(gross_amount_cents, int) and isinstance(discount, int)
        paid = gross_amount_cents - discount
        order_id = f"ord-{self._order_seq:04d}"
        self._order_seq += 1

        order: OrderDict = {
            "id": order_id,
            "customerId": customer,
            "grossAmountCents": gross_amount_cents,
            "couponDiscountCents": discount,
            "paidAmountCents": paid,
            "refundedAmountCents": 0,
            "pendingRefundAmountCents": 0,
            "remainingRefundableCents": paid,
            "status": "PENDING_PAYMENT",
            "createdAt": _utc_now_iso(),
        }
        self._orders[order_id] = order
        self._audit_logs[order_id] = []
        return OrderDict(**order)

    def pay_order(self, order_id: str) -> OrderDict:
        order = self._require_mutable_order(order_id)
        if order["status"] != "PENDING_PAYMENT":
            raise AppError(
                409,
                "INVALID_ORDER_STATE",
                f"Cannot pay order in status {order['status']}",
            )
        order["status"] = "PAID"
        return OrderDict(**order)

    def cancel_order(self, order_id: str) -> OrderDict:
        order = self._require_mutable_order(order_id)
        if order["status"] != "PENDING_PAYMENT":
            raise AppError(
                409,
                "INVALID_ORDER_STATE",
                f"Cannot cancel order in status {order['status']}",
            )
        order["status"] = "CANCELLED"
        order["remainingRefundableCents"] = 0
        return OrderDict(**order)

    def request_refund(
        self,
        *,
        order_id: str,
        idempotency_key: str | None,
        amount_cents: object,
        reason: object,
        actor_id: object,
    ) -> tuple[int, RefundResponsePayload]:
        """Implement REQ-01..REQ-07, REQ-09, REQ-10, REQ-11."""
        # REQ-05: Mandatory Idempotency-Key header
        key = (idempotency_key or "").strip()
        if not key:
            raise AppError(
                400,
                "MISSING_IDEMPOTENCY_KEY",
                "Idempotency-Key header is required for refund requests",
            )

        # REQ-01 & REQ-09: Strict integer cents + reason + actorId validation
        details: list[ErrorDetail] = []
        if not _is_int(amount_cents) or (isinstance(amount_cents, int) and amount_cents <= 0):
            details.append(
                {
                    "field": "amountCents",
                    "message": "amountCents must be a positive integer in cents",
                }
            )
        reason_str = reason.strip() if isinstance(reason, str) else ""
        if len(reason_str) < 5:
            details.append(
                {
                    "field": "reason",
                    "message": "reason must be at least 5 non-whitespace characters",
                }
            )
        actor_str = actor_id.strip() if isinstance(actor_id, str) else ""
        if not actor_str:
            details.append({"field": "actorId", "message": "actorId is required"})
        if details:
            raise AppError(400, "VALIDATION_ERROR", "Invalid refund payload", details)

        assert isinstance(amount_cents, int)
        order = self._require_mutable_order(order_id)

        # REQ-05 & REQ-06: Idempotency replay & canonical fingerprint conflict check
        fingerprint = self._compute_fingerprint(
            order_id=order["id"],
            amount_cents=amount_cents,
            reason=reason_str,
            actor_id=actor_str,
        )
        existing_entry = self._idempotency_store.get(key)
        if existing_entry is not None:
            if existing_entry.fingerprint != fingerprint:
                raise AppError(
                    409,
                    "IDEMPOTENCY_CONFLICT",
                    f'Idempotency-Key "{key}" was already used with a different refund payload',
                )
            existing_refund = self._refunds.get(existing_entry.refund_id)
            if existing_refund is None:
                raise AppError(500, "INTERNAL_ERROR", "Idempotency record references missing refund")
            return (
                200,
                {
                    "refund": RefundRecordDict(**existing_refund),
                    "order": OrderDict(**order),
                    "idempotentReplay": True,
                },
            )

        # REQ-03: Order state machine guard
        if order["status"] not in ("PAID", "PARTIALLY_REFUNDED"):
            raise AppError(
                409,
                "INVALID_ORDER_STATE",
                f"Refunds are only allowed for PAID or PARTIALLY_REFUNDED orders (current: {order['status']})",
            )

        # REQ-01, REQ-02, REQ-04, REQ-07: Coupon-aware remaining refundable balance in exact integer cents
        current_remaining = (
            order["paidAmountCents"]
            - order["refundedAmountCents"]
            - order["pendingRefundAmountCents"]
        )
        if amount_cents > current_remaining:
            raise AppError(
                422,
                "REFUND_EXCEEDS_REMAINING",
                f"Requested {amount_cents} cents exceeds remaining refundable balance of {current_remaining} cents",
            )

        now = _utc_now_iso()
        refund_id = f"ref-{self._refund_seq:04d}"
        self._refund_seq += 1
        requires_approval = amount_cents >= HIGH_VALUE_APPROVAL_THRESHOLD_CENTS

        refund: RefundRecordDict = {
            "id": refund_id,
            "orderId": order["id"],
            "amountCents": amount_cents,
            "reason": reason_str,
            "actorId": actor_str,
            "status": "PENDING_APPROVAL" if requires_approval else "COMPLETED",
            "idempotencyKey": key,
            "createdAt": now,
        }
        if not requires_approval:
            refund["completedAt"] = now

        if requires_approval:
            # REQ-07: Reserve pending amount so subsequent requests cannot over-refund
            order["pendingRefundAmountCents"] += amount_cents
            order["remainingRefundableCents"] = (
                order["paidAmountCents"]
                - order["refundedAmountCents"]
                - order["pendingRefundAmountCents"]
            )
        else:
            # REQ-01 & REQ-04: Exact integer accounting & status transitions
            order["refundedAmountCents"] += amount_cents
            order["remainingRefundableCents"] = (
                order["paidAmountCents"]
                - order["refundedAmountCents"]
                - order["pendingRefundAmountCents"]
            )
            order["status"] = (
                "FULLY_REFUNDED"
                if order["refundedAmountCents"] == order["paidAmountCents"]
                else "PARTIALLY_REFUNDED"
            )

        self._refunds[refund_id] = refund
        status_code = 202 if requires_approval else 201
        self._idempotency_store[key] = _IdempotencyEntry(
            fingerprint=fingerprint,
            status_code=status_code,
            refund_id=refund_id,
        )

        # REQ-10: Append immutable audit log event
        self._append_audit(
            event_type="REFUND_PENDING_APPROVAL" if requires_approval else "REFUND_COMPLETED",
            order_id=order["id"],
            refund_id=refund_id,
            actor_id=actor_str,
            amount_cents=amount_cents,
            reason=reason_str,
            timestamp=now,
        )

        return (
            status_code,
            {
                "refund": RefundRecordDict(**refund),
                "order": OrderDict(**order),
                "idempotentReplay": False,
            },
        )

    def approve_refund(
        self,
        *,
        order_id: str,
        refund_id: str,
        approver_id: object,
    ) -> dict[str, object]:
        """Implement REQ-08 & REQ-10: Four-eyes human approval for high-value pending refunds."""
        approver = approver_id.strip() if isinstance(approver_id, str) else ""
        if not approver:
            raise AppError(
                400,
                "VALIDATION_ERROR",
                "approverId is required",
                [{"field": "approverId", "message": "approverId must be a non-empty string"}],
            )

        order = self._require_mutable_order(order_id)
        refund = self._refunds.get(refund_id)
        if refund is None or refund["orderId"] != order["id"]:
            raise AppError(
                404,
                "NOT_FOUND",
                f"Refund {refund_id} not found for order {order['id']}",
            )

        if refund["status"] != "PENDING_APPROVAL":
            raise AppError(
                409,
                "INVALID_REFUND_STATE",
                f"Refund {refund['id']} is already in status {refund['status']}",
            )

        # REQ-08: Separation of duties (Four-Eyes principle)
        if approver == refund["actorId"]:
            raise AppError(
                403,
                "SELF_APPROVAL_FORBIDDEN",
                "Refund requester cannot approve their own high-value refund",
            )

        now = _utc_now_iso()
        refund["status"] = "COMPLETED"
        refund["approverId"] = approver
        refund["completedAt"] = now

        amount = refund["amountCents"]
        order["pendingRefundAmountCents"] -= amount
        order["refundedAmountCents"] += amount
        order["remainingRefundableCents"] = (
            order["paidAmountCents"]
            - order["refundedAmountCents"]
            - order["pendingRefundAmountCents"]
        )
        order["status"] = (
            "FULLY_REFUNDED"
            if order["refundedAmountCents"] == order["paidAmountCents"]
            else "PARTIALLY_REFUNDED"
        )

        self._append_audit(
            event_type="REFUND_APPROVED",
            order_id=order["id"],
            refund_id=refund["id"],
            actor_id=approver,
            amount_cents=amount,
            reason=f"Approved refund: {refund['reason']}",
            timestamp=now,
        )

        return {"refund": RefundRecordDict(**refund), "order": OrderDict(**order)}

    def get_audit_log(self, order_id: str) -> dict[str, object]:
        self._require_mutable_order(order_id)
        events = [AuditEventDict(**e) for e in self._audit_logs.get(order_id, [])]
        return {"orderId": order_id, "events": events}

    def _require_mutable_order(self, order_id: str) -> OrderDict:
        order = self._orders.get(order_id)
        if order is None:
            raise AppError(404, "NOT_FOUND", f"Order {order_id} not found")
        return order

    @staticmethod
    def _compute_fingerprint(
        *,
        order_id: str,
        amount_cents: int,
        reason: str,
        actor_id: str,
    ) -> str:
        canonical = json.dumps(
            {
                "orderId": order_id,
                "amountCents": amount_cents,
                "reason": reason,
                "actorId": actor_id,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _append_audit(
        self,
        *,
        event_type: AuditEventType,
        order_id: str,
        refund_id: str,
        actor_id: str,
        amount_cents: int,
        reason: str,
        timestamp: str,
    ) -> None:
        event: AuditEventDict = {
            "id": f"aud-{self._audit_seq:04d}",
            "eventType": event_type,
            "orderId": order_id,
            "refundId": refund_id,
            "actorId": actor_id,
            "amountCents": amount_cents,
            "reason": reason,
            "timestamp": timestamp,
        }
        self._audit_seq += 1
        self._audit_logs.setdefault(order_id, []).append(event)
