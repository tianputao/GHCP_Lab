"""INTENTIONAL VULNERABLE TEACHING ARTIFACT (OWASP A03: Code Injection).

DO NOT copy into production code.
Lab 04 Exercise 2: Ask Copilot to explain why `apply_discount_vulnerable` is
exploitable, fix it safely (strict numeric parsing + range validation), and add
regression tests rejecting expression payloads like `"__import__('os').environ"`.
"""

from __future__ import annotations

import math
import re

PLAIN_NUMBER_RE = re.compile(r"^\d+(\.\d+)?$")


def apply_discount_vulnerable(amount: float, rule: str) -> float:
    """Intentionally unsafe dynamic eval() for security training."""
    percent = float(eval(rule))  # noqa: S307 — INTENTIONAL VULNERABILITY for Lab 04
    safe_percent = min(max(percent, 0.0), 100.0)
    return round(amount * (1.0 - safe_percent / 100.0), 2)


def apply_discount_safe(amount: float, rule: str) -> float:
    """Reference hardened implementation for side-by-side comparison."""
    if isinstance(amount, bool) or not isinstance(amount, (int, float)) or not math.isfinite(amount) or amount < 0:
        raise ValueError("amount must be a non-negative finite number")
    trimmed = rule.strip()
    if not PLAIN_NUMBER_RE.match(trimmed):
        raise ValueError("discount rule must be a plain non-negative numeric percentage")
    percent = float(trimmed)
    if not math.isfinite(percent) or percent < 0 or percent > 100:
        raise ValueError("discount percentage must be between 0 and 100")
    return round(amount * (1.0 - percent / 100.0), 2)
