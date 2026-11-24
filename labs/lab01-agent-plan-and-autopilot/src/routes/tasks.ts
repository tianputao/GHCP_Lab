import { Router } from 'express';
import type { Request, Response } from 'express';
import type { TaskStore } from '../store.js';
import type { CreateTaskBody, Task, TaskStatus, UpdateTaskBody } from '../types.js';

const VALID_PRIORITIES: ReadonlySet<string> = new Set(['low', 'medium', 'high']);
const VALID_STATUSES: ReadonlySet<string> = new Set(['todo', 'in_progress', 'done']);

export function createTasksRouter(store: TaskStore): Router {
  const router = Router();

  /**
   * GET /tasks
   * Currently returns all tasks without pagination.
   * Lab 01 Exercise 1: Ask Plan -> Agent/Autopilot to add cursor-based pagination here.
   */
  router.get('/', (_req: Request, res: Response) => {
    const tasks = store.listAll();
    res.status(200).json({ data: tasks, total: tasks.length });
  });

  router.get('/:id', (req: Request, res: Response) => {
    const task = store.findById(req.params.id ?? '');
    if (!task) {
      res.status(404).json({
        error: { code: 'NOT_FOUND', message: `Task ${req.params.id} not found` },
      });
      return;
    }
    res.status(200).json(task);
  });

  router.post('/', (req: Request, res: Response) => {
    const body = (req.body ?? {}) as CreateTaskBody;
    if (typeof body.title !== 'string' || body.title.trim().length === 0) {
      res.status(400).json({
        error: { code: 'VALIDATION_ERROR', message: 'title must be a non-empty string' },
      });
      return;
    }

    const priority = body.priority ?? 'medium';
    if (typeof priority !== 'string' || !VALID_PRIORITIES.has(priority)) {
      res.status(400).json({
        error: { code: 'VALIDATION_ERROR', message: 'priority must be low, medium, or high' },
      });
      return;
    }

    const created = store.create(body.title.trim(), priority as Task['priority']);
    res.status(201).json(created);
  });

  router.patch('/:id', (req: Request, res: Response) => {
    const body = (req.body ?? {}) as UpdateTaskBody;
    const patch: Partial<Pick<Task, 'title' | 'status' | 'priority'>> = {};

    if (body.title !== undefined) {
      if (typeof body.title !== 'string' || body.title.trim().length === 0) {
        res.status(400).json({
          error: { code: 'VALIDATION_ERROR', message: 'title must be a non-empty string' },
        });
        return;
      }
      patch.title = body.title.trim();
    }

    if (body.status !== undefined) {
      if (typeof body.status !== 'string' || !VALID_STATUSES.has(body.status)) {
        res.status(400).json({
          error: { code: 'VALIDATION_ERROR', message: 'status must be todo, in_progress, or done' },
        });
        return;
      }
      patch.status = body.status as TaskStatus;
    }

    if (body.priority !== undefined) {
      if (typeof body.priority !== 'string' || !VALID_PRIORITIES.has(body.priority)) {
        res.status(400).json({
          error: { code: 'VALIDATION_ERROR', message: 'priority must be low, medium, or high' },
        });
        return;
      }
      patch.priority = body.priority as Task['priority'];
    }

    const updated = store.update(req.params.id ?? '', patch);
    if (!updated) {
      res.status(404).json({
        error: { code: 'NOT_FOUND', message: `Task ${req.params.id} not found` },
      });
      return;
    }

    res.status(200).json(updated);
  });

  router.delete('/:id', (req: Request, res: Response) => {
    const removed = store.delete(req.params.id ?? '');
    if (!removed) {
      res.status(404).json({
        error: { code: 'NOT_FOUND', message: `Task ${req.params.id} not found` },
      });
      return;
    }
    res.status(204).end();
  });

  return router;
}
