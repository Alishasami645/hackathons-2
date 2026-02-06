"""MCP Server Implementation.

Initializes and exposes MCP tools for use by the OpenAI Agents SDK.
This server uses server-side tool execution (no tool definitions sent to client).

The MCP protocol allows:
1. Tools defined on this server
2. Agents (like OpenAI's) to call tools via MCP
3. All state persisted in PostgreSQL (stateless server pattern)

Reference: https://modelcontextprotocol.io/
"""

from app.mcp_server import tools


# Tool Registry: Maps tool names to their implementation
# Used by agents to discover and call available operations
TOOL_REGISTRY = {
    "create_task": tools.create_task,
    "read_task": tools.read_task,
    "update_task": tools.update_task,
    "delete_task": tools.delete_task,
    "list_tasks": tools.list_tasks,
}


def get_tool_definitions() -> list[dict]:
    """Return MCP tool definitions for client discovery.

    These definitions tell agents what tools are available and how to call them.
    Format complies with MCP specification for tool schemas.

    Returns:
        List of tool definition dicts with name, description, and input schema
    """
    return [
        {
            "name": "create_task",
            "description": "Create a new task for the authenticated user",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Task title (max 255 chars)",
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional task description",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Task priority level",
                    },
                    "due_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Optional due date (ISO 8601)",
                    },
                },
                "required": ["title"],
            },
        },
        {
            "name": "read_task",
            "description": "Retrieve a specific task by ID",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "Task ID to retrieve",
                    },
                },
                "required": ["task_id"],
            },
        },
        {
            "name": "update_task",
            "description": "Update one or more fields of a task",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "Task ID to update",
                    },
                    "title": {
                        "type": "string",
                        "description": "New title (optional)",
                    },
                    "description": {
                        "type": "string",
                        "description": "New description (optional)",
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "New completion status (optional)",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "New priority (optional)",
                    },
                    "due_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "New due date (optional)",
                    },
                },
                "required": ["task_id"],
            },
        },
        {
            "name": "delete_task",
            "description": "Delete a task permanently",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "Task ID to delete",
                    },
                },
                "required": ["task_id"],
            },
        },
        {
            "name": "list_tasks",
            "description": "List tasks with optional filtering and pagination",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "filter_completed": {
                        "type": "boolean",
                        "description": "Filter by completion status (optional)",
                    },
                    "filter_priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Filter by priority (optional)",
                    },
                    "sort_by": {
                        "type": "string",
                        "enum": ["created_at", "due_date", "priority"],
                        "description": "Sort field (default: created_at)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results (default: 100, max: 1000)",
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Pagination offset (default: 0)",
                    },
                },
                "required": [],
            },
        },
    ]
