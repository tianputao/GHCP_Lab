#!/usr/bin/env python3
"""Copy `SDD/base_app/` cleanly into `SDD/playground/` so students or instructors
can repeatedly practice Vibe Coding vs SDD from an identical brownfield starting point.
"""

from __future__ import annotations

import shutil
from pathlib import Path

SDD_ROOT = Path(__file__).resolve().parent.parent
SOURCE = SDD_ROOT / "base_app"
TARGET = SDD_ROOT / "playground"


def main() -> None:
    if TARGET.exists():
        shutil.rmtree(TARGET)
    shutil.copytree(
        SOURCE,
        TARGET,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
    )
    print("✅ Reset SDD/playground/ from clean brownfield SDD/base_app/.")
    print(
        "   Next: run Vibe Coding or SDD inside SDD/playground/, then evaluate with `uv run python -m evaluator.evaluate_playground`."
    )


if __name__ == "__main__":
    main()
