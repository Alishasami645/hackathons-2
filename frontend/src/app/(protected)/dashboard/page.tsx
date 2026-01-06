"use client";

import { useEffect, useState, useCallback } from "react";
import { tasksApi } from "@/lib/api";
import { TaskForm } from "@/components/tasks/TaskForm";
import { TaskList } from "@/components/tasks/TaskList";
import { TaskFilters } from "@/components/tasks/TaskFilters";
import type { Task, TaskCreate } from "@/types";

/**
 * Dashboard page - main task management interface.
 *
 * Reference: specs/001-todo-web-app/spec.md - US2, US3
 */
export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Filters
  const [status, setStatus] = useState("all");
  const [priority, setPriority] = useState("all");
  const [sort, setSort] = useState("createdAt");

  // Fetch tasks with current filters
  const fetchTasks = useCallback(async () => {
    try {
      setError("");
      const response = await tasksApi.list({
        status: status as "all" | "active" | "completed",
        priority: priority as "all" | "low" | "medium" | "high",
        sort: sort as "createdAt" | "dueDate" | "priority",
        order: "desc",
      });
      setTasks(response.tasks);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setLoading(false);
    }
  }, [status, priority, sort]);

  // Initial load and filter changes
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // Create task handler
  const handleCreateTask = async (data: TaskCreate) => {
    const response = await tasksApi.create(data);
    // Add new task to the top of the list
    setTasks((prev) => [response.task, ...prev]);
  };

  // Toggle complete handler (FR-013)
  const handleToggleComplete = async (task: Task) => {
    const response = await tasksApi.toggleComplete(task.id);
    setTasks((prev) =>
      prev.map((t) => (t.id === task.id ? response.task : t))
    );
  };

  // Delete handler (FR-011)
  const handleDelete = async (id: string) => {
    await tasksApi.delete(id);
    setTasks((prev) => prev.filter((t) => t.id !== id));
  };

  // Update handler (FR-010, FR-012)
  const handleUpdate = async (
    id: string,
    data: { title?: string; description?: string; priority?: "low" | "medium" | "high" }
  ) => {
    const response = await tasksApi.update(id, data);
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? response.task : t))
    );
  };

  // Count stats
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter((t) => t.completed).length;
  const activeTasks = totalTasks - completedTasks;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">My Tasks</h1>
        <p className="text-gray-600 mt-1">
          {activeTasks} active, {completedTasks} completed
        </p>
      </div>

      {/* Error display */}
      {error && (
        <div className="p-4 text-red-600 bg-red-50 rounded-lg">
          {error}
          <button
            onClick={fetchTasks}
            className="ml-4 text-sm underline hover:no-underline"
          >
            Retry
          </button>
        </div>
      )}

      {/* Create task form */}
      <TaskForm onSubmit={handleCreateTask} />

      {/* Filters */}
      <TaskFilters
        status={status}
        priority={priority}
        sort={sort}
        onStatusChange={setStatus}
        onPriorityChange={setPriority}
        onSortChange={setSort}
      />

      {/* Task list */}
      <TaskList
        tasks={tasks}
        loading={loading}
        onToggleComplete={handleToggleComplete}
        onDelete={handleDelete}
        onUpdate={handleUpdate}
      />
    </div>
  );
}
