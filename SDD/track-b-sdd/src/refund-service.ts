import { createHash } from 'node:crypto';
import { AppError } from '../../base-app/src/errors.js';
import type { Order } from '../../base-app/src/types.js';
import type { AuditEvent, RefundRecord, RefundResponsePayload } from './types.js';

export const HIGH_VALUE_APPROVAL_THRESHOLD_CENTS = 50_000;

interface IdempotencyEntry {
  fingerprint: string;
  statusCode: number;
  refundId: string;
}

/**
 * Spec-Driven Partial Refund Ledger Service implementing REQ-01..REQ-12
 * from `openspec/changes/add-partial-refund/specs/refunds/spec.md`.
 */
export class RefundService {
  private readonly orders = new Map<string, Order>();
  private readonly refunds = new Map<string, RefundRecord>();
  private readonly auditLogs = new Map<string, AuditEvent[]>();
  private readonly idempotencyStore = new Map<string, IdempotencyEntry>();
  private orderSeq = 1;
  private refundSeq = 1;
  private auditSeq = 1;

  listOrders(): Order[] {
    return [...this.orders.values()].map((o) => ({ ...o }));
  }

  getOrder(orderId: string): Order {
    const order = this.orders.get(orderId);
    if (!order) {
      throw new AppError(404, 'NOT_FOUND', `Order ${orderId} not found`);
    }
    return { ...order };
  }

  createOrder(input: {
    customerId: unknown;
    grossAmountCents: unknown;
    couponDiscountCents?: unknown;
  }): Order {
    const customerId = typeof input.customerId === 'string' ? input.customerId.trim() : '';
    const gross = input.grossAmountCents;
    const discount = input.couponDiscountCents ?? 0;

    const details: Array<{ field: string; message: string }> = [];
    if (!customerId) details.push({ field: 'customerId', message: 'customerId is required' });
    if (typeof gross !== 'number' || !Number.isInteger(gross) || gross <= 0) {
      details.push({ field: 'grossAmountCents', message: 'grossAmountCents must be a positive integer' });
    }
    if (
      typeof discount !== 'number' ||
      !Number.isInteger(discount) ||
      discount < 0 ||
      (typeof gross === 'number' && discount > gross)
    ) {
      details.push({
        field: 'couponDiscountCents',
        message: 'couponDiscountCents must be an integer between 0 and grossAmountCents',
      });
    }
    if (details.length > 0) {
      throw new AppError(400, 'VALIDATION_ERROR', 'Invalid order payload', details);
    }

    const paidAmountCents = (gross as number) - (discount as number);
    const id = `ord-${String(this.orderSeq++).padStart(4, '0')}`;
    const order: Order = {
      id,
      customerId,
      grossAmountCents: gross as number,
      couponDiscountCents: discount as number,
      paidAmountCents,
      refundedAmountCents: 0,
      pendingRefundAmountCents: 0,
      remainingRefundableCents: paidAmountCents,
      status: 'PENDING_PAYMENT',
      createdAt: new Date().toISOString(),
    };
    this.orders.set(id, order);
    this.auditLogs.set(id, []);
    return { ...order };
  }

  payOrder(orderId: string): Order {
    const order = this.requireMutableOrder(orderId);
    if (order.status !== 'PENDING_PAYMENT') {
      throw new AppError(409, 'INVALID_ORDER_STATE', `Cannot pay order in status ${order.status}`);
    }
    order.status = 'PAID';
    return { ...order };
  }

  cancelOrder(orderId: string): Order {
    const order = this.requireMutableOrder(orderId);
    if (order.status !== 'PENDING_PAYMENT') {
      throw new AppError(409, 'INVALID_ORDER_STATE', `Cannot cancel order in status ${order.status}`);
    }
    order.status = 'CANCELLED';
    order.remainingRefundableCents = 0;
    return { ...order };
  }

  /**
   * Implements REQ-01..REQ-07, REQ-09, REQ-10, REQ-11.
   */
  requestRefund(input: {
    orderId: string;
    idempotencyKey: string | undefined;
    amountCents: unknown;
    reason: unknown;
    actorId: unknown;
  }): { statusCode: number; body: RefundResponsePayload } {
    // REQ-05: Mandatory Idempotency-Key header
    const key = (input.idempotencyKey ?? '').trim();
    if (!key) {
      throw new AppError(
        400,
        'MISSING_IDEMPOTENCY_KEY',
        'Idempotency-Key header is required for refund requests',
      );
    }

    // REQ-01 & REQ-09: Strict integer cents + reason + actorId validation
    const details: Array<{ field: string; message: string }> = [];
    const amount = input.amountCents;
    if (typeof amount !== 'number' || !Number.isInteger(amount) || amount <= 0) {
      details.push({
        field: 'amountCents',
        message: 'amountCents must be a positive integer in cents',
      });
    }
    const reason = typeof input.reason === 'string' ? input.reason.trim() : '';
    if (reason.length < 5) {
      details.push({
        field: 'reason',
        message: 'reason must be at least 5 non-whitespace characters',
      });
    }
    const actorId = typeof input.actorId === 'string' ? input.actorId.trim() : '';
    if (!actorId) {
      details.push({ field: 'actorId', message: 'actorId is required' });
    }
    if (details.length > 0) {
      throw new AppError(400, 'VALIDATION_ERROR', 'Invalid refund payload', details);
    }

    const order = this.requireMutableOrder(input.orderId);

    // REQ-05 & REQ-06: Idempotency replay & canonical fingerprint conflict check
    const fingerprint = this.computeFingerprint({
      orderId: order.id,
      amountCents: amount as number,
      reason,
      actorId,
    });
    const existingEntry = this.idempotencyStore.get(key);
    if (existingEntry) {
      if (existingEntry.fingerprint !== fingerprint) {
        throw new AppError(
          409,
          'IDEMPOTENCY_CONFLICT',
          `Idempotency-Key "${key}" was already used with a different refund payload`,
        );
      }
      const existingRefund = this.refunds.get(existingEntry.refundId);
      if (!existingRefund) {
        throw new AppError(500, 'INTERNAL_ERROR', 'Idempotency record references missing refund');
      }
      return {
        statusCode: 200,
        body: {
          refund: { ...existingRefund },
          order: { ...order },
          idempotentReplay: true,
        },
      };
    }

    // REQ-03: Order state machine guard
    if (order.status !== 'PAID' && order.status !== 'PARTIALLY_REFUNDED') {
      throw new AppError(
        409,
        'INVALID_ORDER_STATE',
        `Refunds are only allowed for PAID or PARTIALLY_REFUNDED orders (current: ${order.status})`,
      );
    }

    // REQ-01, REQ-02, REQ-04, REQ-07: Coupon-aware remaining refundable balance in exact integer cents
    const currentRemaining =
      order.paidAmountCents - order.refundedAmountCents - order.pendingRefundAmountCents;
    if ((amount as number) > currentRemaining) {
      throw new AppError(
        422,
        'REFUND_EXCEEDS_REMAINING',
        `Requested ${amount} cents exceeds remaining refundable balance of ${currentRemaining} cents`,
      );
    }

    const now = new Date().toISOString();
    const refundId = `ref-${String(this.refundSeq++).padStart(4, '0')}`;
    const requiresApproval = (amount as number) >= HIGH_VALUE_APPROVAL_THRESHOLD_CENTS;

    const refund: RefundRecord = {
      id: refundId,
      orderId: order.id,
      amountCents: amount as number,
      reason,
      actorId,
      status: requiresApproval ? 'PENDING_APPROVAL' : 'COMPLETED',
      idempotencyKey: key,
      createdAt: now,
      ...(requiresApproval ? {} : { completedAt: now }),
    };

    if (requiresApproval) {
      // REQ-07: Reserve pending amount so subsequent requests cannot over-refund
      order.pendingRefundAmountCents += amount as number;
      order.remainingRefundableCents =
        order.paidAmountCents - order.refundedAmountCents - order.pendingRefundAmountCents;
    } else {
      // REQ-01 & REQ-04: Exact integer accounting & status transitions
      order.refundedAmountCents += amount as number;
      order.remainingRefundableCents =
        order.paidAmountCents - order.refundedAmountCents - order.pendingRefundAmountCents;
      order.status =
        order.refundedAmountCents === order.paidAmountCents
          ? 'FULLY_REFUNDED'
          : 'PARTIALLY_REFUNDED';
    }

    this.refunds.set(refundId, refund);
    const statusCode = requiresApproval ? 202 : 201;
    this.idempotencyStore.set(key, { fingerprint, statusCode, refundId });

    // REQ-10: Append immutable audit log event
    this.appendAudit({
      eventType: requiresApproval ? 'REFUND_PENDING_APPROVAL' : 'REFUND_COMPLETED',
      orderId: order.id,
      refundId,
      actorId,
      amountCents: amount as number,
      reason,
      timestamp: now,
    });

    return {
      statusCode,
      body: {
        refund: { ...refund },
        order: { ...order },
        idempotentReplay: false,
      },
    };
  }

  /**
   * Implements REQ-08 & REQ-10: Four-eyes human approval for high-value pending refunds.
   */
  approveRefund(input: {
    orderId: string;
    refundId: string;
    approverId: unknown;
  }): { refund: RefundRecord; order: Order } {
    const approverId = typeof input.approverId === 'string' ? input.approverId.trim() : '';
    if (!approverId) {
      throw new AppError(400, 'VALIDATION_ERROR', 'approverId is required', [
        { field: 'approverId', message: 'approverId must be a non-empty string' },
      ]);
    }

    const order = this.requireMutableOrder(input.orderId);
    const refund = this.refunds.get(input.refundId);
    if (!refund || refund.orderId !== order.id) {
      throw new AppError(404, 'NOT_FOUND', `Refund ${input.refundId} not found for order ${order.id}`);
    }

    if (refund.status !== 'PENDING_APPROVAL') {
      throw new AppError(
        409,
        'INVALID_REFUND_STATE',
        `Refund ${refund.id} is already in status ${refund.status}`,
      );
    }

    // REQ-08: Separation of duties (Four-Eyes principle)
    if (approverId === refund.actorId) {
      throw new AppError(
        403,
        'SELF_APPROVAL_FORBIDDEN',
        'Refund requester cannot approve their own high-value refund',
      );
    }

    const now = new Date().toISOString();
    refund.status = 'COMPLETED';
    refund.approverId = approverId;
    refund.completedAt = now;

    order.pendingRefundAmountCents -= refund.amountCents;
    order.refundedAmountCents += refund.amountCents;
    order.remainingRefundableCents =
      order.paidAmountCents - order.refundedAmountCents - order.pendingRefundAmountCents;
    order.status =
      order.refundedAmountCents === order.paidAmountCents ? 'FULLY_REFUNDED' : 'PARTIALLY_REFUNDED';

    this.appendAudit({
      eventType: 'REFUND_APPROVED',
      orderId: order.id,
      refundId: refund.id,
      actorId: approverId,
      amountCents: refund.amountCents,
      reason: `Approved refund: ${refund.reason}`,
      timestamp: now,
    });

    return {
      refund: { ...refund },
      order: { ...order },
    };
  }

  getAuditLog(orderId: string): { orderId: string; events: AuditEvent[] } {
    this.requireMutableOrder(orderId);
    const events = this.auditLogs.get(orderId) ?? [];
    return {
      orderId,
      events: events.map((e) => ({ ...e })),
    };
  }

  private requireMutableOrder(orderId: string): Order {
    const order = this.orders.get(orderId);
    if (!order) {
      throw new AppError(404, 'NOT_FOUND', `Order ${orderId} not found`);
    }
    return order;
  }

  private computeFingerprint(payload: {
    orderId: string;
    amountCents: number;
    reason: string;
    actorId: string;
  }): string {
    return createHash('sha256').update(JSON.stringify(payload)).digest('hex');
  }

  private appendAudit(event: Omit<AuditEvent, 'id'>): void {
    const list = this.auditLogs.get(event.orderId) ?? [];
    list.push({
      id: `aud-${String(this.auditSeq++).padStart(4, '0')}`,
      ...event,
    });
    this.auditLogs.set(event.orderId, list);
  }
}
