#!/usr/bin/env python3
"""Bundled deterministic verification script for the `scaffold-feature` Agent Skill.

Checks target directories for common Python standards violations:
  - explicit `Any` annotations
  - dynamic `eval(` or `exec(` calls
  - raw string interpolation/concatenation inside SQL statements
  - `shell=True` subprocess calls
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RULES: list[tuple[str, re.Pattern[str], str]] = [
    ("NO_ANY", re.compile(r"(?::|\->|\[)\s*Any\b"), "Avoid explicit `Any` type; use precise types or `object`"),
    ("NO_EVAL", re.compile(r"\b(eval|exec)\s*\("), "Do not use dynamic `eval()` or `exec()`"),
    ("NO_SHELL_TRUE", re.compile(r"\bshell\s*=\s*True\b"), "Avoid `shell=True` in subprocess calls"),
    (
        "NO_SQL_CONCAT",
        re.compile(
            r"""(?:f["'](?:SELECT|INSERT|UPDATE|DELETE)\b[^"']*\{|["'](?:SELECT|INSERT|UPDATE|DELETE)\b[^"']*["']\s*\+)""",
            re.IGNORECASE,
        ),
        "Possible unparameterized SQL string concatenation/f-string",
    ),
]


def walk_py(target: Path) -> list[Path]:
    if target.is_file():
        return [target] if target.suffix == ".py" else []
    files: list[Path] = []
    for path in sorted(target.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        files.append(path)
    return files


def main() -> None:
    targets = sys.argv[1:]
    if not targets:
        print("Usage: python check_conventions.py <dir1> [dir2...]", file=sys.stderr)
        sys.exit(2)

    cwd = Path.cwd()
    violations: list[tuple[str, int, str, str]] = []
    files_scanned = 0

    for raw_target in targets:
        abs_target = (cwd / raw_target).resolve()
        for file_path in walk_py(abs_target):
            files_scanned += 1
            rel = str(file_path.relative_to(cwd))
            lines = file_path.read_text(encoding="utf-8").splitlines()
            for idx, line in enumerate(lines, start=1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                for rule_id, pattern, message in RULES:
                    if pattern.search(line):
                        violations.append((rel, idx, rule_id, message))

    if violations:
        print(
            f"❌ Convention check failed ({len(violations)} issue(s) across {files_scanned} files):",
            file=sys.stderr,
        )
        for rel, line_no, rule_id, msg in violations:
            print(f"  - {rel}:{line_no} [{rule_id}] {msg}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Convention check passed ({files_scanned} Python files scanned, 0 violations).")


if __name__ == "__main__":
    main()
