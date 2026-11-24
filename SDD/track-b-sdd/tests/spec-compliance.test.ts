import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { createApp } from '../src/app.js';
import { runAcceptanceSuite } from '../../evaluator/acceptance-suite.js';

/**
 * Full Spec-to-Test Compliance Suite for Track B (SDD).
 * Explicitly maps every requirement REQ-01..REQ-12 from
 * `openspec/changes/add-partial-refund/specs/`.
 */
describe('Track B (SDD) — OpenSpec Compliance Verification (REQ-01..REQ-12)', async () => {
  const results = await runAcceptanceSuite(createApp);
  const byId = new Map(results.map((r) => [r.id, r]));

  const reqIds = [
    'REQ-01',
    'REQ-02',
    'REQ-03',
    'REQ-04',
    'REQ-05',
    'REQ-06',
    'REQ-07',
    'REQ-08',
    'REQ-09',
    'REQ-10',
    'REQ-11',
    'REQ-12',
  ];

  for (const id of reqIds) {
    it(`${id}: satisfies OpenSpec acceptance scenario`, () => {
      const outcome = byId.get(id);
      assert.ok(outcome, `Missing evaluation result for ${id}`);
      assert.equal(outcome.passed, true, `${id} failed: ${outcome.detail}`);
    });
  }
});
