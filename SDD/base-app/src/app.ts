import express from 'express';
import type { Express, Request, Response } from 'express';
import { AppError, sendError } from './errors.js';
import type { Order } from './types.js';

/**
 * Clean Brownfield Order API (As-Is Baseline).
 * Notice: No refund endpoint exists yet. Copy this folder via `npm run reset:playground`
 * to test Vibe Coding vs SDD hands-on.
 */
export function createApp(): Express {
  const app = express();
  app.use(express.json());

  const orders = new Map<string, Order>();
  let orderSeq = 1;

  app.get('/health', (_req: Request, res: Response) => {
    res.status(200).json({ status: 'ok', service: 'order-service-base' });
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
      const grossAmountCents = body.grossAmountCents;
      const couponDiscountCents = body.couponDiscountCents ?? 0;

      const details: Array<{ field: string; message: string }> = [];
      if (!customerId) details.push({ field: 'customerId', message: 'customerId is required' });
      if (typeof grossAmountCents !== 'number' || !Number.isInteger(grossAmountCents) || grossAmountCents <= 0) {
        details.push({ field: 'grossAmountCents', message: 'grossAmountCents must be a positive integer' });
      }
      if (
        typeof couponDiscountCents !== 'number' ||
        !Number.isInteger(couponDiscountCents) ||
        couponDiscountCents < 0 ||
        (typeof grossAmountCents === 'number' && couponDiscountCents > grossAmountCents)
      ) {
        details.push({
          field: 'couponDiscountCents',
          message: 'couponDiscountCents must be an integer between 0 and grossAmountCents',
        });
      }
      if (details.length > 0) {
        throw new AppError(400, 'VALIDATION_ERROR', 'Invalid order payload', details);
      }

      const paidAmountCents = (grossAmountCents as number) - (couponDiscountCents as number);
      const id = `ord-${String(orderSeq++).padStart(4, '0')}`;
      const order: Order = {
        id,
        customerId,
        grossAmountCents: grossAmountCents as number,
        couponDiscountCents: couponDiscountCents as number,
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

  return app;
}
