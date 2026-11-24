// http.ts — a tiny, dependency-free HTTP abstraction
//
// The demo avoids a runtime web framework so it type-checks anywhere with zero
// install. These interfaces mirror the shape of an Express request/response
// closely enough that the routing code reads like real Express code — which is
// what matters for the custom-instructions demo.

import { AppError } from "../src/errors";
import type { ApiErrorBody } from "../src/types";

/** An inbound HTTP request. */
export interface ApiRequest<Body = unknown> {
  /** Path parameters, e.g. `{ id: "123" }` for `/tasks/:id`. */
  readonly params: Record<string, string>;
  /** Query-string parameters, e.g. `{ tag: "urgent" }`. */
  readonly query: Record<string, string | undefined>;
  /** Parsed request body. */
  readonly body: Body;
}

/** A fluent response writer. `status().json()` or `status().end()`. */
export interface ApiResponse {
  status(code: number): ApiResponse;
  json(payload: unknown): void;
  /** Ends the response with no body (used for 204). */
  end(): void;
}

/** An async-capable route handler. */
export type RouteHandler<Body = unknown> = (
  req: ApiRequest<Body>,
  res: ApiResponse,
) => Promise<void> | void;

/**
 * Translates any thrown error into the standard {@link ApiErrorBody} envelope.
 * Known {@link AppError}s map to their declared status/code; anything else
 * becomes an opaque 500 so internal details never leak to clients.
 *
 * @param res - the response to write to.
 * @param err - the thrown value.
 */
export function sendError(res: ApiResponse, err: unknown): void {
  if (err instanceof AppError) {
    const body: ApiErrorBody = {
      error: {
        code: err.code,
        message: err.message,
        ...("details" in err ? { details: (err as { details?: ApiErrorBody["error"]["details"] }).details } : {}),
      },
    };
    res.status(err.status).json(body);
    return;
  }
  const body: ApiErrorBody = {
    error: { code: "INTERNAL_ERROR", message: "An unexpected error occurred" },
  };
  res.status(500).json(body);
}
