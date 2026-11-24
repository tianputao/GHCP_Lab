"""Custom domain errors for Lab 02 Task API.

Convention demonstrated for Copilot: never raise bare Exception or strings.
Every error carries a stable `code` and HTTP `status` so the API layer maps it
to the standard error envelope without leaking stack traces.
"""

from __future__ import annotations

from abc import ABC

from src.models import FieldErrorDetail


class AppError(Exception, ABC):
    """Base class for all application errors."""

    code: str
    status: int

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    """Raised when a requested resource does not exist (HTTP 404)."""

    code = "NOT_FOUND"
    status = 404

    def __init__(self, resource: str, resource_id: str) -> None:
        super().__init__(f'{resource} with id "{resource_id}" was not found')


class ValidationError(AppError):
    """Raised when client input fails validation (HTTP 400)."""

    code = "VALIDATION_ERROR"
    status = 400

    def __init__(self, details: list[FieldErrorDetail]) -> None:
        super().__init__("One or more fields are invalid")
        self.details = details


class ConflictError(AppError):
    """Raised when an operation conflicts with current state (HTTP 409)."""

    code = "CONFLICT"
    status = 409

    def __init__(self, message: str) -> None:
        super().__init__(message)
