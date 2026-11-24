#!/usr/bin/env python3
"""GitHub AI Credits & Context Budget Audit Tool (Lab 05).

Demonstrates why context engineering directly governs Token-Based Billing (AI Credits):
  1. Checks `.github/copilot-instructions.md` length against Copilot Code Review's
     4,000-character instruction prefix window.
  2. Compares estimated input token footprint of:
     - Naive approach: dumping all lab files into every turn
     - Targeted approach: referencing only task-relevant files + concise instructions
"""

from __future__ import annotations

import math
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent.parent
IGNORED_DIRS = {".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".git", "dist"}


def estimate_tokens(char_count: int) -> int:
    """Rule-of-thumb approximation (~4 chars/token for code & English)."""
    return math.ceil(char_count / 4)


def walk_files(root: Path) -> list[Path]:
    result: list[Path] = []
    for path in sorted(root.rglob("*")):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.is_file():
            result.append(path)
    return result


def main() -> None:
    all_files = walk_files(LAB_ROOT)
    naive_chars = sum(len(f.read_text(encoding="utf-8", errors="ignore")) for f in all_files)

    targeted_paths = [
        ".github/copilot-instructions.md",
        "src/routes/orders.py",
        "src/lib/discount.py",
    ]
    targeted_chars = 0
    for rel in targeted_paths:
        full = LAB_ROOT / rel
        if full.is_file():
            targeted_chars += len(full.read_text(encoding="utf-8"))

    instructions_path = LAB_ROOT / ".github/copilot-instructions.md"
    instruction_chars = (
        len(instructions_path.read_text(encoding="utf-8")) if instructions_path.is_file() else 0
    )

    naive_tokens = estimate_tokens(naive_chars)
    targeted_tokens = estimate_tokens(targeted_chars)
    reduction_pct = round((1 - targeted_tokens / naive_tokens) * 100) if naive_tokens > 0 else 0
    budget_status = "PASS ✅" if instruction_chars <= 4000 else "OVER LIMIT ⚠️"

    print("=== Lab 05 · Context & GitHub AI Credits Optimization Audit ===")
    print(f"Files scanned (excluding .venv/caches): {len(all_files)}")
    print(f"Instruction file length: {instruction_chars} chars (Code Review 4,000-char budget: {budget_status})")
    print(f"Naive full-folder context estimate:    ~{naive_tokens} input tokens/turn")
    print(f"Targeted #file context estimate:       ~{targeted_tokens} input tokens/turn ({reduction_pct}% input reduction)")
    print(f"10-turn Agent session savings:         ~{(naive_tokens - targeted_tokens) * 10} input tokens saved")
    print("Tip: Pair targeted #file context + concise instructions + Task-Aware Auto + local fast tests to optimize AI Credits.")


if __name__ == "__main__":
    main()
