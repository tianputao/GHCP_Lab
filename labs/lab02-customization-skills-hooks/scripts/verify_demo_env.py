#!/usr/bin/env python3
"""Verify Lab 02 environment, prep answer-key files, type safety, smoke test, and hooks."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent.parent


def run_cmd(cmd: list[str]) -> None:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(LAB_ROOT) if not existing else f"{LAB_ROOT}{os.pathsep}{existing}"
    res = subprocess.run(cmd, cwd=LAB_ROOT, env=env, check=False)
    if res.returncode != 0:
        sys.exit(res.returncode)


def main() -> None:
    fail = False
    print("[1/5] Python runtime version (>= 3.11 required)...")
    print(f"      {sys.version.split()[0]}")

    print("[2/5] Prep answer-key files present...")
    required = [
        "prep/copilot-instructions.md",
        "prep/api.instructions.md",
        "prep/skills/scaffold-feature/SKILL.md",
        "prep/skills/scaffold-feature/check_conventions.py",
        "prep/security-reviewer.agent.md",
        "prep/hooks/guardrails.json",
        "prep/hooks/guard_tools.py",
        "prep/insecure_example.py",
    ]
    for rel in required:
        if (LAB_ROOT / rel).is_file():
            print(f"      ✓ {rel}")
        else:
            print(f"      ❌ missing {rel}")
            fail = True

    print("[3/5] Clean BEFORE state check...")
    if (LAB_ROOT / ".github").exists():
        print("      ⚠️  .github/ is currently populated (run 'uv run python scripts/reset_demo.py' for Before->After demo).")
    else:
        print("      ✓ clean starting state — ready for Before -> After demo")

    print("[4/5] mypy strict check + Smoke test...")
    run_cmd([sys.executable, "-m", "mypy", "src", "api", "tests"])
    run_cmd([sys.executable, "-m", "api.smoke"])

    print("[5/5] Hook guardrail & Skill checker tests...")
    run_cmd([sys.executable, "-m", "pytest"])
    run_cmd([sys.executable, "prep/skills/scaffold-feature/check_conventions.py", "src", "api"])

    if fail:
        sys.exit(1)
    print("\n✅ Lab 02 environment verified.")


if __name__ == "__main__":
    main()
