"""Side-by-side scorecard comparing Track A (Vibe Coding) vs Track B (SDD)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from evaluator.acceptance_suite import run_acceptance_suite
from track_a_vibe_coding.src.app import create_app as create_vibe_app
from track_b_sdd.src.app import create_app as create_sdd_app

SDD_ROOT = Path(__file__).resolve().parent.parent


def check_spec_traceability() -> tuple[list[str], list[str]]:
    refund_spec = (SDD_ROOT / "openspec/changes/add-partial-refund/specs/refunds/spec.md").read_text(
        encoding="utf-8"
    )
    order_spec = (SDD_ROOT / "openspec/changes/add-partial-refund/specs/orders/spec.md").read_text(
        encoding="utf-8"
    )
    compliance_test = (SDD_ROOT / "track_b_sdd/tests/test_spec_compliance.py").read_text(
        encoding="utf-8"
    )

    spec_reqs = sorted(set(re.findall(r"\bREQ-\d{2}\b", f"{refund_spec}\n{order_spec}")))
    missing = [req for req in spec_reqs if req not in compliance_test]
    return spec_reqs, missing


def main() -> None:
    print("================================================================================")
    print("  SDD vs Vibe Coding — Automated Enterprise Acceptance Scorecard (12 Contracts)")
    print("================================================================================\n")

    vibe_results = run_acceptance_suite(create_vibe_app)
    sdd_results = run_acceptance_suite(create_sdd_app)

    vibe_passed = sum(1 for r in vibe_results if r.passed)
    sdd_passed = sum(1 for r in sdd_results if r.passed)

    print("| REQ    | Enterprise Requirement                                       | Vibe Coding | SDD (OpenSpec) |")
    print("|--------|--------------------------------------------------------------|-------------|----------------|")
    for v, s in zip(vibe_results, sdd_results, strict=True):
        title = s.title[:60].ljust(60)
        v_mark = " PASS ✅    " if v.passed else " FAIL ❌    "
        s_mark = " PASS ✅       " if s.passed else " FAIL ❌       "
        print(f"| {s.id} | {title} |{v_mark}|{s_mark}|")

    print("\n--- Why Vibe Coding Failed (despite its own test_basic.py passing!) ---")
    for r in vibe_results:
        if not r.passed:
            print(f"  ❌ [{r.id}] {r.detail}")

    spec_reqs, missing_in_tests = check_spec_traceability()
    print("\n--- OpenSpec Traceability Check ---")
    print(f"  Requirements defined in OpenSpec delta: {len(spec_reqs)} ({', '.join(spec_reqs)})")
    print(f"  Missing in SDD compliance tests:        {len(missing_in_tests)}")

    print("\n================================================================================")
    print(f"  SCORE SUMMARY:  Track A (Vibe Coding) = {vibe_passed}/12   |   Track B (SDD) = {sdd_passed}/12")
    print("================================================================================\n")

    if sdd_passed != 12 or missing_in_tests:
        print("❌ SDD Track B must satisfy 12/12 acceptance criteria and 100% REQ traceability!", file=sys.stderr)
        sys.exit(1)
    if vibe_passed >= 10:
        print("❌ Vibe Coding baseline unexpectedly passed too many checks — verify demo contrast.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
