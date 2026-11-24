// types.ts — domain types for the Task API
//
// This file is intentionally small and well-typed so that Copilot has a clean,
// consistent set of examples to follow once the custom instructions are added
// during the Week 7 demo. Keep these tabs open so Copilot sees the conventions.

/** Lifecycle states a task can be in. */
export type TaskStatus = "todo" | "in_progress" | "done";

/** A task owned by a user. Money/time fields use precise primitives, not floats. */
export interface Task {
  /** Stable unique identifier (UUID v4). */
  readonly id: string;
  /** Short human-readable title. Required, 1–200 chars. */
  title: string;
  /** Optional longer description. */
  description: string | null;
  /** Current lifecycle state. */
  status: TaskStatus;
  /** Optional list of free-form tags (added in the Week 7 demo). */
  tags: string[];
  /** Creation timestamp (ISO-8601 string in UTC). */
  readonly createdAt: string;
  /** Last-update timestamp (ISO-8601 string in UTC). */
  updatedAt: string;
}

/** Input accepted when creating a task. The server assigns id/timestamps/status. */
export interface CreateTaskInput {
  title: string;
  description?: string | null;
}

/** Input accepted when updating a task. All fields optional (partial update). */
export interface UpdateTaskInput {
  title?: string;
  description?: string | null;
  status?: TaskStatus;
}

/**
 * The single, consistent API error envelope used by every endpoint.
 * Routes must never leak stack traces or internal details to clients.
 */
export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    /** Optional field-level validation details. */
    details?: Array<{ field: string; message: string }>;
  };
}
