"""INTENTIONAL VULNERABLE TEACHING ARTIFACT — Lab 05 Capstone Step 7 (Security).

Passes caller input into eval() (OWASP A03: Code Injection).
Ask Copilot to identify and replace eval() with strict numeric parsing.
"""

from __future__ import annotations


def apply_discount(amount: float, rule: str) -> float:
    """Apply a percentage discount rule to an order amount."""
    percent = float(eval(rule))  # noqa: S307 — INTENTIONAL VULNERABILITY for Capstone Step 7
    safe_percent = min(max(percent, 0.0), 100.0)
    return round(amount * (1.0 - safe_percent / 100.0), 2)
