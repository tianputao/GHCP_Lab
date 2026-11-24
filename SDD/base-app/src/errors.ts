import type { Response } from 'express';
import type { ApiErrorBody } from './types.js';

export class AppError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details?: Array<{ field: string; message: string }>;

  constructor(
    status: number,
    code: string,
    message: string,
    details?: Array<{ field: string; message: string }>,
  ) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export function sendError(res: Response, err: unknown): void {
  if (err instanceof AppError) {
    const body: ApiErrorBody = {
      error: {
        code: err.code,
        message: err.message,
        ...(err.details ? { details: err.details } : {}),
      },
    };
    res.status(err.status).json(body);
    return;
  }
  res.status(500).json({
    error: { code: 'INTERNAL_ERROR', message: 'An unexpected error occurred' },
  });
}
