"""Domain models for Track B (SDD) Partial Refund & Audit Ledger."""

from __future__ import annotations

from typing import Literal, TypedDict

from base_app.src.models import OrderDict

RefundStatus = Literal["COMPLETED", "PENDING_APPROVAL"]
AuditEventType = Literal["REFUND_COMPLETED", "REFUND_PENDING_APPROVAL", "REFUND_APPROVED"]


class RefundRecordDict(TypedDict, total=False):
    id: str
    orderId: str
    amountCents: int
    reason: str
    actorId: str
    status: RefundStatus
    idempotencyKey: str
    approverId: str
    createdAt: str
    completedAt: str


class AuditEventDict(TypedDict):
    id: str
    eventType: AuditEventType
    orderId: str
    refundId: str
    actorId: str
    amountCents: int
    reason: str
    timestamp: str


class RefundResponsePayload(TypedDict):
    refund: RefundRecordDict
    order: OrderDict
    idempotentReplay: bool
