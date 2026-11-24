import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { calculateDiscount } from '../src/calculateDiscount.js';

describe('Lab 04 — Real vs Tautological Tests', () => {
  it('TAUTOLOGICAL ANTI-PATTERN (always passes, proves nothing — inspect in Lab 04)', () => {
    // BAD: computes "expected" by calling the exact same function under test!
    const expected = calculateDiscount(100, 15, 20, 50);
    assert.equal(calculateDiscount(100, 15, 20, 50), expected);
  });

  it('REAL TEST: enforces minOrder threshold, normal discount, maxCap, and error paths', () => {
    assert.equal(calculateDiscount(40, 20, 50, 50), 0);
    assert.equal(calculateDiscount(100, 15, 50, 50), 15);
    assert.equal(calculateDiscount(500, 30, 50, 50), 50);
    assert.throws(() => calculateDiscount(100, 120, 50, 0), RangeError);
    assert.throws(() => calculateDiscount(Number.NaN, 10, 50, 0), TypeError);
  });
});
