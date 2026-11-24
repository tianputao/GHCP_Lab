# Tasks: add-partial-refund

## 1. Domain Model & Ledger Invariants

- [x] 1.1 Extend Order status and ledger fields (`refundedAmountCents`, `pendingRefundAmountCents`, `remainingRefundableCents`) using integer cents only (`REQ-01`, `REQ-02`, `REQ-04`).
- [x] 1.2 Add `RefundRecord`, `AuditEvent`, and `IdempotencyEntry` types plus `ForbiddenError` (403) and `UnprocessableError` (422) using the unified error envelope (`REQ-08`, `REQ-10`, `REQ-11`).

## 2. Refund Service & Policy Enforcement

- [x] 2.1 Implement order state guard allowing refunds only for `PAID` and `PARTIALLY_REFUNDED` orders (`REQ-03`).
- [x] 2.2 Implement strict validation for `Idempotency-Key`, integer `amountCents > 0`, `reason` (>= 5 chars), and `actorId` (`REQ-05`, `REQ-09`).
- [x] 2.3 Implement idempotency replay (`idempotentReplay: true`) and canonical payload conflict detection (`409 IDEMPOTENCY_CONFLICT`) (`REQ-05`, `REQ-06`).
- [x] 2.4 Implement coupon-aware remaining cap check (`422 REFUND_EXCEEDS_REMAINING`) and high-value approval reservation (`>= 50000` cents -> `202 PENDING_APPROVAL`) (`REQ-02`, `REQ-07`).
- [x] 2.5 Implement `approveRefund` with four-eyes check (`403 SELF_APPROVAL_FORBIDDEN`) and cumulative status transition to `PARTIALLY_REFUNDED` / `FULLY_REFUNDED` (`REQ-04`, `REQ-08`).
- [x] 2.6 Append immutable audit events on creation and approval, exposed at `GET /orders/:id/audit-log` (`REQ-10`).

## 3. Verification & Traceability

- [x] 3.1 Verify all brownfield endpoints remain intact (`REQ-12`).
- [x] 3.2 Run `track_b_sdd/tests/test_spec_compliance.py` and `evaluator/compare.py` to confirm 12/12 acceptance criteria pass and contrast against Vibe Coding baseline (`REQ-01`..`REQ-12`).
