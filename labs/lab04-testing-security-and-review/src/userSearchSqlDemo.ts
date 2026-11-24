import { DatabaseSync } from 'node:sqlite';

export interface UserRow {
  id: number;
  username: string;
  role: string;
  email: string;
}

/**
 * Creates an in-memory SQLite database (zero native C++ build needed on Node 22.5+/24)
 * seeded with normal and privileged users for live SQL injection demonstrations.
 */
export function createDemoUsersDb(): DatabaseSync {
  const db = new DatabaseSync(':memory:');
  db.exec(`
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
  `);
  return db;
}

/**
 * INTENTIONALLY VULNERABLE: String interpolation in SQL query (OWASP A03).
 * Attack payload `' OR '1'='1' --` leaks all rows including `superadmin`.
 */
export function searchUsersVulnerable(db: DatabaseSync, username: string): UserRow[] {
  const sql = `SELECT id, username, role, email FROM users WHERE username = '${username}'`;
  return db.prepare(sql).all() as unknown as UserRow[];
}

/**
 * SAFE REMEDIATION: Parameterized SQL query with `?` placeholder.
 */
export function searchUsersSafe(db: DatabaseSync, username: string): UserRow[] {
  const stmt = db.prepare(
    'SELECT id, username, role, email FROM users WHERE username = ?',
  );
  return stmt.all(username) as unknown as UserRow[];
}
