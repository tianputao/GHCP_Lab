// db.ts — data-access layer
//
// IMPORTANT (demo note): This is an in-memory stand-in for a real SQLite database
// so the demo runs anywhere with ZERO native dependencies. The public shape mirrors
// a `better-sqlite3` table closely enough that swapping in a real database later is
// mechanical. Repository methods document the equivalent parameterized SQL in JSDoc
// so Copilot learns the "parameterized queries only — never string concatenation"
// convention from real, visible examples.

/** Values that may be bound to a query parameter. */
export type SqlValue = string | number | null;

/**
 * A minimal, typed, in-memory table.
 *
 * @typeParam Row - the stored record shape (must have a string `id`).
 */
export class InMemoryTable<Row extends { id: string }> {
  private readonly rows = new Map<string, Row>();

  /** Inserts a row. Throws if the id already exists. */
  insert(row: Row): void {
    if (this.rows.has(row.id)) {
      throw new Error(`duplicate id: ${row.id}`);
    }
    this.rows.set(row.id, structuredClone(row));
  }

  /** Returns a single row by id, or `undefined` if not present. */
  findById(id: string): Row | undefined {
    const found = this.rows.get(id);
    return found ? structuredClone(found) : undefined;
  }

  /** Returns all rows, optionally filtered by a predicate. */
  findAll(predicate?: (row: Row) => boolean): Row[] {
    const all = [...this.rows.values()].map((r) => structuredClone(r));
    return predicate ? all.filter(predicate) : all;
  }

  /** Replaces an existing row. Returns the number of rows changed (0 or 1). */
  update(row: Row): number {
    if (!this.rows.has(row.id)) {
      return 0;
    }
    this.rows.set(row.id, structuredClone(row));
    return 1;
  }

  /** Removes a row by id. Returns the number of rows changed (0 or 1). */
  remove(id: string): number {
    return this.rows.delete(id) ? 1 : 0;
  }
}
