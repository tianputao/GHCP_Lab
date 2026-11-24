// insecure-example.ts — INTENTIONALLY VULNERABLE TEACHING BAIT (Demo 4)
// Excluded from `tsc` (tsconfig "exclude": ["prep"]) and never imported.
// All credential strings below are OBVIOUS FAKE PLACEHOLDERS for training only.
//
// Planted vulnerabilities for Security Reviewer Agent to catch:
//   1. SQL injection via string concatenation      (OWASP A03)
//   2. Hardcoded fake credentials                  (OWASP A02 / A05)
//   3. Command injection from untrusted filename   (OWASP A03)
//   4. Stack trace & secret leaked in HTTP 500     (OWASP A05 / A09)
//   5. Missing input validation                    (OWASP A03)

import { exec } from "node:child_process";

const DEMO_DB_PASSWORD = "FAKE_DEMO_DB_PASSWORD_NOT_REAL_0001";
const DEMO_SERVICE_TOKEN = "FAKE_DEMO_SERVICE_TOKEN_DO_NOT_USE_0002";

export function searchUsers(db: { exec: (sql: string) => unknown[] }, searchTerm: string): unknown[] {
  const sql = "SELECT * FROM users WHERE name LIKE '%" + searchTerm + "%'";
  return db.exec(sql);
}

export function makeThumbnail(filename: string): void {
  exec("convert " + filename + " -resize 100x100 thumb.png");
}

export function getAccount(
  req: { params: { id: string } },
  res: { status: (n: number) => { json: (b: unknown) => void } },
): void {
  try {
    throw new Error(`DB connection failed using password ${DEMO_DB_PASSWORD}`);
  } catch (err) {
    res.status(500).json({
      error: (err as Error).stack,
      token: DEMO_SERVICE_TOKEN,
      id: req.params.id,
    });
  }
}
