# Design: Partial Refund Ledger & Governance Engine

## Context

The brownfield Order API (`base-app/`) uses Express + TypeScript with an in-memory store and a standard `ApiError` envelope (`{ error: { code, message, details? } }`). All existing order amounts already use integer cents (`grossAmountCents`, `couponDiscountCents`, `paidAmountCents`).

## Goals / Non-Goals

**Goals:**
- Enforce exact integer-cent ledger invariants (`remainingRefundableCents = paidAmountCents - refundedAmountCents - pendingRefundAmountCents`).
- Guarantee idempotent retry behavior and payload-hash conflict detection (`SHA-256` over canonical JSON).
- Separate high-value refund initiation from human approval (Four-Eyes check).
- Provide an immutable, append-only audit log per order.

**Non-Goals:**
- Distributed locking across multiple processes (single-process synchronous critical section suffices for this deterministic demo; production uses DB unique constraints + row locks).
- External payment PSP settlement webhooks.

## Decisions

1. **Integer-Cents Accounting (`REQ-01`, `REQ-02`)**: Reject any non-integer `amountCents` (`!Number.isInteger(amountCents)`). Never convert to floating-point dollars inside ledger calculations.
2. **Idempotency Fingerprinting (`REQ-05`, `REQ-06`)**: Store `Map<string, { fingerprint, statusCode, body }>` keyed by `Idempotency-Key`. Compute `fingerprint = JSON.stringify({ orderId, amountCents, reason, actorId })`. Exact match returns stored result with `idempotentReplay: true`; mismatch returns `409 IDEMPOTENCY_CONFLICT`.
3. **Pending Balance Reservation (`REQ-07`, `REQ-08`)**: High-value refunds (`>= 50000` cents) immediately reserve `pendingRefundAmountCents` so concurrent/subsequent refunds cannot exceed `paidAmountCents` before approval completes.
4. **Error Envelope Reuse (`REQ-11`)**: Extend existing `AppError` hierarchy (`ValidationError` 400, `ForbiddenError` 403, `NotFoundError` 404, `ConflictError` 409, `UnprocessableError` 422) and serialize via a single `sendError()` helper.

## API Contract

| Method & Path | Success | Key Error Codes |
|---|---|---|
| `POST /orders/:id/refunds` | `201` (auto-completed `< 50000`) / `202` (`PENDING_APPROVAL >= 50000`) / `200` (idempotent replay) | `400 MISSING_IDEMPOTENCY_KEY`, `400 VALIDATION_ERROR`, `404 NOT_FOUND`, `409 INVALID_ORDER_STATE`, `409 IDEMPOTENCY_CONFLICT`, `422 REFUND_EXCEEDS_REMAINING` |
| `POST /orders/:id/refunds/:refundId/approve` | `200` (`COMPLETED`) | `400 VALIDATION_ERROR`, `403 SELF_APPROVAL_FORBIDDEN`, `404 NOT_FOUND`, `409 INVALID_REFUND_STATE` |
| `GET /orders/:id/audit-log` | `200` (`{ orderId, events }`) | `404 NOT_FOUND` |

## Risks / Trade-offs

- In-memory idempotency store resets on process restart — acceptable for this reproducible lab; production deployments must persist the idempotency table with a unique index on `idempotency_key`.
