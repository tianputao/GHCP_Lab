"""Lab 05 Capstone Step 6: INTENTIONALLY TAUTOLOGICAL TEST — fix this during the exercise!"""

from __future__ import annotations

from src.lib.discount import apply_discount


def test_apply_discount_tautological_fix_in_step6() -> None:
    expected = apply_discount(100, "10")  # BAD: self-referential expectation!
    assert apply_discount(100, "10") == expected
