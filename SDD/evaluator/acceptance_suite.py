"""Shared 12-item Enterprise Acceptance Contract (`REQ-01`..`REQ-12`).

Executes identical black-box HTTP checks against Track A (Vibe Coding),
Track B (SDD), or a student's `playground/` implementation via FastAPI TestClient.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient


@dataclass(frozen=True)
class RequirementResult:
    id: str
    title: str
    category: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class _JsonResponse:
    status: int
    body: dict[str, Any]


def _http_json(
    client: TestClient,
    method: str,
    path: str,
    *,
    headers: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
) -> _JsonResponse:
    res = client.request(method, path, headers=headers, json=body)
    try:
        raw = res.json()
        parsed: dict[str, Any] = raw if isinstance(raw, dict) else {"data": raw}
    except Exception:
        parsed = {"rawText": res.text}
    return _JsonResponse(status=res.status_code, body=parsed)


def _create_paid_order(
    client: TestClient,
    gross_amount_cents: int,
    coupon_discount_cents: int = 0,
) -> tuple[str, int]:
    created = _http_json(
        client,
        "POST",
        "/orders",
        body={
            "customerId": "cust-eval",
            "grossAmountCents": gross_amount_cents,
            "couponDiscountCents": coupon_discount_cents,
        },
    )
    order_id = str(created.body.get("id", ""))
    _http_json(client, "POST", f"/orders/{order_id}/pay")
    return order_id, int(created.body.get("paidAmountCents", 0))


def _expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def _is_exact_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _as_dict(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def run_acceptance_suite(app_factory: Callable[[], FastAPI]) -> list[RequirementResult]:
    """Run all 12 black-box enterprise acceptance contracts against a FastAPI app."""
    client = TestClient(app_factory())
    results: list[RequirementResult] = []

    def check(req_id: str, title: str, category: str, fn: Callable[[], str]) -> None:
        try:
            detail = fn()
            results.append(RequirementResult(req_id, title, category, True, detail))
        except Exception as err:
            results.append(RequirementResult(req_id, title, category, False, str(err)))

    # REQ-01: Integer Cents Monetary Precision
    def check_req01() -> str:
        order_id, _ = _create_paid_order(client, 1999, 0)
        r1 = _http_json(
            client,
            "POST",
            f"/orders/{order_id}/refunds",
            headers={"Idempotency-Key": "req01-k1"},
            body={"amountCents": 10, "reason": "Minor packaging damage", "actorId": "agent-1"},
        )
        _expect(r1.status == 201, f"Expected 201 on first refund, got {r1.status}")
        r2 = _http_json(
            client,
            "POST",
            f"/orders/{order_id}/refunds",
            headers={"Idempotency-Key": "req01-k2"},
            body={"amountCents": 20, "reason": "Additional goodwill credit", "actorId": "agent-1"},
        )
        _expect(r2.status == 201, f"Expected 201 on second refund, got {r2.status}")
        ord_data = r2.body.get("order") or {}
        rem = ord_data.get("remainingRefundableCents") if isinstance(ord_data, dict) else None
        _expect(
            _is_exact_int(rem) and rem == 1969,
            f"Float drift detected: expected exact integer 1969, got {rem!r}",
        )
        return "Exact integer remainingRefundableCents = 1969"

    check("REQ-01", "Integer cents precision (no IEEE-754 float drift)", "Financial Integrity", check_req01)

    # REQ-02: Coupon-Aware Refundable Cap
    def check_req02() -> str:
        order_id, _ = _create_paid_order(client, 10000, 2000)  # paid = 8000
        res = _http_json(
            client,
            "POST",
            f"/orders/{order_id}/refunds",
            headers={"Idempotency-Key": "req02-k1"},
            body={"amountCents": 9000, "reason": "Attempt refund above net paid", "actorId": "agent-1"},
        )
        err = _as_dict(res.body.get("error"))
        _expect(
            res.status == 422 and err.get("code") == "REFUND_EXCEEDS_REMAINING",
            f"Expected 422 REFUND_EXCEEDS_REMAINING, got HTTP {res.status} ({res.body})",
        )
        return "Blocked 9000 refund on 8000 net-paid order (422 REFUND_EXCEEDS_REMAINING)"

    check("REQ-02", "Coupon-aware cap (never refund above paidAmountCents)", "Financial Integrity", check_req02)

    # REQ-03: Order State Machine Guard
    def check_req03() -> str:
        created = _http_json(
            client,
            "POST",
            "/orders",
            body={"customerId": "cust-unpaid", "grossAmountCents": 5000},
        )
        unpaid_id = str(created.body.get("id", ""))
        res = _http_json(
            client,
            "POST",
            f"/orders/{unpaid_id}/refunds",
            headers={"Idempotency-Key": "req03-k1"},
            body={"amountCents": 1000, "reason": "Refund before payment", "actorId": "agent-1"},
        )
        err = _as_dict(res.body.get("error"))
        _expect(
            res.status == 409 and err.get("code") == "INVALID_ORDER_STATE",
            f"Expected 409 INVALID_ORDER_STATE on unpaid order, got HTTP {res.status} ({res.body})",
        )
        return "Rejected refund on PENDING_PAYMENT order (409 INVALID_ORDER_STATE)"

    check("REQ-03", "State machine blocks refunds on PENDING_PAYMENT / CANCELLED", "State Machine", check_req03)

    # REQ-04: Cumulative Partial Refund & State Transitions
    def check_req04() -> str:
        order_id, _ = _create_paid_order(client, 10000, 0)
        r1 = _http_json(
            client,
            "POST",
            f"/orders/{order_id}/refunds",
            headers={"Idempotency-Key": "req04-k1"},
            body={"amountCents": 4000, "reason": "First partial refund", "actorId": "agent-1"},
        )
        _expect(r1.status == 201, f"Expected 201, got {r1.status}")
        _expect(r1.body.get("order", {}).get("status") == "PARTIALLY_REFUNDED", "Expected PARTIALLY_REFUNDED")

        r2 = _http_json(
            client,
            "POST",
            f"/orders/{order_id}/refunds",
            headers={"Idempotency-Key": "req04-k2"},
            body={"amountCents": 6000, "reason": "Final remaining refund", "actorId": "agent-1"},
        )
        _expect(r2.status == 201, f"Expected 201, got {r2.status}")
        _expect(r2.body.get("order", {}).get("status") == "FULLY_REFUNDED", "Expected FULLY_REFUNDED")

        r3 = _http_json(
            client,
            "POST",
            f"/orders/{order_id}/refunds",
            headers={"Idempotency-Key": "req04-k3"},
            body={"amountCents": 100, "reason": "Extra refund after full", "actorId": "agent-1"},
        )
        _expect(r3.status in (409, 422), f"Expected 409/422 after full refund, got {r3.status}")
        return "Transitions verified and post-full-refund blocked"

    check(
        "REQ-04",
        "Cumulative refunds transition PAID -> PARTIALLY_REFUNDED -> FULLY_REFUNDED",
        "State Machine",
        check_req04,
    )

    # REQ-05: Idempotency Key Replay Safety
    def check_req05() -> str:
        order_id, _ = _create_paid_order(client, 10000, 0)
        missing_key = _http_json(
            client,
            "POST",
            f"/orders/{order_id}/refunds",
            body={"amountCents": 2000, "reason": "No key header", "actorId": "agent-1"},
        )
        err = _as_dict(missing_key.body.get("error"))
        _expect(
            missing_key.status == 400 and err.get("code") == "MISSING_IDEMPOTENCY_KEY",
            f"Expected 400 MISSING_IDEMPOTENCY_KEY when header omitted, got HTTP {missing_key.status}",
        )

        first = _http_json(
            client,
            "POST",
            f"/orders/{order_id}/refunds",
            headers={"Idempotency-Key": "req05-retry-key"},
            body={"amountCents": 2000, "reason": "Timeout retry test", "actorId": "agent-1"},
        )
        second = _http_json(
            client,
            "POST",
            f"/orders/{order_id}/refunds",
            headers={"Idempotency-Key": "req05-retry-key"},
            body={"amountCents": 2000, "reason": "Timeout retry test", "actorId": "agent-1"},
        )
        _expect(first.status == 201, f"Expected 201 on first call, got {first.status}")
        _expect(
            second.body.get("idempotentReplay") is True
            and second.body.get("refund", {}).get("id") == first.body.get("refund", {}).get("id")
            and second.body.get("order", {}).get("refundedAmountCents") == 2000,
            f"Double deduction or missing idempotentReplay flag: {second.body}",
        )
        return "Replay returned original refund without double-deduction"

    check("REQ-05", "Idempotency-Key required & exact retry prevents double refund", "Idempotency", check_req05)

    # REQ-06: Idempotency Payload Conflict Detection
    def check_req06() -> str:
        order_id, _ = _create_paid_order(client, 10000, 0)
        _http_json(
            client,
            "POST",
            f"/orders/{order_id}/refunds",
            headers={"Idempotency-Key": "req06-conflict-key"},
            body={"amountCents": 1000, "reason": "Original request", "actorId": "agent-1"},
        )
        conflict = _http_json(
            client,
            "POST",
            f"/orders/{order_id}/refunds",
            headers={"Idempotency-Key": "req06-conflict-key"},
            body={"amountCents": 2500, "reason": "Mutated amount with same key", "actorId": "agent-1"},
        )
        err = _as_dict(conflict.body.get("error"))
        _expect(
            conflict.status == 409 and err.get("code") == "IDEMPOTENCY_CONFLICT",
            f"Expected 409 IDEMPOTENCY_CONFLICT, got HTTP {conflict.status} ({conflict.body})",
        )
        return "Conflicting payload reuse blocked (409 IDEMPOTENCY_CONFLICT)"

    check("REQ-06", "Reusing Idempotency-Key with different payload returns 409", "Idempotency", check_req06)

    # REQ-07: High-Value Refund Approval Threshold
    def check_req07() -> str:
        order_id, _ = _create_paid_order(client, 80000, 0)
        hv = _http_json(
            client,
            "POST",
            f"/orders/{order_id}/refunds",
            headers={"Idempotency-Key": "req07-hv-1"},
            body={"amountCents": 50000, "reason": "Damaged enterprise hardware", "actorId": "agent-alice"},
        )
        _expect(
            hv.status == 202
            and hv.body.get("refund", {}).get("status") == "PENDING_APPROVAL"
            and hv.body.get("order", {}).get("pendingRefundAmountCents") == 50000,
            f"Expected 202 PENDING_APPROVAL reserving 50000 cents, got HTTP {hv.status} ({hv.body})",
        )

        over = _http_json(
            client,
            "POST",
            f"/orders/{order_id}/refunds",
            headers={"Idempotency-Key": "req07-hv-2"},
            body={"amountCents": 40000, "reason": "Attempt double drain during pending", "actorId": "agent-alice"},
        )
        _expect(over.status == 422, f"Expected 422 when exceeding unreserved balance, got {over.status}")
        return "202 PENDING_APPROVAL + fund reservation prevented over-drain"

    check(
        "REQ-07",
        "High-value refund (>=50000 cents) pauses as 202 PENDING_APPROVAL & reserves funds",
        "Governance",
        check_req07,
    )

    # REQ-08: Four-Eyes Human Approval Separation of Duties
    def check_req08() -> str:
        order_id, _ = _create_paid_order(client, 70000, 0)
        hv = _http_json(
            client,
            "POST",
            f"/orders/{order_id}/refunds",
            headers={"Idempotency-Key": "req08-hv"},
            body={"amountCents": 50000, "reason": "High-value warranty refund", "actorId": "agent-alice"},
        )
        refund_id = str(hv.body.get("refund", {}).get("id", ""))
        _expect(hv.status == 202 and len(refund_id) > 0, f"Prerequisite pending refund failed (HTTP {hv.status})")

        self_approve = _http_json(
            client,
            "POST",
            f"/orders/{order_id}/refunds/{refund_id}/approve",
            body={"approverId": "agent-alice"},
        )
        self_err = _as_dict(self_approve.body.get("error"))
        _expect(
            self_approve.status == 403 and self_err.get("code") == "SELF_APPROVAL_FORBIDDEN",
            f"Expected 403 SELF_APPROVAL_FORBIDDEN, got HTTP {self_approve.status}",
        )

        manager_approve = _http_json(
            client,
            "POST",
            f"/orders/{order_id}/refunds/{refund_id}/approve",
            body={"approverId": "manager-bob"},
        )
        _expect(
            manager_approve.status == 200
            and manager_approve.body.get("refund", {}).get("status") == "COMPLETED"
            and manager_approve.body.get("order", {}).get("refundedAmountCents") == 50000,
            f"Manager approval failed: HTTP {manager_approve.status}",
        )
        return "Self-approval blocked (403); distinct manager completed refund (200)"

    check(
        "REQ-08",
        "Four-eyes approval rejects self-approval (403) & completes on distinct approver",
        "Governance",
        check_req08,
    )

    # REQ-09: Mandatory Reason, Actor & Integer Validation
    def check_req09() -> str:
        order_id, _ = _create_paid_order(client, 10000, 0)
        bad = _http_json(
            client,
            "POST",
            f"/orders/{order_id}/refunds",
            headers={"Idempotency-Key": "req09-bad"},
            body={"amountCents": 10.5, "reason": "no", "actorId": ""},
        )
        err = _as_dict(bad.body.get("error"))
        details = err.get("details")
        _expect(
            bad.status == 400
            and err.get("code") == "VALIDATION_ERROR"
            and isinstance(details, list)
            and len(details) >= 2,
            f"Expected 400 VALIDATION_ERROR with field details, got HTTP {bad.status} ({bad.body})",
        )
        return "Rejected float amount, short reason, and empty actorId with field details"

    check(
        "REQ-09",
        "Strict validation rejects float cents, short reason, missing actorId (400)",
        "Input Validation",
        check_req09,
    )

    # REQ-10: Immutable Audit Log Trail
    def check_req10() -> str:
        order_id, _ = _create_paid_order(client, 60000, 0)
        hv = _http_json(
            client,
            "POST",
            f"/orders/{order_id}/refunds",
            headers={"Idempotency-Key": "req10-hv"},
            body={"amountCents": 50000, "reason": "Audit compliance check", "actorId": "agent-alice"},
        )
        refund_id = str(hv.body.get("refund", {}).get("id", ""))
        _http_json(
            client,
            "POST",
            f"/orders/{order_id}/refunds/{refund_id}/approve",
            body={"approverId": "manager-bob"},
        )

        audit = _http_json(client, "GET", f"/orders/{order_id}/audit-log")
        events = _as_list(audit.body.get("events"))
        _expect(
            audit.status == 200
            and len(events) == 2
            and _as_dict(events[0]).get("eventType") == "REFUND_PENDING_APPROVAL"
            and _as_dict(events[1]).get("eventType") == "REFUND_APPROVED"
            and _as_dict(events[1]).get("actorId") == "manager-bob",
            f"Expected 2 structured audit events at GET /orders/:id/audit-log, got HTTP {audit.status} ({audit.body})",
        )
        return "Recorded REFUND_PENDING_APPROVAL -> REFUND_APPROVED in chronological order"

    check("REQ-10", "Immutable audit log captures refund creation and approval events", "Auditability", check_req10)

    # REQ-11: Consistent Error Envelope (Anti-Architectural-Drift)
    def check_req11() -> str:
        not_found = _http_json(
            client,
            "POST",
            "/orders/ord-missing/refunds",
            headers={"Idempotency-Key": "req11-nf"},
            body={"amountCents": 500, "reason": "Missing order test", "actorId": "agent-1"},
        )
        err = _as_dict(not_found.body.get("error"))
        _expect(
            not_found.status == 404
            and isinstance(err.get("code"), str)
            and isinstance(err.get("message"), str),
            f"Architectural drift in error format: HTTP {not_found.status} ({not_found.body})",
        )
        return "Standard error envelope preserved across refund endpoints"

    check("REQ-11", "All errors conform to standard { error: { code, message } } envelope", "Architecture", check_req11)

    # REQ-12: Brownfield Non-Regression
    def check_req12() -> str:
        health = _http_json(client, "GET", "/health")
        _expect(health.status == 200 and health.body.get("status") == "ok", "GET /health failed")

        order = _http_json(
            client,
            "POST",
            "/orders",
            body={"customerId": "cust-legacy", "grossAmountCents": 4500, "couponDiscountCents": 500},
        )
        _expect(order.status == 201 and order.body.get("paidAmountCents") == 4000, "POST /orders regressed")
        cancel = _http_json(client, "POST", f"/orders/{order.body.get('id')}/cancel")
        _expect(cancel.status == 200 and cancel.body.get("status") == "CANCELLED", "POST /orders/:id/cancel regressed")
        return "GET /health, POST /orders, POST /cancel intact"

    check("REQ-12", "Existing brownfield Order endpoints remain backward-compatible", "Non-Regression", check_req12)

    return results
