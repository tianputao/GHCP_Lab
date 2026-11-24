export type TaskStatus = 'todo' | 'in_progress' | 'done';

export interface Task {
  id: string;
  title: string;
  status: TaskStatus;
  priority: 'low' | 'medium' | 'high';
  createdAt: string;
}

export interface CreateTaskBody {
  title?: unknown;
  priority?: unknown;
}

export interface UpdateTaskBody {
  title?: unknown;
  status?: unknown;
  priority?: unknown;
}
