# Orders Baseline Specification (As-Is)

## Purpose
Define the existing brownfield Order API contract that MUST NOT regress when introducing refund capabilities.

## Requirements

### Requirement: REQ-12 Brownfield Order Lifecycle Preservation
The Order service SHALL preserve existing endpoints (`GET /health`, `GET /orders`, `GET /orders/:id`, `POST /orders`, `POST /orders/:id/pay`, `POST /orders/:id/cancel`) and their standard error envelope `{ error: { code, message, details? } }`.

#### Scenario: Existing order creation and payment remain intact
- **WHEN** a client creates an order with integer `grossAmountCents` and `couponDiscountCents` and calls `POST /orders/:id/pay`
- **THEN** the order transitions from `PENDING_PAYMENT` to `PAID` with `paidAmountCents = grossAmountCents - couponDiscountCents`
