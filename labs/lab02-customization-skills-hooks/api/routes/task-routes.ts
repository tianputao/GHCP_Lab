// task-routes.ts — RESTful task endpoints (the API-layer "good example")
//
// Conventions demonstrated for Copilot (these mirror api.instructions.md):
//   - async handlers wrapped in try/catch
//   - every input validated before use
//   - correct status codes: POST→201, GET→200, PUT→200, DELETE→204, not-found→404
//   - all errors funnelled through sendError() into the standard envelope
//   - no direct DB access — everything goes through TaskRepository

import { TaskRepository } from "../../src/repositories/task-repository";
import { sendError } from "../http";
import type { ApiRequest, ApiResponse, RouteHandler } from "../http";
import { validateCreateTask, validateUpdateTask } from "../validation";

/** A registered route: method + path pattern + handler. */
export interface Route {
  method: "GET" | "POST" | "PUT" | "DELETE";
  path: string;
  handler: RouteHandler;
}

/**
 * Builds the task routes against a given repository.
 *
 * @param repo - the task repository (injected for testability).
 * @returns the list of routes to register.
 */
export function createTaskRoutes(repo: TaskRepository): Route[] {
  /** GET /tasks?tag=urgent → 200 with the (optionally filtered) task list. */
  const list: RouteHandler = (req: ApiRequest, res: ApiResponse) => {
    try {
      const tag = req.query["tag"];
      res.status(200).json(repo.findAll(tag));
    } catch (err) {
      sendError(res, err);
    }
  };

  /** GET /tasks/:id → 200 with the task, or 404 if it does not exist. */
  const getOne: RouteHandler = (req: ApiRequest, res: ApiResponse) => {
    try {
      res.status(200).json(repo.getById(req.params["id"] ?? ""));
    } catch (err) {
      sendError(res, err);
    }
  };

  /** POST /tasks → 201 with the created task. */
  const create: RouteHandler = (req: ApiRequest, res: ApiResponse) => {
    try {
      const input = validateCreateTask(req.body);
      res.status(201).json(repo.create(input));
    } catch (err) {
      sendError(res, err);
    }
  };

  /** PUT /tasks/:id → 200 with the updated task, or 404 if it does not exist. */
  const update: RouteHandler = (req: ApiRequest, res: ApiResponse) => {
    try {
      const input = validateUpdateTask(req.body);
      res.status(200).json(repo.update(req.params["id"] ?? "", input));
    } catch (err) {
      sendError(res, err);
    }
  };

  /** DELETE /tasks/:id → 204 with no body, or 404 if it does not exist. */
  const remove: RouteHandler = (req: ApiRequest, res: ApiResponse) => {
    try {
      repo.delete(req.params["id"] ?? "");
      res.status(204).end();
    } catch (err) {
      sendError(res, err);
    }
  };

  return [
    { method: "GET", path: "/tasks", handler: list },
    { method: "GET", path: "/tasks/:id", handler: getOne },
    { method: "POST", path: "/tasks", handler: create },
    { method: "PUT", path: "/tasks/:id", handler: update },
    { method: "DELETE", path: "/tasks/:id", handler: remove },
  ];
}
