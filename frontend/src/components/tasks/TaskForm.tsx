"use client";

import { useState } from "react";
import type { TaskCreate, TaskPriority } from "@/types";

interface TaskFormProps {
  onSubmit: (data: TaskCreate) => Promise<void>;
}

/**
 * Form for creating new tasks.
 *
 * Reference: specs/001-todo-web-app/spec.md - US2, FR-008, FR-012, FR-015, FR-016
 */
export function TaskForm({ onSubmit }: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<TaskPriority>("medium");
  const [dueDate, setDueDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [expanded, setExpanded] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      setError("Title is required");
      return;
    }

    setError("");
    setLoading(true);

    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        due_date: dueDate ? new Date(dueDate).toISOString() : undefined,
      });

      // Reset form on success
      setTitle("");
      setDescription("");
      setPriority("medium");
      setDueDate("");
      setExpanded(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create task");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card p-4">
      {error && (
        <div className="mb-4 p-3 text-sm text-red-600 bg-red-50 rounded-lg">
          {error}
        </div>
      )}

      {/* Title input - always visible */}
      <div className="flex gap-2">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Add a new task..."
          className="input flex-1"
          onFocus={() => setExpanded(true)}
        />
        <button
          type="submit"
          disabled={loading || !title.trim()}
          className="btn btn-primary disabled:opacity-50"
        >
          {loading ? "Adding..." : "Add"}
        </button>
      </div>

      {/* Expanded options */}
      {expanded && (
        <div className="mt-4 space-y-4 border-t pt-4">
          {/* Description */}
          <div>
            <label htmlFor="description" className="label">
              Description (optional)
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Add more details..."
              className="input resize-none"
              rows={2}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            {/* Priority */}
            <div>
              <label htmlFor="priority" className="label">
                Priority
              </label>
              <select
                id="priority"
                value={priority}
                onChange={(e) => setPriority(e.target.value as TaskPriority)}
                className="input"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            {/* Due date */}
            <div>
              <label htmlFor="dueDate" className="label">
                Due date (optional)
              </label>
              <input
                id="dueDate"
                type="date"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                className="input"
              />
            </div>
          </div>

          {/* Collapse button */}
          <button
            type="button"
            onClick={() => setExpanded(false)}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Collapse
          </button>
        </div>
      )}
    </form>
  );
}
