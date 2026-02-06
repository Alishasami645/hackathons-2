"""MCP Server for Task Operations.

This module provides a Model Context Protocol (MCP) server that exposes
task management operations through standardized tools. These tools are consumed
by the OpenAI Agents SDK to perform autonomous task operations.

Production Architecture:
- Stateless: Each tool request includes full context (user_id, auth tokens)
- Persistent: All state changes are written to PostgreSQL
- Tools: create_task, read_task, update_task, delete_task, list_tasks

Reference: specs/001-todo-web-app/spec.md - Task Management CRUD
"""
