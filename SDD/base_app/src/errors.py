"""Standard API error envelope shared across brownfield Order endpoints."""

from __future__ import annotations

from fastapi.responses import JSONResponse

from base_app.src.models import ErrorDetail


class AppError(Exception):
    """Domain/HTTP error carrying stable error code and optional field details."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: list[ErrorDetail] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


def error_response(err: Exception) -> JSONResponse:
    """Serialize any exception into `{ "error": { "code", "message", "details?" } }`."""
    if isinstance(err, AppError):
        payload: dict[str, object] = {"code": err.code, "message": err.message}
        if err.details is not None:
            payload["details"] = err.details
        return JSONResponse(status_code=err.status_code, content={"error": payload})

    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}},
    )
