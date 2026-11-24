#!/usr/bin/env python3
"""Deterministic Copilot `preToolUse` Hook Guardrail (2026 Copilot Harness).

Unlike prose instructions (probabilistic guidance for an LLM), hooks run
deterministically before every tool call and enforce hard security boundaries.

Reads a JSON hook event from stdin and writes a JSON decision to stdout:
    {"permissionDecision": "allow" | "deny", "permissionDecisionReason": "..."}
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, UTC
from typing import Any

DANGEROUS_SHELL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("destructive-rm", re.compile(r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f\b|\brm\s+-rf\b")),
    ("force-push", re.compile(r"\bgit\s+push\b[^\n]*(--force|-f)\b")),
    ("pipe-to-shell", re.compile(r"\b(curl|wget)\b[^\n]*\|\s*(ba)?sh\b")),
    ("privilege-escalation", re.compile(r"\bsudo\b")),
]

SENSITIVE_FILE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(^|[\\/])\.env(\.|$)", re.IGNORECASE),
    re.compile(r"(^|[\\/])secrets[\\/]", re.IGNORECASE),
    re.compile(r"\.(pem|key)$", re.IGNORECASE),
]

SHELL_TOOL_RE = re.compile(r"(shell|bash|terminal|powershell|run_in_terminal|command)")
FILE_TOOL_RE = re.compile(r"(read|view|edit|write|create|patch|file|shell|bash|terminal)")


def evaluate_tool_event(event: dict[str, Any]) -> dict[str, str]:
    """Evaluate a preToolUse hook event and return an allow/deny decision."""
    tool_name = str(event.get("toolName") or event.get("tool_name") or "").lower()
    raw_args = event.get("toolArgs")
    if raw_args is None:
        raw_args = event.get("tool_input")
    if raw_args is None:
        raw_args = event.get("input")
    if raw_args is None:
        raw_args = {}

    args_text = raw_args if isinstance(raw_args, str) else json.dumps(raw_args)

    # 1. Block destructive shell commands regardless of prompt wording
    if SHELL_TOOL_RE.search(tool_name):
        for rule_name, pattern in DANGEROUS_SHELL_PATTERNS:
            if pattern.search(args_text):
                return {
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        f"Blocked by deterministic hook [{rule_name}]: "
                        "destructive or privileged shell command is not permitted in this lab."
                    ),
                }

    # 2. Block reading/writing sensitive secret paths
    if FILE_TOOL_RE.search(tool_name):
        candidates: list[str] = []
        if isinstance(raw_args, str):
            candidates.append(raw_args)
        elif isinstance(raw_args, dict):
            for value in raw_args.values():
                if isinstance(value, str):
                    candidates.append(value)
        for value in candidates:
            for pattern in SENSITIVE_FILE_PATTERNS:
                if pattern.search(value):
                    return {
                        "permissionDecision": "deny",
                        "permissionDecisionReason": (
                            f'Blocked by deterministic hook [sensitive-path]: access to "{value}" is restricted.'
                        ),
                    }

    return {
        "permissionDecision": "allow",
        "permissionDecisionReason": "Allowed by lab guardrail policy.",
    }


def main() -> None:
    raw = sys.stdin.read().strip()
    event: dict[str, Any] = json.loads(raw) if raw else {}
    decision = evaluate_tool_event(event)

    audit_path = os.environ.get("HOOK_AUDIT_LOG")
    if audit_path:
        entry = {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "toolName": event.get("toolName") or event.get("tool_name") or "unknown",
            "decision": decision["permissionDecision"],
            "reason": decision["permissionDecisionReason"],
        }
        with open(audit_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")

    sys.stdout.write(json.dumps(decision) + "\n")


if __name__ == "__main__":
    main()
