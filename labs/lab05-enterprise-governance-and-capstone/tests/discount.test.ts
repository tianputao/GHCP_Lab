import { test } from 'node:test';
import assert from 'node:assert/strict';
import { applyDiscount } from '../src/lib/discount.js';

// Lab 05 Capstone Step 6: INTENTIONALLY TAUTOLOGICAL TEST — fix this during the exercise!
test('applyDiscount returns a discounted amount (TAUTOLOGICAL — fix in Step 6)', () => {
  const expected = applyDiscount(100, '10'); // BAD: self-referential expectation!
  assert.equal(applyDiscount(100, '10'), expected);
});
