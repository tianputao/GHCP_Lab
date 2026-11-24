// smoke.ts — in-process smoke test for the Task API
//
// Not a unit-test suite (that's a great thing to have Copilot generate during the
// demo!). This just exercises the route table end-to-end so `npm run demo:smoke`
// proves the base project is wired correctly before you present.

import { createApp } from "./app";
import type { ApiRequest, ApiResponse, RouteHandler } from "./http";

interface Captured {
  status: number;
  payload: unknown;
}

/** Builds a fake response that records what a handler wrote. */
function captureResponse(): { res: ApiResponse; out: Captured } {
  const out: Captured = { status: 0, payload: undefined };
  const res: ApiResponse = {
    status(code: number) {
      out.status = code;
      return res;
    },
    json(payload: unknown) {
      out.payload = payload;
    },
    end() {
      out.payload = undefined;
    },
  };
  return { res, out };
}

function call(
  handler: RouteHandler,
  req: Partial<ApiRequest> & { body?: unknown },
): Captured {
  const { res, out } = captureResponse();
  const fullReq: ApiRequest = {
    params: req.params ?? {},
    query: req.query ?? {},
    body: req.body,
  };
  void handler(fullReq, res);
  return out;
}

function assert(condition: boolean, label: string): void {
  if (!condition) {
    throw new Error(`SMOKE FAIL: ${label}`);
  }
  console.log(`  ✓ ${label}`);
}

function main(): void {
  console.log("Running Task API smoke test...");
  const { routes } = createApp();
  const byKey = (method: string, path: string): RouteHandler => {
    const route = routes.find((r) => r.method === method && r.path === path);
    if (!route) {
      throw new Error(`route not found: ${method} ${path}`);
    }
    return route.handler;
  };

  const created = call(byKey("POST", "/tasks"), { body: { title: "Write talk track" } });
  assert(created.status === 201, "POST /tasks returns 201");
  const id = (created.payload as { id: string }).id;

  const fetched = call(byKey("GET", "/tasks/:id"), { params: { id } });
  assert(fetched.status === 200, "GET /tasks/:id returns 200");

  const missing = call(byKey("GET", "/tasks/:id"), { params: { id: "does-not-exist" } });
  assert(missing.status === 404, "GET unknown id returns 404");

  const bad = call(byKey("POST", "/tasks"), { body: { title: "" } });
  assert(bad.status === 400, "POST with empty title returns 400");

  const updated = call(byKey("PUT", "/tasks/:id"), { params: { id }, body: { status: "done" } });
  assert(updated.status === 200, "PUT /tasks/:id returns 200");

  const removed = call(byKey("DELETE", "/tasks/:id"), { params: { id } });
  assert(removed.status === 204, "DELETE /tasks/:id returns 204");

  console.log("Smoke test passed. ✅");
}

main();
