// task-repository.ts — repository pattern for tasks
//
// This is the canonical "good example" Copilot should imitate when you ask it to
// scaffold new repositories (e.g. the "comments" feature in the Week 7 demo).
// Note the documented parameterized SQL on each method: `?` placeholders, never
// string concatenation. All data access is centralized here — routes never touch
// the database directly.

import { randomUUID } from "node:crypto";
import { InMemoryTable } from "../db";
import { NotFoundError } from "../errors";
import type { CreateTaskInput, Task, TaskStatus, UpdateTaskInput } from "../types";

/** Centralized data access for {@link Task} records. */
export class TaskRepository {
  private readonly table = new InMemoryTable<Task>();

  /**
   * Returns every task, optionally filtered by tag.
   *
   * @param tag - when provided, only tasks containing this tag are returned.
   * @returns the matching tasks (possibly empty).
   * @remarks Production SQL:
   *   `SELECT * FROM tasks WHERE (? IS NULL OR id IN
   *      (SELECT task_id FROM task_tags WHERE tag = ?))`
   */
  findAll(tag?: string): Task[] {
    if (tag === undefined) {
      return this.table.findAll();
    }
    return this.table.findAll((t) => t.tags.includes(tag));
  }

  /**
   * Returns a single task by id.
   *
   * @param id - the task id.
   * @returns the task.
   * @throws {NotFoundError} when no task has the given id.
   * @remarks Production SQL: `SELECT * FROM tasks WHERE id = ?`
   */
  getById(id: string): Task {
    const task = this.table.findById(id);
    if (!task) {
      throw new NotFoundError("Task", id);
    }
    return task;
  }

  /**
   * Creates a new task with server-assigned id, status, and timestamps.
   *
   * @param input - the validated creation input.
   * @returns the newly created task.
   * @remarks Production SQL:
   *   `INSERT INTO tasks (id, title, description, status, created_at, updated_at)
   *      VALUES (?, ?, ?, ?, ?, ?)`
   */
  create(input: CreateTaskInput): Task {
    const now = new Date().toISOString();
    const task: Task = {
      id: randomUUID(),
      title: input.title,
      description: input.description ?? null,
      status: "todo",
      tags: [],
      createdAt: now,
      updatedAt: now,
    };
    this.table.insert(task);
    return task;
  }

  /**
   * Applies a partial update to an existing task.
   *
   * @param id - the task id.
   * @param input - the fields to update.
   * @returns the updated task.
   * @throws {NotFoundError} when no task has the given id.
   * @remarks Production SQL:
   *   `UPDATE tasks SET title = ?, description = ?, status = ?, updated_at = ?
   *      WHERE id = ?`
   */
  update(id: string, input: UpdateTaskInput): Task {
    const existing = this.getById(id);
    const updated: Task = {
      ...existing,
      title: input.title ?? existing.title,
      description:
        input.description === undefined ? existing.description : input.description,
      status: (input.status ?? existing.status) as TaskStatus,
      updatedAt: new Date().toISOString(),
    };
    this.table.update(updated);
    return updated;
  }

  /**
   * Deletes a task by id.
   *
   * @param id - the task id.
   * @throws {NotFoundError} when no task has the given id.
   * @remarks Production SQL: `DELETE FROM tasks WHERE id = ?`
   */
  delete(id: string): void {
    const changes = this.table.remove(id);
    if (changes === 0) {
      throw new NotFoundError("Task", id);
    }
  }
}
