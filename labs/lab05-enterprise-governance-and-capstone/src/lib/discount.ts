/**
 * INTENTIONAL VULNERABLE TEACHING ARTIFACT — Lab 05 Capstone Step 7 (Security).
 * Passes caller input into eval() (OWASP A03: Code Injection).
 * Ask Copilot to identify and replace eval() with strict numeric parsing.
 */
export function applyDiscount(amount: number, rule: string): number {
  // eslint-disable-next-line no-eval
  const percent = eval(rule) as number; // <-- INTENTIONAL VULNERABILITY for Capstone exercise
  const safePercent = Math.min(Math.max(percent, 0), 100);
  return Math.round(amount * (1 - safePercent / 100) * 100) / 100;
}
