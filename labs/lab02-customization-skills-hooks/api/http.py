"""Lightweight, dependency-free HTTP abstraction for Lab 02."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol

from src.errors import AppError, ValidationError
from src.models import ApiErrorBody, ApiErrorPayload


@dataclass(frozen=True)
class ApiRequest:
    """An inbound HTTP request."""

    params: dict[str, str] = field(default_factory=dict)
    query: dict[str, str | None] = field(default_factory=dict)
    body: object = None


class ApiResponse(Protocol):
    """Fluent response writer protocol (`status().json()` or `status().end()`)."""

    def status(self, code: int) -> ApiResponse: ...
    def json(self, payload: object) -> None: ...
    def end(self) -> None: ...


RouteHandler = Callable[[ApiRequest, ApiResponse], None]


def send_error(res: ApiResponse, err: Exception) -> None:
    """Translate any raised exception into the standard ApiErrorBody envelope.

    Known AppError subclasses map to their declared HTTP status and code;
    unexpected exceptions become an opaque 500 so internals never leak.
    """
    if isinstance(err, AppError):
        payload: ApiErrorPayload = {"code": err.code, "message": err.message}
        if isinstance(err, ValidationError):
            payload["details"] = err.details
        body: ApiErrorBody = {"error": payload}
        res.status(err.status).json(body)
        return

    body = {"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}}
    res.status(500).json(body)
