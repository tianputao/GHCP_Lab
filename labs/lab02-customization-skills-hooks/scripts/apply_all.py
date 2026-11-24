#!/usr/bin/env python3
"""Deploy all Lab 02 2026 customizations from prep/ into .github/."""

from __future__ import annotations

import shutil
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    print("Applying all Lab 02 2026 customizations from prep/ into .github/...")
    targets = [
        ("prep/copilot-instructions.md", ".github/copilot-instructions.md"),
        ("prep/api.instructions.md", ".github/instructions/api.instructions.md"),
        ("prep/skills/scaffold-feature/SKILL.md", ".github/skills/scaffold-feature/SKILL.md"),
        (
            "prep/skills/scaffold-feature/check_conventions.py",
            ".github/skills/scaffold-feature/check_conventions.py",
        ),
        ("prep/security-reviewer.agent.md", ".github/agents/security-reviewer.agent.md"),
        ("prep/hooks/guardrails.json", ".github/hooks/guardrails.json"),
        ("prep/hooks/guard_tools.py", ".github/hooks/guard_tools.py"),
    ]
    for src_rel, dst_rel in targets:
        dst = LAB_ROOT / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(LAB_ROOT / src_rel, dst)

    print("✅ Applied:")
    print("  - .github/copilot-instructions.md")
    print("  - .github/instructions/api.instructions.md")
    print("  - .github/skills/scaffold-feature/{SKILL.md,check_conventions.py}")
    print("  - .github/agents/security-reviewer.agent.md")
    print("  - .github/hooks/{guardrails.json,guard_tools.py}")
    print("\nTip: Open this folder in VS Code and run 'Chat: Open Customizations' to inspect all loaded layers.")


if __name__ == "__main__":
    main()
