"use client";

import { useState } from "react";
import type { Task, TaskPriority } from "@/types";
import { TaskEditModal } from "./TaskEditModal";

interface TaskItemProps {
  task: Task;
  onToggleComplete: (task: Task) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  onUpdate: (id: string, data: { title?: string; description?: string; priority?: TaskPriority }) => Promise<void>;
}

/**
 * Individual task item component with completion toggle.
 *
 * Reference: specs/001-todo-web-app/spec.md - US2, FR-010, FR-011, FR-013
 */
export function TaskItem({
  task,
  onToggleComplete,
  onDelete,
  onUpdate,
}: TaskItemProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleToggle = async () => {
    setLoading(true);
    try {
      await onToggleComplete(task);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this task?")) return;
    setLoading(true);
    try {
      await onDelete(task.id);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveEdit = async (
    id: string,
    data: { title: string; description?: string; priority?: TaskPriority }
  ) => {
    await onUpdate(id, data);
  };

  // Check if task is overdue
  const isOverdue =
    task.due_date &&
    !task.completed &&
    new Date(task.due_date) < new Date();

  // Priority color mapping
  const priorityColors = {
    high: "bg-red-100 text-red-800",
    medium: "bg-yellow-100 text-yellow-800",
    low: "bg-green-100 text-green-800",
  };

  return (
    <div
      className={`card p-4 ${
        task.completed ? "opacity-60" : ""
      } ${loading ? "opacity-50 pointer-events-none" : ""}`}
    >
      <div className="flex items-start gap-3">
        {/* Completion checkbox */}
        <button
          onClick={handleToggle}
          className={`mt-1 w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
            task.completed
              ? "bg-blue-600 border-blue-600 text-white"
              : "border-gray-300 hover:border-blue-500"
          }`}
          aria-label={task.completed ? "Mark as incomplete" : "Mark as complete"}
        >
          {task.completed && (
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </button>

        {/* Task content */}
        <div className="flex-1 min-w-0">
          <div
            className={`${
              task.completed ? "line-through text-gray-500" : ""
            }`}
          >
            <span className="font-medium">{task.title}</span>
          </div>

          {/* Task metadata */}
          <div className="flex flex-wrap gap-2 mt-2">
            {/* Priority badge */}
            <span
              className={`text-xs px-2 py-0.5 rounded-full ${
                priorityColors[task.priority]
              }`}
            >
              {task.priority}
            </span>

            {/* Due date */}
            {task.due_date && (
              <span
                className={`text-xs ${
                  isOverdue ? "text-red-600 font-medium" : "text-gray-500"
                }`}
              >
                {isOverdue && "Overdue: "}
                {new Date(task.due_date).toLocaleDateString()}
              </span>
            )}

            {/* Description preview */}
            {task.description && (
              <span className="text-xs text-gray-400 truncate max-w-[200px]">
                {task.description}
              </span>
            )}
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2">
          {/* Edit button */}
          <button
            onClick={() => setIsModalOpen(true)}
            className="text-gray-400 hover:text-blue-600 transition-colors p-1"
            aria-label="Edit task"
            disabled={loading}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              />
            </svg>
          </button>

          {/* Delete button */}
          <button
            onClick={handleDelete}
            className="text-gray-400 hover:text-red-600 transition-colors p-1"
            aria-label="Delete task"
            disabled={loading}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Edit Modal */}
      <TaskEditModal
        task={task}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveEdit}
      />
    </div>
  );
}
