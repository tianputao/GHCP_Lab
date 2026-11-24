import express from 'express';
import type { Express, Request, Response } from 'express';
import { createOrdersRouter } from './routes/orders.js';

export function createApp(): Express {
  const app = express();
  app.use(express.json());

  app.get('/health', (_req: Request, res: Response) => {
    res.json({ status: 'ok', service: 'lab05-enterprise-capstone' });
  });

  app.use('/orders', createOrdersRouter());
  return app;
}
