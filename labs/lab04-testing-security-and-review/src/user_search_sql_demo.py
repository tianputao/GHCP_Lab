"""Live SQLite SQL Injection vs Parameterized Query Demo (Python stdlib sqlite3)."""

from __future__ import annotations

import sqlite3
from typing import TypedDict


class UserRow(TypedDict):
    id: int
    username: str
    role: str
    email: str


def create_demo_users_db() -> sqlite3.Connection:
    """Create an in-memory SQLite database seeded with normal and privileged users."""
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT NOT NULL
        );
        INSERT INTO users (username, role, email) VALUES
            ('alice', 'member', 'alice@example.com'),
            ('bob', 'member', 'bob@example.com'),
            ('superadmin', 'admin', 'admin@example.com');
        """
    )
    return conn


def _rows_to_dicts(rows: list[tuple[int, str, str, str]]) -> list[UserRow]:
    return [
        {"id": row[0], "username": row[1], "role": row[2], "email": row[3]}
        for row in rows
    ]


def search_users_vulnerable(conn: sqlite3.Connection, username: str) -> list[UserRow]:
    """INTENTIONALLY VULNERABLE: f-string interpolation in SQL query (OWASP A03).

    Attack payload `' OR '1'='1' --` dumps all rows including `superadmin`.
    """
    sql = f"SELECT id, username, role, email FROM users WHERE username = '{username}'"
    cursor = conn.execute(sql)
    return _rows_to_dicts(cursor.fetchall())


def search_users_safe(conn: sqlite3.Connection, username: str) -> list[UserRow]:
    """SAFE REMEDIATION: Parameterized SQL query with `?` placeholder."""
    cursor = conn.execute(
        "SELECT id, username, role, email FROM users WHERE username = ?",
        (username,),
    )
    return _rows_to_dicts(cursor.fetchall())
