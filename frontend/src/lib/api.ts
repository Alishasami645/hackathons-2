/**
 * API client for task operations.
 * Attaches JWT token to all requests.
 *
 * Reference: specs/001-todo-web-app/contracts/tasks-api.md
 */

import type { Task, TaskCreate, TaskUpdate, TasksResponse, TaskResponse } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Get the stored access token.
 */
function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

/**
 * Set the access token in storage.
 */
export function setToken(token: string): void {
  localStorage.setItem("access_token", token);
}

/**
 * Clear the access token from storage.
 */
export function clearToken(): void {
  localStorage.removeItem("access_token");
}

/**
 * Make an authenticated API request.
 * Automatically attaches JWT token to Authorization header.
 */
async function fetchWithAuth<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // Token expired or invalid - clear and redirect to login
    clearToken();
    if (typeof window !== "undefined") {
      window.location.href = "/signin";
    }
    throw new Error("Unauthorized");
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Request failed" }));
    throw new Error(error.error || error.detail || "Request failed");
  }

  return response.json();
}

/**
 * Task API functions.
 * Reference: specs/001-todo-web-app/contracts/tasks-api.md
 */
export const tasksApi = {
  /**
   * List all tasks for the authenticated user.
   * Implements FR-009, FR-017, FR-018, FR-019
   */
  async list(params?: {
    status?: "all" | "active" | "completed";
    priority?: "all" | "low" | "medium" | "high";
    sort?: "createdAt" | "dueDate" | "priority";
    order?: "asc" | "desc";
  }): Promise<TasksResponse> {
    const searchParams = new URLSearchParams();
    if (params?.status && params.status !== "all") {
      searchParams.set("status", params.status);
    }
    if (params?.priority && params.priority !== "all") {
      searchParams.set("priority", params.priority);
    }
    if (params?.sort) {
      searchParams.set("sort", params.sort);
    }
    if (params?.order) {
      searchParams.set("order", params.order);
    }

    const query = searchParams.toString();
    return fetchWithAuth<TasksResponse>(`/api/tasks${query ? `?${query}` : ""}`);
  },

  /**
   * Create a new task.
   * Implements FR-008, FR-012, FR-015, FR-016
   */
  async create(data: TaskCreate): Promise<TaskResponse> {
    return fetchWithAuth<TaskResponse>("/api/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  /**
   * Get a single task by ID.
   */
  async get(id: string): Promise<TaskResponse> {
    return fetchWithAuth<TaskResponse>(`/api/tasks/${id}`);
  },

  /**
   * Update an existing task.
   * Implements FR-010, FR-013
   */
  async update(id: string, data: TaskUpdate): Promise<TaskResponse> {
    return fetchWithAuth<TaskResponse>(`/api/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete a task permanently.
   * Implements FR-011
   */
  async delete(id: string): Promise<{ success: boolean; message: string }> {
    return fetchWithAuth(`/api/tasks/${id}`, {
      method: "DELETE",
    });
  },

  /**
   * Toggle task completion status using PATCH endpoint.
   * Implements FR-013
   */
  async toggleComplete(taskId: string): Promise<TaskResponse> {
    return fetchWithAuth<TaskResponse>(`/api/tasks/${taskId}/toggle`, {
      method: "PATCH",
    });
  },
};
