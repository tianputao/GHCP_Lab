#!/usr/bin/env python3
"""Pure-Python Strict OpenSpec 2.1 Validator (zero Node.js required).

Validates the OpenSpec workspace under `SDD/openspec/`:
  - `openspec/config.yaml` schema and context
  - Base specs under `openspec/specs/**/spec.md`
  - Active changes under `openspec/changes/*/` (`.openspec.yaml`, `proposal.md`,
    `design.md`, `tasks.md`, and `specs/**/spec.md` delta files)
  - Strict rules matching `@fission-ai/openspec` 2.1:
      * Each requirement (`### Requirement: ...`) must use normative SHALL/MUST language
      * Each requirement must define at least one `#### Scenario:` block with `WHEN` and `THEN`
      * `proposal.md` must document `## Why`, `## What Changes`, and Non-Goals
      * `tasks.md` must reference `REQ-XX` identifiers

Optional cross-check:
  Pass `--use-npx` (when Node.js is installed) to additionally invoke
  `npx --yes @fission-ai/openspec validate --all --strict --no-interactive`.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

SDD_ROOT = Path(__file__).resolve().parent.parent
OPENSPEC_DIR = SDD_ROOT / "openspec"

REQ_HEADING_RE = re.compile(r"^###\s+Requirement:\s+(.+)$", re.MULTILINE)
SCENARIO_HEADING_RE = re.compile(r"^####\s+Scenario:\s+(.+)$", re.MULTILINE)
NORMATIVE_RE = re.compile(r"\b(SHALL|MUST)\b")
REQ_ID_RE = re.compile(r"\bREQ-\d{2}\b")


def validate_spec_file(spec_path: Path, *, is_delta: bool) -> list[str]:
    errors: list[str] = []
    rel = str(spec_path.relative_to(SDD_ROOT))
    text = spec_path.read_text(encoding="utf-8")

    if is_delta:
        if not re.search(r"^##\s+(ADDED|MODIFIED|REMOVED)\s+Requirements\b", text, re.MULTILINE):
            errors.append(f"{rel}: missing `## ADDED/MODIFIED/REMOVED Requirements` section")
    else:
        if "## Purpose" not in text:
            errors.append(f"{rel}: missing `## Purpose` section")

    matches = list(REQ_HEADING_RE.finditer(text))
    if not matches:
        errors.append(f"{rel}: must contain at least one `### Requirement:` heading")
        return errors

    for idx, match in enumerate(matches):
        req_title = match.group(1).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        block = text[start:end]

        if not NORMATIVE_RE.search(block):
            errors.append(f"{rel}: requirement '{req_title}' missing normative SHALL/MUST statement")

        scenarios = list(SCENARIO_HEADING_RE.finditer(block))
        if not scenarios:
            errors.append(f"{rel}: requirement '{req_title}' missing at least one `#### Scenario:` block")
            continue

        for s_idx, s_match in enumerate(scenarios):
            s_title = s_match.group(1).strip()
            s_start = s_match.end()
            s_end = scenarios[s_idx + 1].start() if s_idx + 1 < len(scenarios) else len(block)
            s_body = block[s_start:s_end]
            if "**WHEN**" not in s_body and "WHEN " not in s_body:
                errors.append(f"{rel}: scenario '{s_title}' missing WHEN condition")
            if "**THEN**" not in s_body and "THEN " not in s_body:
                errors.append(f"{rel}: scenario '{s_title}' missing THEN outcome")

    return errors


def validate_workspace() -> tuple[list[str], int, int]:
    errors: list[str] = []

    config_path = OPENSPEC_DIR / "config.yaml"
    if not config_path.is_file():
        return [f"Missing {config_path.relative_to(SDD_ROOT)}"], 0, 0

    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or not config.get("schema"):
        errors.append("openspec/config.yaml: must define `schema`")

    base_specs = sorted((OPENSPEC_DIR / "specs").glob("**/spec.md"))
    for spec_path in base_specs:
        errors.extend(validate_spec_file(spec_path, is_delta=False))

    changes_dir = OPENSPEC_DIR / "changes"
    change_dirs = [
        d for d in sorted(changes_dir.iterdir())
        if d.is_dir() and d.name != "archive"
    ] if changes_dir.is_dir() else []

    for change_dir in change_dirs:
        rel_change = str(change_dir.relative_to(SDD_ROOT))
        for required_file in (".openspec.yaml", "proposal.md", "design.md", "tasks.md"):
            if not (change_dir / required_file).is_file():
                errors.append(f"{rel_change}: missing required artifact `{required_file}`")

        proposal_path = change_dir / "proposal.md"
        if proposal_path.is_file():
            proposal = proposal_path.read_text(encoding="utf-8")
            if "## Why" not in proposal:
                errors.append(f"{rel_change}/proposal.md: missing `## Why` section")
            if "## What Changes" not in proposal:
                errors.append(f"{rel_change}/proposal.md: missing `## What Changes` section")
            if "Non-Goals" not in proposal:
                errors.append(f"{rel_change}/proposal.md: missing explicit Non-Goals section")

        tasks_path = change_dir / "tasks.md"
        if tasks_path.is_file():
            tasks = tasks_path.read_text(encoding="utf-8")
            if not REQ_ID_RE.search(tasks):
                errors.append(f"{rel_change}/tasks.md: tasks must reference REQ-XX identifiers")

        delta_specs = sorted((change_dir / "specs").glob("**/spec.md"))
        if not delta_specs:
            errors.append(f"{rel_change}: missing delta spec files under `specs/**/spec.md`")
        for spec_path in delta_specs:
            errors.extend(validate_spec_file(spec_path, is_delta=True))

    return errors, len(base_specs), len(change_dirs)


def main() -> None:
    use_npx = "--use-npx" in sys.argv[1:]
    errors, base_count, change_count = validate_workspace()

    if errors:
        print(f"❌ OpenSpec strict validation failed ({len(errors)} issue(s)):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    print(
        f"✅ OpenSpec strict validation passed ({base_count} base spec(s), {change_count} change(s), 0 issues) [Python validator]."
    )

    if use_npx:
        npx_bin = shutil.which("npx")
        if npx_bin is None:
            print("⚠️  --use-npx requested, but `npx` was not found in PATH.", file=sys.stderr)
            sys.exit(1)
        env = os.environ.copy()
        env["OPENSPEC_TELEMETRY"] = "0"
        res = subprocess.run(
            [npx_bin, "--yes", "@fission-ai/openspec", "validate", "--all", "--strict", "--no-interactive"],
            cwd=SDD_ROOT,
            env=env,
            check=False,
        )
        if res.returncode != 0:
            sys.exit(res.returncode)


if __name__ == "__main__":
    main()
