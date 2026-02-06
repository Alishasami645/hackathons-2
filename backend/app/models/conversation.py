"""Conversation and Message models for AI chatbot.

Phase III: AI Todo Chatbot
Reference: constitution.md - Stateless Architecture
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class MessageRole(str, Enum):
    """Message role types."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageBase(SQLModel):
    """Base message fields."""
    role: MessageRole
    content: str


class Message(MessageBase, table=True):
    """Message database model.
    
    Represents a single message in a conversation.
    Persists both user and assistant messages for context.
    
    Reference: constitution.md - Message State Persistence
    """
    __tablename__ = "messages"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True
    )
    conversation_id: uuid.UUID = Field(
        foreign_key="conversations.id",
        index=True,
        nullable=False
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MessageResponse(MessageBase):
    """Schema for message response."""
    id: uuid.UUID
    conversation_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationBase(SQLModel):
    """Base conversation fields."""
    title: Optional[str] = Field(default=None, max_length=255)


class Conversation(ConversationBase, table=True):
    """Conversation database model.
    
    Represents a chat conversation with the AI assistant.
    Tracks all messages and maintains conversation context.
    
    Reference: constitution.md - Conversation State Persistence
    """
    __tablename__ = "conversations"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        index=True,
        nullable=False
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationResponse(ConversationBase):
    """Schema for conversation response."""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    """Conversation with all messages."""
    messages: list[MessageResponse] = []


class ChatRequest(SQLModel):
    """Schema for chat message request.
    
    User sends a message and optionally a conversation ID.
    If conversation_id is None, a new conversation is created.
    """
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: Optional[uuid.UUID] = None


class ChatResponse(SQLModel):
    """Schema for chat message response.
    
    Contains the assistant's response and updated conversation.
    """
    conversation_id: uuid.UUID
    message: MessageResponse
    task_actions: Optional[list[dict]] = None  # Actions performed by agent
