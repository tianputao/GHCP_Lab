"""Capped monetary discount calculator for AI TDD & boundary-test exercises."""

from __future__ import annotations

import math


def calculate_discount(
    amount: float,
    percent: float,
    max_cap: float,
    min_order: float,
) -> float:
    """Compute a capped monetary discount with a minimum order threshold."""
    values = (amount, percent, max_cap, min_order)
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise TypeError("All inputs must be finite numbers")

    if amount < 0 or percent < 0 or max_cap < 0 or min_order < 0:
        raise ValueError("Inputs cannot be negative")

    if percent > 100:
        raise ValueError("Percent cannot exceed 100")

    if amount < min_order:
        return 0.0

    raw_discount = (amount * percent) / 100.0
    final_discount = min(raw_discount, max_cap, amount)
    return round(final_discount, 2)
