// errors.ts — custom error classes
//
// Convention demonstrated for Copilot: never throw bare Error or strings.
// Every error carries a stable `code` and an HTTP `status` so the API layer can
// translate it into the standard error envelope without leaking internals.

/** Base class for all application errors. */
export abstract class AppError extends Error {
  /** Stable, machine-readable error code (e.g. "NOT_FOUND"). */
  abstract readonly code: string;
  /** HTTP status code this error maps to. */
  abstract readonly status: number;

  protected constructor(message: string) {
    super(message);
    // Preserve the concrete class name in stack traces.
    this.name = new.target.name;
  }
}

/** Thrown when a requested resource does not exist. Maps to HTTP 404. */
export class NotFoundError extends AppError {
  readonly code = "NOT_FOUND";
  readonly status = 404;

  constructor(resource: string, id: string) {
    super(`${resource} with id "${id}" was not found`);
  }
}

/** Thrown when client input fails validation. Maps to HTTP 400. */
export class ValidationError extends AppError {
  readonly code = "VALIDATION_ERROR";
  readonly status = 400;
  readonly details: Array<{ field: string; message: string }>;

  constructor(details: Array<{ field: string; message: string }>) {
    super("One or more fields are invalid");
    this.details = details;
  }
}

/** Thrown when an operation conflicts with current state. Maps to HTTP 409. */
export class ConflictError extends AppError {
  readonly code = "CONFLICT";
  readonly status = 409;

  constructor(message: string) {
    super(message);
  }
}
