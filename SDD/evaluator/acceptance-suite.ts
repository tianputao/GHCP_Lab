import type { Express } from 'express';
import type { Server } from 'node:http';
import type { AddressInfo } from 'node:net';

export interface RequirementResult {
  id: string;
  title: string;
  category: string;
  passed: boolean;
  detail: string;
}

interface JsonResponse {
  status: number;
  body: Record<string, unknown>;
}

async function httpJson(
  url: string,
  options: { method?: string; headers?: Record<string, string>; body?: unknown } = {},
): Promise<JsonResponse> {
  const res = await fetch(url, {
    method: options.method ?? 'GET',
    headers: {
      ...(options.body !== undefined ? { 'content-type': 'application/json' } : {}),
      ...(options.headers ?? {}),
    },
    ...(options.body !== undefined ? { body: JSON.stringify(options.body) } : {}),
  });
  const text = await res.text();
  let parsed: Record<string, unknown> = {};
  try {
    parsed = text ? (JSON.parse(text) as Record<string, unknown>) : {};
  } catch {
    parsed = { rawText: text };
  }
  return { status: res.status, body: parsed };
}

async function createPaidOrder(
  baseUrl: string,
  grossAmountCents: number,
  couponDiscountCents = 0,
): Promise<{ id: string; paidAmountCents: number }> {
  const created = await httpJson(`${baseUrl}/orders`, {
    method: 'POST',
    body: { customerId: 'cust-eval', grossAmountCents, couponDiscountCents },
  });
  const id = String(created.body.id ?? '');
  await httpJson(`${baseUrl}/orders/${id}/pay`, { method: 'POST' });
  return { id, paidAmountCents: Number(created.body.paidAmountCents) };
}

/**
 * Shared 12-item Enterprise Acceptance Contract (`REQ-01`..`REQ-12`).
 * Executes identical black-box HTTP checks against Track A (Vibe Coding),
 * Track B (SDD), or a student's `playground/` implementation.
 */
export async function runAcceptanceSuite(appFactory: () => Express): Promise<RequirementResult[]> {
  const app = appFactory();
  let server!: Server;
  let baseUrl = '';

  await new Promise<void>((resolve) => {
    server = app.listen(0, () => {
      const addr = server.address() as AddressInfo;
      baseUrl = `http://127.0.0.1:${addr.port}`;
      resolve();
    });
  });

  const results: RequirementResult[] = [];

  async function check(
    id: string,
    title: string,
    category: string,
    fn: () => Promise<string>,
  ): Promise<void> {
    try {
      const detail = await fn();
      results.push({ id, title, category, passed: true, detail });
    } catch (err) {
      results.push({
        id,
        title,
        category,
        passed: false,
        detail: err instanceof Error ? err.message : String(err),
      });
    }
  }

  function expect(cond: boolean, msg: string): void {
    if (!cond) throw new Error(msg);
  }

  try {
    // REQ-01: Integer Cents Monetary Precision
    await check('REQ-01', 'Integer cents precision (no IEEE-754 float drift)', 'Financial Integrity', async () => {
      const order = await createPaidOrder(baseUrl, 1999, 0);
      const r1 = await httpJson(`${baseUrl}/orders/${order.id}/refunds`, {
        method: 'POST',
        headers: { 'Idempotency-Key': 'req01-k1' },
        body: { amountCents: 10, reason: 'Minor packaging damage', actorId: 'agent-1' },
      });
      expect(r1.status === 201, `Expected 201 on first refund, got ${r1.status}`);
      const r2 = await httpJson(`${baseUrl}/orders/${order.id}/refunds`, {
        method: 'POST',
        headers: { 'Idempotency-Key': 'req01-k2' },
        body: { amountCents: 20, reason: 'Additional goodwill credit', actorId: 'agent-1' },
      });
      expect(r2.status === 201, `Expected 201 on second refund, got ${r2.status}`);
      const ord = (r2.body.order ?? {}) as Record<string, unknown>;
      expect(
        ord.remainingRefundableCents === 1969 && Number.isInteger(ord.remainingRefundableCents),
        `Float drift detected: expected exact integer 1969, got ${String(ord.remainingRefundableCents)}`,
      );
      return 'Exact integer remainingRefundableCents = 1969';
    });

    // REQ-02: Coupon-Aware Refundable Cap
    await check('REQ-02', 'Coupon-aware cap (never refund above paidAmountCents)', 'Financial Integrity', async () => {
      const order = await createPaidOrder(baseUrl, 10000, 2000); // paid = 8000
      const res = await httpJson(`${baseUrl}/orders/${order.id}/refunds`, {
        method: 'POST',
        headers: { 'Idempotency-Key': 'req02-k1' },
        body: { amountCents: 9000, reason: 'Attempt refund above net paid', actorId: 'agent-1' },
      });
      const err = (res.body.error ?? {}) as Record<string, unknown>;
      expect(
        res.status === 422 && err.code === 'REFUND_EXCEEDS_REMAINING',
        `Expected 422 REFUND_EXCEEDS_REMAINING, got HTTP ${res.status} (${JSON.stringify(res.body)})`,
      );
      return 'Blocked 9000 refund on 8000 net-paid order (422 REFUND_EXCEEDS_REMAINING)';
    });

    // REQ-03: Order State Machine Guard
    await check('REQ-03', 'State machine blocks refunds on PENDING_PAYMENT / CANCELLED', 'State Machine', async () => {
      const created = await httpJson(`${baseUrl}/orders`, {
        method: 'POST',
        body: { customerId: 'cust-unpaid', grossAmountCents: 5000 },
      });
      const unpaidId = String(created.body.id);
      const res = await httpJson(`${baseUrl}/orders/${unpaidId}/refunds`, {
        method: 'POST',
        headers: { 'Idempotency-Key': 'req03-k1' },
        body: { amountCents: 1000, reason: 'Refund before payment', actorId: 'agent-1' },
      });
      const err = (res.body.error ?? {}) as Record<string, unknown>;
      expect(
        res.status === 409 && err.code === 'INVALID_ORDER_STATE',
        `Expected 409 INVALID_ORDER_STATE on unpaid order, got HTTP ${res.status} (${JSON.stringify(res.body)})`,
      );
      return 'Rejected refund on PENDING_PAYMENT order (409 INVALID_ORDER_STATE)';
    });

    // REQ-04: Cumulative Partial Refund & State Transitions
    await check('REQ-04', 'Cumulative refunds transition PAID -> PARTIALLY_REFUNDED -> FULLY_REFUNDED', 'State Machine', async () => {
      const order = await createPaidOrder(baseUrl, 10000, 0);
      const r1 = await httpJson(`${baseUrl}/orders/${order.id}/refunds`, {
        method: 'POST',
        headers: { 'Idempotency-Key': 'req04-k1' },
        body: { amountCents: 4000, reason: 'First partial refund', actorId: 'agent-1' },
      });
      expect(r1.status === 201, `Expected 201, got ${r1.status}`);
      expect((r1.body.order as Record<string, unknown>)?.status === 'PARTIALLY_REFUNDED', 'Expected PARTIALLY_REFUNDED');

      const r2 = await httpJson(`${baseUrl}/orders/${order.id}/refunds`, {
        method: 'POST',
        headers: { 'Idempotency-Key': 'req04-k2' },
        body: { amountCents: 6000, reason: 'Final remaining refund', actorId: 'agent-1' },
      });
      expect(r2.status === 201, `Expected 201, got ${r2.status}`);
      expect((r2.body.order as Record<string, unknown>)?.status === 'FULLY_REFUNDED', 'Expected FULLY_REFUNDED');

      const r3 = await httpJson(`${baseUrl}/orders/${order.id}/refunds`, {
        method: 'POST',
        headers: { 'Idempotency-Key': 'req04-k3' },
        body: { amountCents: 100, reason: 'Extra refund after full', actorId: 'agent-1' },
      });
      expect(r3.status === 409 || r3.status === 422, `Expected 409/422 after full refund, got ${r3.status}`);
      return 'Transitions verified and post-full-refund blocked';
    });

    // REQ-05: Idempotency Key Replay Safety
    await check('REQ-05', 'Idempotency-Key required & exact retry prevents double refund', 'Idempotency', async () => {
      const order = await createPaidOrder(baseUrl, 10000, 0);
      const missingKey = await httpJson(`${baseUrl}/orders/${order.id}/refunds`, {
        method: 'POST',
        body: { amountCents: 2000, reason: 'No key header', actorId: 'agent-1' },
      });
      const err = (missingKey.body.error ?? {}) as Record<string, unknown>;
      expect(
        missingKey.status === 400 && err.code === 'MISSING_IDEMPOTENCY_KEY',
        `Expected 400 MISSING_IDEMPOTENCY_KEY when header omitted, got HTTP ${missingKey.status}`,
      );

      const first = await httpJson(`${baseUrl}/orders/${order.id}/refunds`, {
        method: 'POST',
        headers: { 'Idempotency-Key': 'req05-retry-key' },
        body: { amountCents: 2000, reason: 'Timeout retry test', actorId: 'agent-1' },
      });
      const second = await httpJson(`${baseUrl}/orders/${order.id}/refunds`, {
        method: 'POST',
        headers: { 'Idempotency-Key': 'req05-retry-key' },
        body: { amountCents: 2000, reason: 'Timeout retry test', actorId: 'agent-1' },
      });
      expect(first.status === 201, `Expected 201 on first call, got ${first.status}`);
      expect(
        second.body.idempotentReplay === true &&
          (second.body.refund as Record<string, unknown>)?.id ===
            (first.body.refund as Record<string, unknown>)?.id &&
          (second.body.order as Record<string, unknown>)?.refundedAmountCents === 2000,
        `Double deduction or missing idempotentReplay flag: ${JSON.stringify(second.body)}`,
      );
      return 'Replay returned original refund without double-deduction';
    });

    // REQ-06: Idempotency Payload Conflict Detection
    await check('REQ-06', 'Reusing Idempotency-Key with different payload returns 409', 'Idempotency', async () => {
      const order = await createPaidOrder(baseUrl, 10000, 0);
      await httpJson(`${baseUrl}/orders/${order.id}/refunds`, {
        method: 'POST',
        headers: { 'Idempotency-Key': 'req06-conflict-key' },
        body: { amountCents: 1000, reason: 'Original request', actorId: 'agent-1' },
      });
      const conflict = await httpJson(`${baseUrl}/orders/${order.id}/refunds`, {
        method: 'POST',
        headers: { 'Idempotency-Key': 'req06-conflict-key' },
        body: { amountCents: 2500, reason: 'Mutated amount with same key', actorId: 'agent-1' },
      });
      const err = (conflict.body.error ?? {}) as Record<string, unknown>;
      expect(
        conflict.status === 409 && err.code === 'IDEMPOTENCY_CONFLICT',
        `Expected 409 IDEMPOTENCY_CONFLICT, got HTTP ${conflict.status} (${JSON.stringify(conflict.body)})`,
      );
      return 'Conflicting payload reuse blocked (409 IDEMPOTENCY_CONFLICT)';
    });

    // REQ-07: High-Value Refund Approval Threshold
    await check('REQ-07', 'High-value refund (>=50000 cents) pauses as 202 PENDING_APPROVAL & reserves funds', 'Governance', async () => {
      const order = await createPaidOrder(baseUrl, 80000, 0);
      const hv = await httpJson(`${baseUrl}/orders/${order.id}/refunds`, {
        method: 'POST',
        headers: { 'Idempotency-Key': 'req07-hv-1' },
        body: { amountCents: 50000, reason: 'Damaged enterprise hardware', actorId: 'agent-alice' },
      });
      expect(
        hv.status === 202 &&
          (hv.body.refund as Record<string, unknown>)?.status === 'PENDING_APPROVAL' &&
          (hv.body.order as Record<string, unknown>)?.pendingRefundAmountCents === 50000,
        `Expected 202 PENDING_APPROVAL reserving 50000 cents, got HTTP ${hv.status} (${JSON.stringify(hv.body)})`,
      );

      // Concurrent/subsequent refund exceeding unreserved remaining (30000) must be rejected
      const over = await httpJson(`${baseUrl}/orders/${order.id}/refunds`, {
        method: 'POST',
        headers: { 'Idempotency-Key': 'req07-hv-2' },
        body: { amountCents: 40000, reason: 'Attempt double drain during pending', actorId: 'agent-alice' },
      });
      expect(over.status === 422, `Expected 422 when exceeding unreserved balance, got ${over.status}`);
      return '202 PENDING_APPROVAL + fund reservation prevented over-drain';
    });

    // REQ-08: Four-Eyes Human Approval Separation of Duties
    await check('REQ-08', 'Four-eyes approval rejects self-approval (403) & completes on distinct approver', 'Governance', async () => {
      const order = await createPaidOrder(baseUrl, 70000, 0);
      const hv = await httpJson(`${baseUrl}/orders/${order.id}/refunds`, {
        method: 'POST',
        headers: { 'Idempotency-Key': 'req08-hv' },
        body: { amountCents: 50000, reason: 'High-value warranty refund', actorId: 'agent-alice' },
      });
      const refundId = String((hv.body.refund as Record<string, unknown>)?.id ?? '');
      expect(hv.status === 202 && refundId.length > 0, `Prerequisite pending refund failed (HTTP ${hv.status})`);

      const selfApprove = await httpJson(`${baseUrl}/orders/${order.id}/refunds/${refundId}/approve`, {
        method: 'POST',
        body: { approverId: 'agent-alice' },
      });
      const selfErr = (selfApprove.body.error ?? {}) as Record<string, unknown>;
      expect(
        selfApprove.status === 403 && selfErr.code === 'SELF_APPROVAL_FORBIDDEN',
        `Expected 403 SELF_APPROVAL_FORBIDDEN, got HTTP ${selfApprove.status}`,
      );

      const managerApprove = await httpJson(`${baseUrl}/orders/${order.id}/refunds/${refundId}/approve`, {
        method: 'POST',
        body: { approverId: 'manager-bob' },
      });
      expect(
        managerApprove.status === 200 &&
          (managerApprove.body.refund as Record<string, unknown>)?.status === 'COMPLETED' &&
          (managerApprove.body.order as Record<string, unknown>)?.refundedAmountCents === 50000,
        `Manager approval failed: HTTP ${managerApprove.status}`,
      );
      return 'Self-approval blocked (403); distinct manager completed refund (200)';
    });

    // REQ-09: Mandatory Reason, Actor & Integer Validation
    await check('REQ-09', 'Strict validation rejects float cents, short reason, missing actorId (400)', 'Input Validation', async () => {
      const order = await createPaidOrder(baseUrl, 10000, 0);
      const bad = await httpJson(`${baseUrl}/orders/${order.id}/refunds`, {
        method: 'POST',
        headers: { 'Idempotency-Key': 'req09-bad' },
        body: { amountCents: 10.5, reason: 'no', actorId: '' },
      });
      const err = (bad.body.error ?? {}) as Record<string, unknown>;
      expect(
        bad.status === 400 &&
          err.code === 'VALIDATION_ERROR' &&
          Array.isArray(err.details) &&
          err.details.length >= 2,
        `Expected 400 VALIDATION_ERROR with field details, got HTTP ${bad.status} (${JSON.stringify(bad.body)})`,
      );
      return 'Rejected float amount, short reason, and empty actorId with field details';
    });

    // REQ-10: Immutable Audit Log Trail
    await check('REQ-10', 'Immutable audit log captures refund creation and approval events', 'Auditability', async () => {
      const order = await createPaidOrder(baseUrl, 60000, 0);
      const hv = await httpJson(`${baseUrl}/orders/${order.id}/refunds`, {
        method: 'POST',
        headers: { 'Idempotency-Key': 'req10-hv' },
        body: { amountCents: 50000, reason: 'Audit compliance check', actorId: 'agent-alice' },
      });
      const refundId = String((hv.body.refund as Record<string, unknown>)?.id ?? '');
      await httpJson(`${baseUrl}/orders/${order.id}/refunds/${refundId}/approve`, {
        method: 'POST',
        body: { approverId: 'manager-bob' },
      });

      const audit = await httpJson(`${baseUrl}/orders/${order.id}/audit-log`);
      const events = Array.isArray(audit.body.events)
        ? (audit.body.events as Array<Record<string, unknown>>)
        : [];
      expect(
        audit.status === 200 &&
          events.length === 2 &&
          events[0]?.eventType === 'REFUND_PENDING_APPROVAL' &&
          events[1]?.eventType === 'REFUND_APPROVED' &&
          events[1]?.actorId === 'manager-bob',
        `Expected 2 structured audit events at GET /orders/:id/audit-log, got HTTP ${audit.status} (${JSON.stringify(audit.body)})`,
      );
      return 'Recorded REFUND_PENDING_APPROVAL -> REFUND_APPROVED in chronological order';
    });

    // REQ-11: Consistent Error Envelope (Anti-Architectural-Drift)
    await check('REQ-11', 'All errors conform to standard { error: { code, message } } envelope', 'Architecture', async () => {
      const notFound = await httpJson(`${baseUrl}/orders/ord-missing/refunds`, {
        method: 'POST',
        headers: { 'Idempotency-Key': 'req11-nf' },
        body: { amountCents: 500, reason: 'Missing order test', actorId: 'agent-1' },
      });
      const err = (notFound.body.error ?? {}) as Record<string, unknown>;
      expect(
        notFound.status === 404 &&
          typeof err.code === 'string' &&
          typeof err.message === 'string',
        `Architectural drift in error format: HTTP ${notFound.status} (${JSON.stringify(notFound.body)})`,
      );
      return 'Standard error envelope preserved across refund endpoints';
    });

    // REQ-12: Brownfield Non-Regression
    await check('REQ-12', 'Existing brownfield Order endpoints remain backward-compatible', 'Non-Regression', async () => {
      const health = await httpJson(`${baseUrl}/health`);
      expect(health.status === 200 && health.body.status === 'ok', 'GET /health failed');

      const order = await httpJson(`${baseUrl}/orders`, {
        method: 'POST',
        body: { customerId: 'cust-legacy', grossAmountCents: 4500, couponDiscountCents: 500 },
      });
      expect(order.status === 201 && order.body.paidAmountCents === 4000, 'POST /orders regressed');
      const cancel = await httpJson(`${baseUrl}/orders/${String(order.body.id)}/cancel`, {
        method: 'POST',
      });
      expect(cancel.status === 200 && cancel.body.status === 'CANCELLED', 'POST /orders/:id/cancel regressed');
      return 'GET /health, POST /orders, POST /cancel intact';
    });
  } finally {
    await new Promise<void>((resolve, reject) => {
      server.close((err) => (err ? reject(err) : resolve()));
    });
  }

  return results;
}
