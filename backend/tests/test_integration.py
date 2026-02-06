"""
Integration tests for AI Todo Chatbot.

These tests verify the complete system including:
- User authentication
- Task CRUD operations
- Chat message flow
- MCP tool execution
- Conversation history persistence
- Error handling

Run with: pytest backend/tests/test_integration.py -v
"""

import pytest
import uuid
import json
from typing import AsyncGenerator
from httpx import AsyncClient

import sys
sys.path.insert(0, 'backend')

from app.main import app
from app.config import settings
from app.dependencies.database import async_session, engine
from sqlmodel import SQLModel


# Test data
TEST_USER_EMAIL = "test-integration@example.com"
TEST_USER_PASSWORD = "test123456"


@pytest.fixture
async def db_session():
    """Create test database session."""
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    # Yield session
    async with async_session() as session:
        yield session
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
async def client() -> AsyncGenerator:
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_token(client: AsyncClient) -> str:
    """Create test user and get auth token."""
    # Sign up
    signup_response = await client.post(
        "/api/auth/signup",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
        },
    )
    assert signup_response.status_code == 200
    
    # Login
    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
        },
    )
    assert login_response.status_code == 200
    
    data = login_response.json()
    return data["access_token"]


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_signup(client: AsyncClient):
    """Test user registration."""
    response = await client.post(
        "/api/auth/signup",
        json={
            "email": "newuser@example.com",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 200
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient, auth_token: str):
    """Test duplicate email signup rejection."""
    response = await client.post(
        "/api/auth/signup",
        json={
            "email": TEST_USER_EMAIL,  # Already exists
            "password": "different123",
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login(client: AsyncClient, auth_token: str):
    """Test user login."""
    response = await client.post(
        "/api/auth/login",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


# ============================================================================
# TASK CRUD TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, auth_token: str):
    """Test creating a task."""
    response = await client.post(
        "/api/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "priority": "high",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["completed"] is False


@pytest.mark.asyncio
async def test_list_tasks(client: AsyncClient, auth_token: str):
    """Test listing tasks."""
    # Create some tasks
    for i in range(3):
        await client.post(
            "/api/tasks",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "title": f"Task {i+1}",
                "priority": "medium",
            },
        )
    
    # List tasks
    response = await client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


@pytest.mark.asyncio
async def test_list_tasks_filtered(client: AsyncClient, auth_token: str):
    """Test listing tasks with status filter."""
    # Create and complete a task
    create_response = await client.post(
        "/api/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"title": "Complete me", "priority": "medium"},
    )
    task_id = create_response.json()["id"]
    
    # Mark as complete
    await client.put(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"completed": True},
    )
    
    # List pending only
    response = await client.get(
        "/api/tasks?status=pending",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert all(task["completed"] is False for task in data)


@pytest.mark.asyncio
async def test_update_task(client: AsyncClient, auth_token: str):
    """Test updating a task."""
    # Create task
    create_response = await client.post(
        "/api/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"title": "Original", "priority": "low"},
    )
    task_id = create_response.json()["id"]
    
    # Update task
    update_response = await client.put(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "title": "Updated",
            "priority": "high",
            "completed": True,
        },
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Updated"
    assert data["priority"] == "high"
    assert data["completed"] is True


@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient, auth_token: str):
    """Test deleting a task."""
    # Create task
    create_response = await client.post(
        "/api/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"title": "Delete me", "priority": "low"},
    )
    task_id = create_response.json()["id"]
    
    # Delete task
    delete_response = await client.delete(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert delete_response.status_code == 204
    
    # Verify deleted
    get_response = await client.get(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized_task_access(client: AsyncClient):
    """Test accessing tasks without authentication."""
    response = await client.get("/api/tasks")
    assert response.status_code == 401


# ============================================================================
# CHAT CONVERSATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_create_conversation(client: AsyncClient, auth_token: str):
    """Test creating a conversation."""
    response = await client.post(
        "/api/chat/conversations",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["user_id"] is not None


@pytest.mark.asyncio
async def test_list_conversations(client: AsyncClient, auth_token: str):
    """Test listing conversations."""
    # Create a conversation
    await client.post(
        "/api/chat/conversations",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    
    # List conversations
    response = await client.get(
        "/api/chat/conversations",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_send_chat_message(client: AsyncClient, auth_token: str):
    """Test sending a chat message."""
    response = await client.post(
        "/api/chat/message",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Hello, can you add a task?",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "message" in data
    assert data["message"]["role"] == "assistant"


# ============================================================================
# MCP TOOL EXECUTION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_chat_add_task_command(client: AsyncClient, auth_token: str):
    """Test natural language add task command."""
    response = await client.post(
        "/api/chat/message",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Add a task to review documentation",
        },
    )
    assert response.status_code == 200
    data = response.json()
    
    # Verify response contains task confirmation
    assert "Added" in data["message"]["content"] or "task" in data["message"]["content"].lower()
    
    # Verify tool action
    if "task_actions" in data and data["task_actions"]:
        assert data["task_actions"][0]["tool"] == "add_task"
        assert data["task_actions"][0]["status"] == "success"


@pytest.mark.asyncio
async def test_chat_list_tasks_command(client: AsyncClient, auth_token: str):
    """Test natural language list tasks command."""
    # Create a task first
    await client.post(
        "/api/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"title": "Test task", "priority": "medium"},
    )
    
    # List via chat
    response = await client.post(
        "/api/chat/message",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Show me all my tasks",
        },
    )
    assert response.status_code == 200
    data = response.json()
    
    # Verify response mentions tasks
    assert "task" in data["message"]["content"].lower()


@pytest.mark.asyncio
async def test_chat_complete_task_command(client: AsyncClient, auth_token: str):
    """Test natural language complete task command."""
    # Create a task
    create_response = await client.post(
        "/api/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"title": "Complete me", "priority": "high"},
    )
    
    # Complete via chat
    response = await client.post(
        "/api/chat/message",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Mark the first task as complete",
        },
    )
    assert response.status_code == 200
    data = response.json()
    
    # Verify response
    assert "complete" in data["message"]["content"].lower() or "done" in data["message"]["content"].lower()


# ============================================================================
# CONVERSATION PERSISTENCE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_conversation_history_persists(client: AsyncClient, auth_token: str):
    """Test that conversation history is persisted."""
    # Send first message
    msg1_response = await client.post(
        "/api/chat/message",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"message": "Hello"},
    )
    conv_id = msg1_response.json()["conversation_id"]
    
    # Send second message to same conversation
    msg2_response = await client.post(
        "/api/chat/message",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "List all my tasks",
            "conversation_id": conv_id,
        },
    )
    assert msg2_response.status_code == 200
    
    # Get conversation with history
    history_response = await client.get(
        f"/api/chat/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert history_response.status_code == 200
    data = history_response.json()
    assert len(data["messages"]) >= 4  # At least 2 requests (user + assistant each)


@pytest.mark.asyncio
async def test_user_isolation(client: AsyncClient, auth_token: str):
    """Test that users can't access other users' data."""
    # Create conversation with first user
    conv_response = await client.post(
        "/api/chat/conversations",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    conv_id = conv_response.json()["id"]
    
    # Create second user
    signup_response = await client.post(
        "/api/auth/signup",
        json={
            "email": "other-user@example.com",
            "password": "password123",
        },
    )
    
    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": "other-user@example.com",
            "password": "password123",
        },
    )
    other_token = login_response.json()["access_token"]
    
    # Try to access first user's conversation with second user's token
    access_response = await client.get(
        f"/api/chat/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    
    # Should be forbidden
    assert access_response.status_code == 404


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_invalid_token(client: AsyncClient):
    """Test that invalid token is rejected."""
    response = await client.get(
        "/api/chat/conversations",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_missing_required_fields(client: AsyncClient, auth_token: str):
    """Test that missing required fields are rejected."""
    response = await client.post(
        "/api/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={},  # Missing required 'title'
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_task_not_found(client: AsyncClient, auth_token: str):
    """Test accessing non-existent task."""
    fake_id = str(uuid.uuid4())
    response = await client.get(
        f"/api/tasks/{fake_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 404


# ============================================================================
# FULL WORKFLOW TEST
# ============================================================================

@pytest.mark.asyncio
async def test_full_workflow(client: AsyncClient, auth_token: str):
    """Test complete workflow: signup, create tasks, use chat."""
    # 1. Create tasks via API
    create1 = await client.post(
        "/api/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"title": "Buy milk", "priority": "high"},
    )
    assert create1.status_code == 200
    
    create2 = await client.post(
        "/api/tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"title": "Pay bills", "priority": "medium"},
    )
    assert create2.status_code == 200
    
    # 2. Start conversation
    chat1 = await client.post(
        "/api/chat/message",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"message": "What tasks do I have?"},
    )
    assert chat1.status_code == 200
    conv_id = chat1.json()["conversation_id"]
    
    # 3. Add task via chat
    chat2 = await client.post(
        "/api/chat/message",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Add a task to call mom",
            "conversation_id": conv_id,
        },
    )
    assert chat2.status_code == 200
    
    # 4. Mark task complete via chat
    chat3 = await client.post(
        "/api/chat/message",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Mark 'Buy milk' as done",
            "conversation_id": conv_id,
        },
    )
    assert chat3.status_code == 200
    
    # 5. Verify via API
    list_response = await client.get(
        "/api/tasks?status=completed",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    completed_tasks = list_response.json()
    assert any(task["title"] == "Buy milk" for task in completed_tasks)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
