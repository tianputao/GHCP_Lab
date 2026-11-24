# Proposal: Add Partial Refund with Idempotency, Approval Threshold & Audit Trail

## Why

Customers and support operations need to issue **partial refunds** on paid orders (for damaged items, shipping adjustments, or partial cancellations) without cancelling the entire order. Previously, ad-hoc "Vibe Coding" prototypes led to floating-point rounding bugs, double refunds on network retries, over-refunding coupon discounts, and missing audit trails.

## What Changes

Introduce a spec-driven, auditable partial refund capability on top of the existing brownfield Order API:
- Add `POST /orders/:id/refunds` supporting partial and cumulative refunds in integer cents.
- Enforce `Idempotency-Key` replay safety and conflict detection (`409 IDEMPOTENCY_CONFLICT`).
- Enforce refundable cap based on `paidAmountCents` (after coupon discount), never gross price.
- Require human approval (`POST /orders/:id/refunds/:refundId/approve`) with separation of duties for refunds `>= 50000` cents.
- Append immutable audit records exposed via `GET /orders/:id/audit-log`.

## Explicit Non-Goals (Out of Scope)

- External payment gateway HTTP calls (Stripe/Alipay/Adyen integration is mocked/in-process).
- Multi-currency FX conversion (single currency integer cents only).
- Automatic refund reversal / chargeback workflows.
- Replacing existing `POST /orders`, `POST /orders/:id/pay`, or `POST /orders/:id/cancel` contracts.

## Capabilities

### New Capabilities
- `refunds`: Partial and cumulative order refunds with integer-cent accounting, coupon-aware caps, idempotency protection, approval workflow, and immutable audit trail.

### Modified Capabilities
- `orders`: Extend order lifecycle states to include `PARTIALLY_REFUNDED` and `FULLY_REFUNDED` while preserving `REQ-12` backward compatibility.

## Impact

- Affected API routes: `POST /orders/:id/refunds`, `POST /orders/:id/refunds/:refundId/approve`, `GET /orders/:id/audit-log`.
- Affected domain model: Order financial ledger fields (`refundedAmountCents`, `pendingRefundAmountCents`, `remainingRefundableCents`), Refund entity, Idempotency record, AuditEvent entity.
- Zero new external database dependencies (runs cleanly in-process for deterministic verification).
