# Spec Delta: Refunds Capability

## Purpose
Provide financially accurate, idempotent, policy-governed partial and cumulative order refunds with high-value human approval and immutable audit trails.

## ADDED Requirements

### Requirement: REQ-01 Integer Cents Monetary Precision
The system SHALL represent and calculate all order and refund monetary amounts strictly as non-negative integer cents (`amountCents`, `paidAmountCents`, `refundedAmountCents`, `remainingRefundableCents`) and MUST NOT use floating-point currency subtraction.

#### Scenario: Sequential small partial refunds avoid floating-point drift
- **WHEN** an order with `paidAmountCents = 1999` receives a refund of `10` cents followed by a refund of `20` cents
- **THEN** `refundedAmountCents` SHALL equal `30` and `remainingRefundableCents` SHALL equal `1969` exactly

### Requirement: REQ-02 Coupon-Aware Refundable Cap
The system SHALL cap total refundable amount (completed plus pending approval) at `paidAmountCents = grossAmountCents - couponDiscountCents` and MUST NOT allow refunding coupon discount value.

#### Scenario: Refund exceeds net paid amount despite being below gross amount
- **WHEN** an order has `grossAmountCents = 10000` and `couponDiscountCents = 2000` (`paidAmountCents = 8000`) and a client requests a refund of `9000` cents
- **THEN** the system SHALL reject the request with HTTP `422` and error code `REFUND_EXCEEDS_REMAINING`

### Requirement: REQ-03 Order State Machine Guard
The system SHALL permit refund creation ONLY when the order status is `PAID` or `PARTIALLY_REFUNDED`.

#### Scenario: Refund attempted on unpaid or cancelled order
- **WHEN** a client requests a refund on an order in `PENDING_PAYMENT`, `CANCELLED`, or `FULLY_REFUNDED` state
- **THEN** the system SHALL reject the request with HTTP `409` and error code `INVALID_ORDER_STATE`

### Requirement: REQ-04 Cumulative Partial Refund and State Transitions
The system SHALL track cumulative refunds across multiple requests, transitioning the order to `PARTIALLY_REFUNDED` while `0 < refundedAmountCents < paidAmountCents` and to `FULLY_REFUNDED` once `refundedAmountCents === paidAmountCents`.

#### Scenario: Multiple partial refunds exhaust the remaining balance
- **WHEN** an order with `paidAmountCents = 10000` receives a completed refund of `4000` cents and then `6000` cents
- **THEN** the order status SHALL become `PARTIALLY_REFUNDED` after the first refund and `FULLY_REFUNDED` after the second, and any further refund SHALL fail with `409 INVALID_ORDER_STATE` or `422 REFUND_EXCEEDS_REMAINING`

### Requirement: REQ-05 Idempotency Key Replay Safety
`POST /orders/:id/refunds` SHALL require a non-empty `Idempotency-Key` HTTP header. Replaying the same `Idempotency-Key` with an identical payload MUST return the original refund without double-deducting.

#### Scenario: Missing idempotency key is rejected
- **WHEN** a client calls `POST /orders/:id/refunds` without an `Idempotency-Key` header
- **THEN** the system SHALL respond with HTTP `400` and error code `MISSING_IDEMPOTENCY_KEY`

#### Scenario: Network retry replays original refund without double deduction
- **WHEN** a client sends two identical refund requests with the same `Idempotency-Key`
- **THEN** the second response SHALL return the same `refund.id` with `idempotentReplay: true` and the order's `refundedAmountCents` SHALL only reflect a single deduction

### Requirement: REQ-06 Idempotency Payload Conflict Detection
The system SHALL bind each `Idempotency-Key` to a canonical fingerprint of `(orderId, amountCents, reason, actorId)` and reject conflicting reuse.

#### Scenario: Reusing an idempotency key with a different amount
- **WHEN** a client reuses an existing `Idempotency-Key` with a different `amountCents`
- **THEN** the system SHALL reject the request with HTTP `409` and error code `IDEMPOTENCY_CONFLICT`

### Requirement: REQ-07 High-Value Refund Approval Threshold
Any refund request with `amountCents >= 50000` SHALL be created in `PENDING_APPROVAL` status with HTTP `202`, reserving `pendingRefundAmountCents` against `remainingRefundableCents` until approved.

#### Scenario: High-value refund pauses for approval and reserves balance
- **WHEN** a paid order of `80000` cents receives a refund request for `50000` cents
- **THEN** the system SHALL return HTTP `202` with `refund.status = "PENDING_APPROVAL"`, set `pendingRefundAmountCents = 50000`, and reject a subsequent `40000` cent refund with HTTP `422 REFUND_EXCEEDS_REMAINING`

### Requirement: REQ-08 Four-Eyes Human Approval Separation of Duties
`POST /orders/:id/refunds/:refundId/approve` SHALL require an `approverId` distinct from the refund requester's `actorId`.

#### Scenario: Requester attempts self-approval
- **WHEN** the same `actorId` who created a `PENDING_APPROVAL` refund submits `approverId === actorId`
- **THEN** the system SHALL reject the approval with HTTP `403` and error code `SELF_APPROVAL_FORBIDDEN`

#### Scenario: Distinct approver completes pending refund
- **WHEN** a distinct `approverId` approves a `PENDING_APPROVAL` refund
- **THEN** the refund status SHALL become `COMPLETED`, `pendingRefundAmountCents` SHALL decrease by `amountCents`, and `refundedAmountCents` SHALL increase by `amountCents`

### Requirement: REQ-09 Input Validation for Amount, Reason, and Actor
Every refund creation request SHALL validate that `amountCents` is a positive integer, `reason` is a trimmed string of at least 5 characters, and `actorId` is a non-empty string.

#### Scenario: Invalid amount or missing reason rejected with field details
- **WHEN** a client submits `amountCents: -100` or `amountCents: 10.5` or `reason: "bad"`
- **THEN** the system SHALL return HTTP `400` with `error.code = "VALIDATION_ERROR"` and non-empty `error.details`

### Requirement: REQ-10 Immutable Audit Log Trail
The system SHALL record an immutable audit event for every refund creation (`REFUND_COMPLETED` or `REFUND_PENDING_APPROVAL`) and approval (`REFUND_APPROVED`), queryable at `GET /orders/:id/audit-log`.

#### Scenario: Audit trail captures complete refund and approval history
- **WHEN** a high-value refund is requested by `agent-alice` and approved by `manager-bob`
- **THEN** `GET /orders/:id/audit-log` SHALL return both events in chronological order with `actorId`, `amountCents`, `reason`, `refundId`, and ISO-8601 `timestamp`

### Requirement: REQ-11 Consistent API Error Envelope
Every error response across all endpoints SHALL follow `{ "error": { "code": string, "message": string, "details"?: Array<{ field: string, message: string }> } }` and MUST NOT leak stack traces.

#### Scenario: Validation and domain errors share one envelope
- **WHEN** any request fails validation, state guard, conflict, authorization, or cap checks
- **THEN** the response JSON SHALL contain `error.code` and `error.message` matching the standard envelope
