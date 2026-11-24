/**
 * INTENTIONAL VULNERABLE TEACHING ARTIFACT (OWASP A03: Code Injection).
 * DO NOT copy into production code.
 *
 * Lab 04 Exercise 2: Ask Copilot to identify why `applyDiscountVulnerable` is
 * exploitable, fix it safely (numeric parsing + strict validation), and add
 * regression tests rejecting expression payloads like "10; process.exit(1)".
 */
export function applyDiscountVulnerable(amount: number, rule: string): number {
  // Intentionally unsafe dynamic evaluation for security training
  // eslint-disable-next-line no-eval
  const percent = Number(eval(rule));
  const safePercent = Math.min(Math.max(percent, 0), 100);
  return Math.round(amount * (1 - safePercent / 100) * 100) / 100;
}

/**
 * Reference hardened implementation for side-by-side comparison.
 */
export function applyDiscountSafe(amount: number, rule: string): number {
  if (!Number.isFinite(amount) || amount < 0) {
    throw new RangeError('amount must be a non-negative finite number');
  }
  const trimmed = rule.trim();
  if (!/^\d+(\.\d+)?$/.test(trimmed)) {
    throw new RangeError('discount rule must be a plain non-negative numeric percentage');
  }
  const percent = Number(trimmed);
  if (!Number.isFinite(percent) || percent < 0 || percent > 100) {
    throw new RangeError('discount percentage must be between 0 and 100');
  }
  return Math.round(amount * (1 - percent / 100) * 100) / 100;
}
