"use client";

interface TaskFiltersProps {
  status: string;
  priority: string;
  sort: string;
  onStatusChange: (status: string) => void;
  onPriorityChange: (priority: string) => void;
  onSortChange: (sort: string) => void;
}

/**
 * Filter and sort controls for tasks.
 *
 * Reference: specs/001-todo-web-app/spec.md - US3, FR-017, FR-018, FR-019
 */
export function TaskFilters({
  status,
  priority,
  sort,
  onStatusChange,
  onPriorityChange,
  onSortChange,
}: TaskFiltersProps) {
  return (
    <div className="flex flex-wrap gap-4 items-center">
      {/* Status filter */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-600">Status:</span>
        <div className="flex rounded-lg overflow-hidden border border-gray-300">
          {["all", "active", "completed"].map((s) => (
            <button
              key={s}
              onClick={() => onStatusChange(s)}
              className={`px-3 py-1 text-sm capitalize ${
                status === s
                  ? "bg-blue-600 text-white"
                  : "bg-white text-gray-700 hover:bg-gray-50"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Priority filter */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-600">Priority:</span>
        <select
          value={priority}
          onChange={(e) => onPriorityChange(e.target.value)}
          className="text-sm border border-gray-300 rounded-lg px-2 py-1"
        >
          <option value="all">All</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {/* Sort */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-600">Sort:</span>
        <select
          value={sort}
          onChange={(e) => onSortChange(e.target.value)}
          className="text-sm border border-gray-300 rounded-lg px-2 py-1"
        >
          <option value="createdAt">Date Created</option>
          <option value="dueDate">Due Date</option>
          <option value="priority">Priority</option>
        </select>
      </div>
    </div>
  );
}
