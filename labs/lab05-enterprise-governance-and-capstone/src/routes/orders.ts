import { Router } from 'express';
import type { Request, Response } from 'express';
import { applyDiscount } from '../lib/discount.js';

export interface Order {
  id: number;
  customer: string;
  amount: number;
  discountRule?: string;
}

export function createOrdersRouter(): Router {
  const orders: Order[] = [
    { id: 1, customer: 'Ada Lovelace', amount: 100 },
    { id: 2, customer: 'Alan Turing', amount: 250, discountRule: '10' },
  ];

  const router = Router();

  router.get('/', (_req: Request, res: Response) => {
    const result = orders.map((o) => ({
      ...o,
      total: applyDiscount(o.amount, o.discountRule ?? '0'),
    }));
    res.json(result);
  });

  // ───────────────────────────────────────────────────────────────────────────
  // Lab 05 Capstone · Agent Mode & Governance Exercise
  //
  // TODO: Add a "POST /orders" endpoint that creates a new order.
  //   - Accept { customer: string, amount: number, discountRule?: string }
  //   - Validate: customer non-empty, amount > 0 and <= 1_000_000
  //   - Return 201 with the created order (assign next id)
  //   - Return 400 with a clear error object when validation fails
  //   - Add tests in tests/orders.smoke.test.ts covering happy path & validation errors
  // ───────────────────────────────────────────────────────────────────────────

  return router;
}
