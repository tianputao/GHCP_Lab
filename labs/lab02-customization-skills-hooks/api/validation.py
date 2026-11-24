"""Lightweight field-level input validation for Lab 02 API layer."""

from __future__ import annotations

from src.errors import ValidationError
from src.models import CreateTaskInput, FieldErrorDetail, TaskStatus, UpdateTaskInput

VALID_STATUSES: tuple[TaskStatus, ...] = ("todo", "in_progress", "done")
TITLE_MAX = 200


def validate_create_task(body: object) -> CreateTaskInput:
    """Validate and narrow an untrusted payload into CreateTaskInput.

    Raises:
        ValidationError: When any field is missing or invalid.
    """
    details: list[FieldErrorDetail] = []
    data: dict[str, object] = body if isinstance(body, dict) else {}

    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        details.append({"field": "title", "message": "title is required"})
    elif len(title) > TITLE_MAX:
        details.append({"field": "title", "message": f"title must be <= {TITLE_MAX} chars"})

    description = data.get("description")
    if description is not None and not isinstance(description, str):
        details.append({"field": "description", "message": "description must be a string or null"})

    if details:
        raise ValidationError(details)

    assert isinstance(title, str)
    assert description is None or isinstance(description, str)
    return CreateTaskInput(title=title.strip(), description=description)


def validate_update_task(body: object) -> UpdateTaskInput:
    """Validate and narrow an untrusted payload into UpdateTaskInput.

    Raises:
        ValidationError: When any provided field is invalid.
    """
    details: list[FieldErrorDetail] = []
    data: dict[str, object] = body if isinstance(body, dict) else {}

    title_val: str | None = None
    status_val: TaskStatus | None = None
    has_description = "description" in data
    description_val: str | None = None

    if "title" in data:
        raw_title = data["title"]
        if not isinstance(raw_title, str) or not raw_title.strip() or len(raw_title) > TITLE_MAX:
            details.append({"field": "title", "message": f"title must be 1-{TITLE_MAX} chars"})
        else:
            title_val = raw_title.strip()

    if "status" in data:
        raw_status = data["status"]
        if not isinstance(raw_status, str) or raw_status not in VALID_STATUSES:
            details.append(
                {
                    "field": "status",
                    "message": f"status must be one of {', '.join(VALID_STATUSES)}",
                }
            )
        else:
            status_val = raw_status

    if has_description:
        raw_desc = data["description"]
        if raw_desc is not None and not isinstance(raw_desc, str):
            details.append(
                {"field": "description", "message": "description must be a string or null"}
            )
        else:
            description_val = raw_desc

    if details:
        raise ValidationError(details)

    return UpdateTaskInput(
        title=title_val,
        has_description=has_description,
        description=description_val,
        status=status_val,
    )
