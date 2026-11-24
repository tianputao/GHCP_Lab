"""Lab 04 — Real vs Tautological Tests."""

from __future__ import annotations

import math

import pytest

from src.calculate_discount import calculate_discount


def test_tautological_antipattern_inspect_in_lab04() -> None:
    """TAUTOLOGICAL ANTI-PATTERN (always passes, proves nothing — inspect in Lab 04)."""
    # BAD: computes "expected" by calling the exact same function under test!
    expected = calculate_discount(100, 15, 20, 50)
    assert calculate_discount(100, 15, 20, 50) == expected


def test_real_discount_contract() -> None:
    """REAL TEST: enforces min_order threshold, normal discount, max_cap, and error paths."""
    assert calculate_discount(40, 20, 50, 50) == 0.0
    assert calculate_discount(100, 15, 50, 50) == 15.0
    assert calculate_discount(500, 30, 50, 50) == 50.0
    with pytest.raises(ValueError):
        calculate_discount(100, 120, 50, 0)
    with pytest.raises(TypeError):
        calculate_discount(math.nan, 10, 50, 0)
