"""insecure_example.py — INTENTIONALLY VULNERABLE TEACHING BAIT (Demo 4).

Excluded from mypy/pytest and never imported.
All credential strings below are OBVIOUS FAKE PLACEHOLDERS for training only.

Planted vulnerabilities for Security Reviewer Agent to catch:
  1. SQL injection via string concatenation        (OWASP A03)
  2. Hardcoded fake credentials                    (OWASP A02 / A05)
  3. Command injection via subprocess shell=True   (OWASP A03)
  4. Traceback & secret leaked in HTTP 500 body    (OWASP A05 / A09)
  5. Missing input validation                      (OWASP A03)
"""

from __future__ import annotations

import subprocess
import traceback
from typing import Protocol

DEMO_DB_PASSWORD = "FAKE_DEMO_DB_PASSWORD_NOT_REAL_0001"
DEMO_SERVICE_TOKEN = "FAKE_DEMO_SERVICE_TOKEN_DO_NOT_USE_0002"


class FakeDb(Protocol):
    def execute(self, sql: str) -> list[dict[str, object]]: ...


def search_users(db: FakeDb, search_term: str) -> list[dict[str, object]]:
    sql = "SELECT * FROM users WHERE name LIKE '%" + search_term + "%'"
    return db.execute(sql)


def make_thumbnail(filename: str) -> None:
    subprocess.run("convert " + filename + " -resize 100x100 thumb.png", shell=True, check=False)


def get_account(account_id: str) -> tuple[int, dict[str, object]]:
    try:
        raise RuntimeError(f"DB connection failed using password {DEMO_DB_PASSWORD}")
    except Exception:
        return (
            500,
            {
                "error": traceback.format_exc(),
                "token": DEMO_SERVICE_TOKEN,
                "id": account_id,
            },
        )
