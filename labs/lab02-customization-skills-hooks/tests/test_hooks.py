"""Tests for Lab 02 deterministic preToolUse Hook Guardrails."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

HOOK_SCRIPT = Path(__file__).resolve().parent.parent / "prep" / "hooks" / "guard_tools.py"


def run_hook(event: dict[str, Any]) -> dict[str, str]:
    res = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT)],
        input=json.dumps(event),
        text=True,
        capture_output=True,
        check=False,
    )
    assert res.returncode == 0, f"Hook process failed: {res.stderr}"
    parsed = json.loads(res.stdout.strip())
    assert isinstance(parsed, dict)
    return {str(k): str(v) for k, v in parsed.items()}


def test_blocks_destructive_rm_rf() -> None:
    decision = run_hook({"toolName": "bash", "toolArgs": {"command": "rm -rf /tmp/project"}})
    assert decision["permissionDecision"] == "deny"
    assert "destructive-rm" in decision["permissionDecisionReason"]


def test_blocks_git_push_force() -> None:
    decision = run_hook(
        {"toolName": "run_in_terminal", "toolArgs": {"command": "git push origin main --force"}}
    )
    assert decision["permissionDecision"] == "deny"
    assert "force-push" in decision["permissionDecisionReason"]


def test_blocks_reading_sensitive_env_and_secrets() -> None:
    env_decision = run_hook(
        {"toolName": "read_file", "toolArgs": {"filePath": "/workspace/.env.production"}}
    )
    assert env_decision["permissionDecision"] == "deny"

    secret_decision = run_hook(
        {"toolName": "view", "toolArgs": {"path": "secrets/api-keys.txt"}}
    )
    assert secret_decision["permissionDecision"] == "deny"


def test_allows_safe_dev_commands_and_source_reads() -> None:
    cmd_decision = run_hook(
        {"toolName": "bash", "toolArgs": {"command": "uv run mypy src api && uv run pytest"}}
    )
    assert cmd_decision["permissionDecision"] == "allow"

    file_decision = run_hook(
        {"toolName": "read_file", "toolArgs": {"filePath": "src/repositories/task_repository.py"}}
    )
    assert file_decision["permissionDecision"] == "allow"
