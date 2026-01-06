/**
 * Type definitions for the Todo Web Application.
 * Reference: specs/001-todo-web-app/data-model.md
 */

export type TaskPriority = "low" | "medium" | "high";

export interface Task {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  priority: TaskPriority;
  due_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: TaskPriority;
  due_date?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string | null;
  completed?: boolean;
  priority?: TaskPriority;
  due_date?: string | null;
}

export interface TasksResponse {
  tasks: Task[];
  count: number;
}

export interface TaskResponse {
  task: Task;
}

export interface User {
  id: string;
  email: string;
  name?: string;
}
