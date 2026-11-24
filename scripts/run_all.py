#!/usr/bin/env python3
"""Cross-platform orchestrator for all Python + uv sub-projects inside GHCP_Lab.

Usage:
    uv run ghcp-lab verify
    uv run ghcp-lab test
    uv run ghcp-lab reset
    uv run ghcp-lab sdd-compare
    uv run ghcp-lab lab02-apply
    uv run ghcp-lab lab02-reset
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PROJECTS: list[dict[str, object]] = [
    {
        "name": "Lab 01 · Agent / Plan / Autopilot",
        "dir": "labs/lab01-agent-plan-and-autopilot",
        "test": [[sys.executable, "-m", "pytest"]],
        "verify": [
            [sys.executable, "-m", "mypy", "src", "tests"],
            [sys.executable, "-m", "pytest"],
        ],
    },
    {
        "name": "Lab 02 · Customization / Skills / Hooks",
        "dir": "labs/lab02-customization-skills-hooks",
        "test": [
            [sys.executable, "-m", "api.smoke"],
            [sys.executable, "-m", "pytest"],
            [
                sys.executable,
                "prep/skills/scaffold-feature/check_conventions.py",
                "src",
                "api",
            ],
        ],
        "verify": [
            [sys.executable, "-m", "mypy", "src", "api", "tests"],
            [sys.executable, "-m", "api.smoke"],
            [sys.executable, "-m", "pytest"],
            [
                sys.executable,
                "prep/skills/scaffold-feature/check_conventions.py",
                "src",
                "api",
            ],
        ],
    },
    {
        "name": "Lab 03 · Custom Enterprise MCP Server",
        "dir": "labs/lab03-mcp-server-and-tools",
        "test": [[sys.executable, "-m", "pytest"]],
        "verify": [
            [sys.executable, "-m", "mypy", "src", "tests"],
            [sys.executable, "-m", "pytest"],
        ],
    },
    {
        "name": "Lab 04 · Testing / Security / Review",
        "dir": "labs/lab04-testing-security-and-review",
        "test": [[sys.executable, "-m", "pytest"]],
        "verify": [
            [sys.executable, "-m", "mypy", "src", "tests"],
            [sys.executable, "-m", "pytest"],
        ],
    },
    {
        "name": "Lab 05 · Governance / AI Credits / Capstone",
        "dir": "labs/lab05-enterprise-governance-and-capstone",
        "test": [[sys.executable, "-m", "pytest"]],
        "verify": [
            [sys.executable, "-m", "mypy", "src", "tests"],
            [sys.executable, "-m", "pytest"],
            [sys.executable, "scripts/token_budget_audit.py"],
            ["bash", "scripts/check-org-governance.sh", "--dry-run"],
        ],
    },
    {
        "name": "SDD    · Vibe Coding vs SDD (OpenSpec)",
        "dir": "SDD",
        "test": [[sys.executable, "-m", "pytest"]],
        "verify": [
            [sys.executable, "scripts/validate_openspec.py"],
            [
                sys.executable,
                "-m",
                "mypy",
                "base_app",
                "track_a_vibe_coding",
                "track_b_sdd",
                "evaluator",
            ],
            [sys.executable, "-m", "pytest"],
            [sys.executable, "-m", "evaluator.compare"],
        ],
    },
]


def run_step(label: str, cwd: Path, cmd: list[str]) -> None:
    rel_cwd = cwd.relative_to(ROOT) if cwd != ROOT else Path(".")
    print("\n============================================================")
    print(f"▶ {label}")
    print(f"  cwd: {rel_cwd}")
    print(f"  cmd: {' '.join(cmd)}")
    print("============================================================", flush=True)
    env = os.environ.copy()
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(cwd) if not existing_pp else f"{cwd}{os.pathsep}{existing_pp}"
    result = subprocess.run(cmd, cwd=cwd, env=env, check=False)
    if result.returncode != 0:
        print(f'\n❌ Failed in "{label}" (exit code {result.returncode})', file=sys.stderr)
        sys.exit(result.returncode)


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    action = args[0] if args else "verify"

    if action == "sdd-compare":
        run_step(
            "SDD vs Vibe Coding Scorecard",
            ROOT / "SDD",
            [sys.executable, "-m", "evaluator.compare"],
        )
        return

    if action == "lab02-apply":
        run_step(
            "Apply Lab 02 Customizations",
            ROOT / "labs/lab02-customization-skills-hooks",
            [sys.executable, "scripts/apply_all.py"],
        )
        return

    if action == "lab02-reset":
        run_step(
            "Reset Lab 02 Customizations",
            ROOT / "labs/lab02-customization-skills-hooks",
            [sys.executable, "scripts/reset_demo.py"],
        )
        return

    if action == "reset":
        run_step(
            "Reset · Lab 02 Customization",
            ROOT / "labs/lab02-customization-skills-hooks",
            [sys.executable, "scripts/reset_demo.py"],
        )
        run_step(
            "Reset · SDD Playground",
            ROOT / "SDD",
            [sys.executable, "scripts/reset_playground.py"],
        )
        print('\n✅ All "reset" actions completed cleanly across GHCP_Lab!')
        return

    if action not in ("test", "verify"):
        print(
            f"Unknown action: {action}. Supported: verify | test | reset | sdd-compare | lab02-apply | lab02-reset",
            file=sys.stderr,
        )
        sys.exit(1)

    for project in PROJECTS:
        proj_dir = ROOT / str(project["dir"])
        if not (proj_dir / "pyproject.toml").exists():
            print(f"❌ Missing pyproject.toml in {project['dir']}", file=sys.stderr)
            sys.exit(1)
        cmds = project[action]
        assert isinstance(cmds, list)
        for cmd in cmds:
            run_step(f"{action.title()} · {project['name']}", proj_dir, cmd)

    print(f'\n✅ All "{action}" checks completed cleanly across GHCP_Lab!')


if __name__ == "__main__":
    main()
