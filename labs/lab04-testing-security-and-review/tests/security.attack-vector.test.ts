import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { createDemoUsersDb, searchUsersSafe, searchUsersVulnerable } from '../src/userSearchSqlDemo.js';
import { applyDiscountSafe, applyDiscountVulnerable } from '../src/discountEvalBug.js';

describe('Lab 04 — Live Security Attack Vector Proof (SQLi & Code Injection)', () => {
  it('proves SQL injection payload dumps ALL users on vulnerable query, but fails on parameterized query', () => {
    const db = createDemoUsersDb();
    try {
      const attackPayload = "' OR '1'='1' --";

      // Vulnerable version leaks all 3 users including superadmin!
      const leaked = searchUsersVulnerable(db, attackPayload);
      assert.equal(leaked.length, 3);
      assert.ok(leaked.some((u) => u.role === 'admin'));

      // Parameterized version treats payload as literal string -> 0 leaked rows
      const safe = searchUsersSafe(db, attackPayload);
      assert.equal(safe.length, 0);

      // Legitimate lookup still works on safe version
      const alice = searchUsersSafe(db, 'alice');
      assert.equal(alice.length, 1);
      assert.equal(alice[0]?.email, 'alice@example.com');
    } finally {
      db.close();
    }
  });

  it('proves eval() accepts arbitrary JS expression while hardened parser rejects it', () => {
    // Vulnerable eval() executes arithmetic/code expressions instead of plain numbers
    assert.equal(applyDiscountVulnerable(100, '5 + 5'), 90);

    // Safe version accepts plain numbers and rejects expressions/injections
    assert.equal(applyDiscountSafe(100, '10'), 90);
    assert.throws(() => applyDiscountSafe(100, '5 + 5'), RangeError);
    assert.throws(() => applyDiscountSafe(100, 'process.env.SECRET'), RangeError);
  });
});
