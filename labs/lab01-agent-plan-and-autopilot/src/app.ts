import express from 'express';
import type { Express, Request, Response } from 'express';
import { TaskStore } from './store.js';
import { createTasksRouter } from './routes/tasks.js';

export function createApp(store = new TaskStore()): Express {
  const app = express();
  app.use(express.json());

  app.get('/health', (_req: Request, res: Response) => {
    res.status(200).json({ status: 'ok', service: 'lab01-task-api' });
  });

  app.use('/tasks', createTasksRouter(store));
  return app;
}
