import type { Task } from './types.js';

const PRIORITIES: ReadonlyArray<Task['priority']> = ['low', 'medium', 'high'];
const STATUSES: ReadonlyArray<Task['status']> = ['todo', 'in_progress', 'done'];

/**
 * Generates deterministic seeded tasks so pagination and filtering exercises
 * behave identically on every machine and every run.
 */
export function createSeedTasks(count = 25): Task[] {
  const baseMs = Date.parse('2026-10-01T09:00:00.000Z');
  const tasks: Task[] = [];
  for (let i = 1; i <= count; i += 1) {
    const id = `task-${String(i).padStart(3, '0')}`;
    tasks.push({
      id,
      title: `Work item #${i}: Implement module checkpoint ${i}`,
      status: STATUSES[i % STATUSES.length] ?? 'todo',
      priority: PRIORITIES[i % PRIORITIES.length] ?? 'medium',
      createdAt: new Date(baseMs + i * 60_000).toISOString(),
    });
  }
  return tasks;
}

export class TaskStore {
  private tasks: Task[];

  constructor(initialTasks: Task[] = createSeedTasks(25)) {
    this.tasks = initialTasks.map((t) => ({ ...t }));
  }

  listAll(): Task[] {
    return this.tasks.map((t) => ({ ...t }));
  }

  findById(id: string): Task | undefined {
    const item = this.tasks.find((t) => t.id === id);
    return item ? { ...item } : undefined;
  }

  create(title: string, priority: Task['priority'] = 'medium'): Task {
    const nextNum = this.tasks.length + 1;
    const task: Task = {
      id: `task-${String(nextNum).padStart(3, '0')}`,
      title,
      status: 'todo',
      priority,
      createdAt: new Date().toISOString(),
    };
    this.tasks.push(task);
    return { ...task };
  }

  update(
    id: string,
    patch: Partial<Pick<Task, 'title' | 'status' | 'priority'>>,
  ): Task | undefined {
    const target = this.tasks.find((t) => t.id === id);
    if (!target) return undefined;
    if (patch.title !== undefined) target.title = patch.title;
    if (patch.status !== undefined) target.status = patch.status;
    if (patch.priority !== undefined) target.priority = patch.priority;
    return { ...target };
  }

  delete(id: string): boolean {
    const before = this.tasks.length;
    this.tasks = this.tasks.filter((t) => t.id !== id);
    return this.tasks.length < before;
  }
}
