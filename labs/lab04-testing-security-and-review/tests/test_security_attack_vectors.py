"""Lab 04 — Live Security Attack Vector Proof (SQLi & Code Injection)."""

from __future__ import annotations

import pytest

from src.discount_eval_bug import apply_discount_safe, apply_discount_vulnerable
from src.user_search_sql_demo import (
    create_demo_users_db,
    search_users_safe,
    search_users_vulnerable,
)


def test_sql_injection_dumps_all_users_vs_parameterized_query() -> None:
    conn = create_demo_users_db()
    try:
        attack_payload = "' OR '1'='1' --"

        # Vulnerable version leaks all 3 users including superadmin!
        leaked = search_users_vulnerable(conn, attack_payload)
        assert len(leaked) == 3
        assert any(u["role"] == "admin" for u in leaked)

        # Parameterized version treats payload as a literal string -> 0 leaked rows
        safe = search_users_safe(conn, attack_payload)
        assert len(safe) == 0

        # Legitimate lookup still works on safe version
        alice = search_users_safe(conn, "alice")
        assert len(alice) == 1
        assert alice[0]["email"] == "alice@example.com"
    finally:
        conn.close()


def test_eval_executes_expression_while_hardened_parser_rejects_it() -> None:
    # Vulnerable eval() executes arbitrary Python expressions instead of plain numbers
    assert apply_discount_vulnerable(100, "5 + 5") == 90.0

    # Safe version accepts plain numbers and rejects expressions/injections
    assert apply_discount_safe(100, "10") == 90.0
    with pytest.raises(ValueError):
        apply_discount_safe(100, "5 + 5")
    with pytest.raises(ValueError):
        apply_discount_safe(100, "__import__('os').environ")
