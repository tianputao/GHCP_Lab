"""In-memory typed table stand-in for Lab 02.

Zero third-party dependencies so the demo runs cleanly anywhere. Repository
methods document the equivalent parameterized SQL (`?` placeholders) in their
docstrings so Copilot learns the convention from real visible examples.
"""

from __future__ import annotations

import copy
from collections.abc import Callable
from typing import Generic, Protocol, TypeVar


class HasId(Protocol):
    @property
    def id(self) -> str: ...


RowT = TypeVar("RowT", bound=HasId)
SqlValue = str | int | float | None


class InMemoryTable(Generic[RowT]):
    """Minimal, strongly-typed in-memory table."""

    def __init__(self) -> None:
        self._rows: dict[str, RowT] = {}

    def insert(self, row: RowT) -> None:
        """Insert a row. Raises ValueError if the id already exists."""
        if row.id in self._rows:
            raise ValueError(f"duplicate id: {row.id}")
        self._rows[row.id] = copy.deepcopy(row)

    def find_by_id(self, row_id: str) -> RowT | None:
        """Return a single row by id, or None if not present."""
        found = self._rows.get(row_id)
        return copy.deepcopy(found) if found is not None else None

    def find_all(self, predicate: Callable[[RowT], bool] | None = None) -> list[RowT]:
        """Return all rows, optionally filtered by a predicate."""
        items = [copy.deepcopy(r) for r in self._rows.values()]
        return [r for r in items if predicate(r)] if predicate is not None else items

    def update(self, row: RowT) -> int:
        """Replace an existing row. Returns rows changed (0 or 1)."""
        if row.id not in self._rows:
            return 0
        self._rows[row.id] = copy.deepcopy(row)
        return 1

    def remove(self, row_id: str) -> int:
        """Remove a row by id. Returns rows changed (0 or 1)."""
        if row_id in self._rows:
            del self._rows[row_id]
            return 1
        return 0
