/**
 * Computes a capped monetary discount with minimum order threshold.
 * Ideal target for `/tests`, TDD, and boundary/error-path test exercises.
 */
export function calculateDiscount(
  amount: number,
  percent: number,
  maxCap: number,
  minOrder: number,
): number {
  if (
    !Number.isFinite(amount) ||
    !Number.isFinite(percent) ||
    !Number.isFinite(maxCap) ||
    !Number.isFinite(minOrder)
  ) {
    throw new TypeError('All inputs must be finite numbers');
  }

  if (amount < 0 || percent < 0 || maxCap < 0 || minOrder < 0) {
    throw new RangeError('Inputs cannot be negative');
  }

  if (percent > 100) {
    throw new RangeError('Percent cannot exceed 100');
  }

  if (amount < minOrder) {
    return 0;
  }

  const rawDiscount = (amount * percent) / 100;
  const finalDiscount = Math.min(rawDiscount, maxCap, amount);
  return Number(finalDiscount.toFixed(2));
}
