#!/usr/bin/env python3
"""Reset Lab 02 back to a clean BEFORE state."""

from __future__ import annotations

import shutil
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    print("Resetting Lab 02 to clean BEFORE state...")
    for rel in (".github", "api/test_route.py", ".hook-audit.log"):
        target = LAB_ROOT / rel
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
    print("✅ Lab 02 reset complete. Run 'uv run python scripts/verify_demo_env.py' to confirm clean state.")


if __name__ == "__main__":
    main()
