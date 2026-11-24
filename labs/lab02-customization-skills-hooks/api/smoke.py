"""In-process smoke test for the Lab 02 Task API."""

from __future__ import annotations

from dataclasses import dataclass

from api.app import create_app
from api.http import ApiRequest, RouteHandler


@dataclass
class Captured:
    status_code: int = 0
    payload: object = None


class FakeResponse:
    def __init__(self, out: Captured) -> None:
        self._out = out

    def status(self, code: int) -> FakeResponse:
        self._out.status_code = code
        return self

    def json(self, payload: object) -> None:
        self._out.payload = payload

    def end(self) -> None:
        self._out.payload = None


def call_handler(
    handler: RouteHandler,
    *,
    params: dict[str, str] | None = None,
    query: dict[str, str | None] | None = None,
    body: object = None,
) -> Captured:
    out = Captured()
    res = FakeResponse(out)
    req = ApiRequest(params=params or {}, query=query or {}, body=body)
    handler(req, res)
    return out


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(f"SMOKE FAIL: {label}")
    print(f"  ✓ {label}")


def main() -> None:
    print("Running Task API smoke test...")
    app = create_app()

    def by_key(method: str, path: str) -> RouteHandler:
        for route in app.routes:
            if route.method == method and route.path == path:
                return route.handler
        raise LookupError(f"route not found: {method} {path}")

    created = call_handler(by_key("POST", "/tasks"), body={"title": "Write talk track"})
    check(created.status_code == 201, "POST /tasks returns 201")
    assert isinstance(created.payload, dict)
    task_id = str(created.payload["id"])

    fetched = call_handler(by_key("GET", "/tasks/:id"), params={"id": task_id})
    check(fetched.status_code == 200, "GET /tasks/:id returns 200")

    missing = call_handler(by_key("GET", "/tasks/:id"), params={"id": "does-not-exist"})
    check(missing.status_code == 404, "GET unknown id returns 404")

    bad = call_handler(by_key("POST", "/tasks"), body={"title": ""})
    check(bad.status_code == 400, "POST with empty title returns 400")

    updated = call_handler(
        by_key("PUT", "/tasks/:id"),
        params={"id": task_id},
        body={"status": "done"},
    )
    check(updated.status_code == 200, "PUT /tasks/:id returns 200")

    removed = call_handler(by_key("DELETE", "/tasks/:id"), params={"id": task_id})
    check(removed.status_code == 204, "DELETE /tasks/:id returns 204")

    print("Smoke test passed. ✅")


if __name__ == "__main__":
    main()
