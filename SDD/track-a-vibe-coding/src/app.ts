import express from 'express';
import type { Express, Request, Response } from 'express';
import { AppError, sendError } from '../../base-app/src/errors.js';
import type { Order } from '../../base-app/src/types.js';

interface VibeRefund {
  id: string;
  orderId: string;
  amountCents: number;
  status: 'COMPLETED';
  reason?: string;
}

/**
 * Track A — Typical "Vibe Coding" implementation generated from a 1-sentence prompt
 * WITHOUT a formal specification.
 *
 * Notice how plausible it looks at first glance — and its own happy-path test passes!
 * Yet it silently breaks 8+ enterprise invariants (floating-point currency drift,
 * coupon over-refunding, unpaid-order refund, missing idempotency, missing approval
 * threshold, missing four-eyes check, missing audit trail, and ad-hoc error shape).
 */
export function createApp(): Express {
  const app = express();
  app.use(express.json());

  const orders = new Map<string, Order>();
  const refunds: VibeRefund[] = [];
  let orderSeq = 1;
  let refundSeq = 1;

  app.get('/health', (_req: Request, res: Response) => {
    res.status(200).json({ status: 'ok', service: 'order-service-vibe' });
  });

  app.get('/orders', (_req: Request, res: Response) => {
    res.status(200).json({ data: [...orders.values()] });
  });

  app.get('/orders/:id', (req: Request, res: Response) => {
    try {
      const order = orders.get(req.params.id ?? '');
      if (!order) throw new AppError(404, 'NOT_FOUND', `Order ${req.params.id} not found`);
      res.status(200).json(order);
    } catch (err) {
      sendError(res, err);
    }
  });

  app.post('/orders', (req: Request, res: Response) => {
    try {
      const body = (req.body ?? {}) as Record<string, unknown>;
      const customerId = typeof body.customerId === 'string' ? body.customerId.trim() : '';
      const grossAmountCents = Number(body.grossAmountCents);
      const couponDiscountCents = Number(body.couponDiscountCents ?? 0);
      if (!customerId || !Number.isInteger(grossAmountCents) || grossAmountCents <= 0) {
        throw new AppError(400, 'VALIDATION_ERROR', 'Invalid order payload');
      }
      const paidAmountCents = grossAmountCents - couponDiscountCents;
      const id = `ord-${String(orderSeq++).padStart(4, '0')}`;
      const order: Order = {
        id,
        customerId,
        grossAmountCents,
        couponDiscountCents,
        paidAmountCents,
        refundedAmountCents: 0,
        pendingRefundAmountCents: 0,
        remainingRefundableCents: paidAmountCents,
        status: 'PENDING_PAYMENT',
        createdAt: new Date().toISOString(),
      };
      orders.set(id, order);
      res.status(201).json(order);
    } catch (err) {
      sendError(res, err);
    }
  });

  app.post('/orders/:id/pay', (req: Request, res: Response) => {
    try {
      const order = orders.get(req.params.id ?? '');
      if (!order) throw new AppError(404, 'NOT_FOUND', `Order ${req.params.id} not found`);
      if (order.status !== 'PENDING_PAYMENT') {
        throw new AppError(409, 'INVALID_ORDER_STATE', `Cannot pay order in status ${order.status}`);
      }
      order.status = 'PAID';
      res.status(200).json(order);
    } catch (err) {
      sendError(res, err);
    }
  });

  app.post('/orders/:id/cancel', (req: Request, res: Response) => {
    try {
      const order = orders.get(req.params.id ?? '');
      if (!order) throw new AppError(404, 'NOT_FOUND', `Order ${req.params.id} not found`);
      if (order.status !== 'PENDING_PAYMENT') {
        throw new AppError(409, 'INVALID_ORDER_STATE', `Cannot cancel order in status ${order.status}`);
      }
      order.status = 'CANCELLED';
      order.remainingRefundableCents = 0;
      res.status(200).json(order);
    } catch (err) {
      sendError(res, err);
    }
  });

  // ── Vibe-Coded Partial Refund Endpoint (exhibits classic spec-less flaws) ──
  app.post('/orders/:id/refunds', (req: Request, res: Response) => {
    const order = orders.get(req.params.id ?? '');
    if (!order) {
      // Architectural drift: ad-hoc `{ msg }` instead of `{ error: { code, message } }`
      res.status(404).json({ msg: 'order not found' });
      return;
    }

    const body = (req.body ?? {}) as Record<string, unknown>;
    const amountCents = Number(body.amountCents);
    if (!Number.isFinite(amountCents) || amountCents <= 0) {
      // Architectural drift + accepts floats like 10.5!
      res.status(400).json({ msg: 'invalid amount' });
      return;
    }

    // Bug 1: Uses grossAmountCents instead of paidAmountCents (ignores coupon discount!)
    if (order.refundedAmountCents + amountCents > order.grossAmountCents) {
      res.status(400).json({ msg: 'refund exceeds order total' });
      return;
    }

    // Bug 2: Floating-point dollar math introduces IEEE-754 precision drift
    const remainingDollars = order.remainingRefundableCents / 100 - amountCents / 100;
    order.refundedAmountCents = order.refundedAmountCents + amountCents;
    order.remainingRefundableCents = remainingDollars * 100;

    // Bug 3: No state check (refunds PENDING_PAYMENT / CANCELLED orders!)
    // Bug 4: No Idempotency-Key check (network retries double-refund!)
    // Bug 5: No high-value approval threshold (auto-completes >= 50000 cents!)
    // Bug 6: No reason / actorId validation, no immutable audit log!
    order.status =
      order.refundedAmountCents >= order.paidAmountCents ? 'FULLY_REFUNDED' : 'PARTIALLY_REFUNDED';

    const refund: VibeRefund = {
      id: `ref-${String(refundSeq++).padStart(4, '0')}`,
      orderId: order.id,
      amountCents,
      status: 'COMPLETED',
      reason: typeof body.reason === 'string' ? body.reason : undefined,
    };
    refunds.push(refund);

    res.status(201).json({ refund, order });
  });

  return app;
}
