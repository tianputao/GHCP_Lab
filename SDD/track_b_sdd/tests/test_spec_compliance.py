"""Full Spec-to-Test Compliance Suite for Track B (SDD).

Explicitly maps every requirement REQ-01..REQ-12 from
`openspec/changes/add-partial-refund/specs/`.
"""

from __future__ import annotations

import pytest

from evaluator.acceptance_suite import RequirementResult, run_acceptance_suite
from track_b_sdd.src.app import create_app

REQ_IDS = [
    "REQ-01",
    "REQ-02",
    "REQ-03",
    "REQ-04",
    "REQ-05",
    "REQ-06",
    "REQ-07",
    "REQ-08",
    "REQ-09",
    "REQ-10",
    "REQ-11",
    "REQ-12",
]


@pytest.fixture(scope="module")
def compliance_results() -> dict[str, RequirementResult]:
    results = run_acceptance_suite(create_app)
    return {r.id: r for r in results}


@pytest.mark.parametrize("req_id", REQ_IDS)
def test_sdd_track_b_satisfies_requirement(
    req_id: str,
    compliance_results: dict[str, RequirementResult],
) -> None:
    outcome = compliance_results.get(req_id)
    assert outcome is not None, f"Missing evaluation result for {req_id}"
    assert outcome.passed, f"{req_id} failed: {outcome.detail}"
