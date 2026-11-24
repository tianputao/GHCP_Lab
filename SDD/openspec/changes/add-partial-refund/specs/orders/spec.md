# Spec Delta: Orders Capability

## MODIFIED Requirements

### Requirement: REQ-12 Brownfield Order Lifecycle Preservation
The Order service SHALL preserve existing endpoints (`GET /health`, `GET /orders`, `GET /orders/:id`, `POST /orders`, `POST /orders/:id/pay`, `POST /orders/:id/cancel`) and extend order statuses with `PARTIALLY_REFUNDED` and `FULLY_REFUNDED` while keeping the standard error envelope `{ error: { code, message, details? } }`.

#### Scenario: Existing order creation and payment remain intact
- **WHEN** a client creates an order with integer `grossAmountCents` and `couponDiscountCents` and calls `POST /orders/:id/pay`
- **THEN** the order transitions from `PENDING_PAYMENT` to `PAID` with `paidAmountCents = grossAmountCents - couponDiscountCents`

#### Scenario: Order cancellation and refund statuses remain backward-compatible
- **WHEN** a client cancels an unpaid order via `POST /orders/:id/cancel` or inspects a refunded order via `GET /orders/:id`
- **THEN** the endpoints SHALL return the standard JSON envelope and valid lifecycle state without breaking existing fields
