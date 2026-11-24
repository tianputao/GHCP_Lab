"""Evaluate a student's `SDD/playground/src/app.py` against all 12 enterprise contracts."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from evaluator.acceptance_suite import run_acceptance_suite

SDD_ROOT = Path(__file__).resolve().parent.parent
PLAYGROUND_APP = SDD_ROOT / "playground" / "src" / "app.py"


def main() -> None:
    if not PLAYGROUND_APP.is_file():
        print(
            "❌ playground/src/app.py not found. Run `uv run python scripts/reset_playground.py` first!",
            file=sys.stderr,
        )
        sys.exit(1)

    if str(SDD_ROOT) not in sys.path:
        sys.path.insert(0, str(SDD_ROOT))

    spec = importlib.util.spec_from_file_location("playground_app", PLAYGROUND_APP)
    if spec is None or spec.loader is None:
        print("❌ Unable to load playground/src/app.py", file=sys.stderr)
        sys.exit(1)

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    create_app = getattr(mod, "create_app", None)
    if not callable(create_app):
        print("❌ playground/src/app.py must export `create_app()`.", file=sys.stderr)
        sys.exit(1)

    results = run_acceptance_suite(create_app)
    passed = sum(1 for r in results if r.passed)

    print("\n=== Student Playground · 12-Contract SDD Acceptance Evaluation ===\n")
    for r in results:
        mark = "✅" if r.passed else "❌"
        print(f"{mark} {r.id} [{r.category}] {r.title}")
        if not r.passed:
            print(f"     ↳ {r.detail}")
    print(f"\nTotal Score: {passed} / {len(results)}")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
