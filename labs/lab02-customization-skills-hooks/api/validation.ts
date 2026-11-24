// validation.ts — lightweight input validation for the API layer
//
// The demo stays dependency-free, so instead of express-validator we use a small
// hand-rolled validator. The PATTERN is what Copilot should imitate: validate
// every field, collect field-level details, and throw a single ValidationError.

import { ValidationError } from "../src/errors";
import type { CreateTaskInput, UpdateTaskInput, TaskStatus } from "../src/types";

const VALID_STATUSES: readonly TaskStatus[] = ["todo", "in_progress", "done"];
const TITLE_MAX = 200;

type Detail = { field: string; message: string };

/**
 * Validates and narrows an unknown payload into a {@link CreateTaskInput}.
 *
 * @param body - the raw request body.
 * @returns the validated input.
 * @throws {ValidationError} when any field is invalid.
 */
export function validateCreateTask(body: unknown): CreateTaskInput {
  const details: Detail[] = [];
  const data = (body ?? {}) as Record<string, unknown>;

  const title = data["title"];
  if (typeof title !== "string" || title.trim().length === 0) {
    details.push({ field: "title", message: "title is required" });
  } else if (title.length > TITLE_MAX) {
    details.push({ field: "title", message: `title must be <= ${TITLE_MAX} chars` });
  }

  const description = data["description"];
  if (description !== undefined && description !== null && typeof description !== "string") {
    details.push({ field: "description", message: "description must be a string or null" });
  }

  if (details.length > 0) {
    throw new ValidationError(details);
  }

  return {
    title: (title as string).trim(),
    description: (description as string | null | undefined) ?? null,
  };
}

/**
 * Validates and narrows an unknown payload into an {@link UpdateTaskInput}.
 *
 * @param body - the raw request body.
 * @returns the validated input.
 * @throws {ValidationError} when any provided field is invalid.
 */
export function validateUpdateTask(body: unknown): UpdateTaskInput {
  const details: Detail[] = [];
  const data = (body ?? {}) as Record<string, unknown>;
  const result: UpdateTaskInput = {};

  if ("title" in data) {
    const title = data["title"];
    if (typeof title !== "string" || title.trim().length === 0 || title.length > TITLE_MAX) {
      details.push({ field: "title", message: `title must be 1–${TITLE_MAX} chars` });
    } else {
      result.title = title.trim();
    }
  }

  if ("status" in data) {
    const status = data["status"];
    if (typeof status !== "string" || !VALID_STATUSES.includes(status as TaskStatus)) {
      details.push({ field: "status", message: `status must be one of ${VALID_STATUSES.join(", ")}` });
    } else {
      result.status = status as TaskStatus;
    }
  }

  if ("description" in data) {
    const description = data["description"];
    if (description !== null && typeof description !== "string") {
      details.push({ field: "description", message: "description must be a string or null" });
    } else {
      result.description = description as string | null;
    }
  }

  if (details.length > 0) {
    throw new ValidationError(details);
  }
  return result;
}
