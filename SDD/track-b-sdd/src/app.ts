import express from 'express';
import type { Express, Request, Response } from 'express';
import { sendError } from '../../base-app/src/errors.js';
import { RefundService } from './refund-service.js';

/**
 * Track B — Specification-Driven Development (SDD) Implementation.
 * Built strictly from `openspec/changes/add-partial-refund/` (`REQ-01`..`REQ-12`).
 */
export function createApp(service = new RefundService()): Express {
  const app = express();
  app.use(express.json());

  app.get('/health', (_req: Request, res: Response) => {
    res.status(200).json({ status: 'ok', service: 'order-service-sdd' });
  });

  app.get('/orders', (_req: Request, res: Response) => {
    res.status(200).json({ data: service.listOrders() });
  });

  app.get('/orders/:id', (req: Request, res: Response) => {
    try {
      res.status(200).json(service.getOrder(req.params.id ?? ''));
    } catch (err) {
      sendError(res, err);
    }
  });

  app.post('/orders', (req: Request, res: Response) => {
    try {
      const body = (req.body ?? {}) as Record<string, unknown>;
      const created = service.createOrder({
        customerId: body.customerId,
        grossAmountCents: body.grossAmountCents,
        couponDiscountCents: body.couponDiscountCents,
      });
      res.status(201).json(created);
    } catch (err) {
      sendError(res, err);
    }
  });

  app.post('/orders/:id/pay', (req: Request, res: Response) => {
    try {
      res.status(200).json(service.payOrder(req.params.id ?? ''));
    } catch (err) {
      sendError(res, err);
    }
  });

  app.post('/orders/:id/cancel', (req: Request, res: Response) => {
    try {
      res.status(200).json(service.cancelOrder(req.params.id ?? ''));
    } catch (err) {
      sendError(res, err);
    }
  });

  app.post('/orders/:id/refunds', (req: Request, res: Response) => {
    try {
      const body = (req.body ?? {}) as Record<string, unknown>;
      const result = service.requestRefund({
        orderId: req.params.id ?? '',
        idempotencyKey: req.header('Idempotency-Key') ?? undefined,
        amountCents: body.amountCents,
        reason: body.reason,
        actorId: body.actorId,
      });
      res.status(result.statusCode).json(result.body);
    } catch (err) {
      sendError(res, err);
    }
  });

  app.post('/orders/:id/refunds/:refundId/approve', (req: Request, res: Response) => {
    try {
      const body = (req.body ?? {}) as Record<string, unknown>;
      const result = service.approveRefund({
        orderId: req.params.id ?? '',
        refundId: req.params.refundId ?? '',
        approverId: body.approverId,
      });
      res.status(200).json(result);
    } catch (err) {
      sendError(res, err);
    }
  });

  app.get('/orders/:id/audit-log', (req: Request, res: Response) => {
    try {
      res.status(200).json(service.getAuditLog(req.params.id ?? ''));
    } catch (err) {
      sendError(res, err);
    }
  });

  return app;
}
