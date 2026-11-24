"""Domain models for the brownfield Order API."""

from __future__ import annotations

from typing import Literal, TypedDict

OrderStatus = Literal[
    "PENDING_PAYMENT",
    "PAID",
    "PARTIALLY_REFUNDED",
    "FULLY_REFUNDED",
    "CANCELLED",
]


class ErrorDetail(TypedDict):
    field: str
    message: str


class OrderDict(TypedDict):
    id: str
    customerId: str
    grossAmountCents: int
    couponDiscountCents: int
    paidAmountCents: int
    refundedAmountCents: int
    pendingRefundAmountCents: int
    remainingRefundableCents: int | float
    status: OrderStatus
    createdAt: str
