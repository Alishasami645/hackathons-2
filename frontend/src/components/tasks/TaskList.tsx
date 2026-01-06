"use client";

import type { Task, TaskPriority } from "@/types";
import { TaskItem } from "./TaskItem";

interface TaskListProps {
  tasks: Task[];
  onToggleComplete: (task: Task) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  onUpdate: (id: string, data: { title?: string; description?: string; priority?: TaskPriority }) => Promise<void>;
  loading?: boolean;
}

/**
 * List of tasks.
 *
 * Reference: specs/001-todo-web-app/spec.md - US2
 */
export function TaskList({
  tasks,
  onToggleComplete,
  onDelete,
  onUpdate,
  loading,
}: TaskListProps) {
  if (loading) {
    return (
      <div className="text-center py-8 text-gray-500">
        Loading tasks...
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p className="text-lg">No tasks yet</p>
        <p className="text-sm mt-1">Create your first task above!</p>
      </div>
    );
  }

  // Calculate task statistics
  const completedCount = tasks.filter(t => t.completed).length;
  const pendingCount = tasks.length - completedCount;
  const completionRate = tasks.length > 0
    ? Math.round((completedCount / tasks.length) * 100)
    : 0;

  return (
    <div className="space-y-4">
      {/* Status Summary Header */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-6">
            {/* Total Tasks */}
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-gray-400"></div>
              <span className="text-sm font-medium text-gray-700">
                Total: <span className="text-gray-900 font-bold">{tasks.length}</span>
              </span>
            </div>

            {/* Pending Tasks */}
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
              <span className="text-sm font-medium text-gray-700">
                Pending: <span className="text-yellow-700 font-bold">{pendingCount}</span>
              </span>
            </div>

            {/* Completed Tasks */}
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="text-sm font-medium text-gray-700">
                Completed: <span className="text-green-700 font-bold">{completedCount}</span>
              </span>
            </div>
          </div>

          {/* Completion Rate */}
          <div className="flex items-center gap-3">
            <div className="text-right">
              <div className="text-xs text-gray-600">Completion Rate</div>
              <div className="text-lg font-bold text-indigo-600">{completionRate}%</div>
            </div>
            <div className="w-16 h-16">
              <svg className="transform -rotate-90" viewBox="0 0 36 36">
                <circle
                  cx="18"
                  cy="18"
                  r="16"
                  fill="none"
                  stroke="#e5e7eb"
                  strokeWidth="3"
                />
                <circle
                  cx="18"
                  cy="18"
                  r="16"
                  fill="none"
                  stroke="#4f46e5"
                  strokeWidth="3"
                  strokeDasharray={`${completionRate}, 100`}
                  strokeLinecap="round"
                />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Task Items */}
      <div className="space-y-3">
        {tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            onToggleComplete={onToggleComplete}
            onDelete={onDelete}
            onUpdate={onUpdate}
          />
        ))}
      </div>
    </div>
  );
}
