// app.ts — composition root for the Task API
//
// Wires the repository and routes into a single route table. There is no network
// server on purpose: the demo is about Copilot's behavior, not about running a
// listener. `npm run typecheck` proves everything compiles; `npm run demo:smoke`
// exercises the route table in-process.

import { TaskRepository } from "../src/repositories/task-repository";
import { createTaskRoutes, type Route } from "./routes/task-routes";

/** A simple health-check route so the `api/` surface feels like a real service. */
const healthRoute: Route = {
  method: "GET",
  path: "/health",
  handler: (_req, res) => {
    res.status(200).json({ status: "ok" });
  },
};

/**
 * Builds the full application route table with a shared repository instance.
 *
 * @returns the repository and the registered routes.
 */
export function createApp(): { repo: TaskRepository; routes: Route[] } {
  const repo = new TaskRepository();
  const routes: Route[] = [healthRoute, ...createTaskRoutes(repo)];
  return { repo, routes };
}
