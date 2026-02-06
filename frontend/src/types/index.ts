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

// Chat types (Phase III - Chatbot)
export type MessageRole = "user" | "assistant" | "system";

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface Conversation {
  id: string;
  user_id: string;
  title?: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationWithMessages extends Conversation {
  messages: Message[];
}

export interface ChatResponse {
  conversation_id: string;
  message: Message;
  task_actions?: Array<{
    tool: string;
    input: Record<string, unknown>;
    result: Record<string, unknown>;
  }>;
}
