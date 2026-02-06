import random
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter(prefix="/api/chat", tags=["chat"])

# In-memory storage (replace with DB in production)
conversations: Dict[str, List[Dict[str, str]]] = {}
tasks: Dict[str, List[str]] = {}  # Tasks per user

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    message: str

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(user_id: str, chat_msg: ChatMessage):
    """Chat endpoint with task handling and friendly responses."""
    msg = chat_msg.message.strip()
    msg_lower = msg.lower()

    # Ensure user has conversation and tasks
    conversations.setdefault(user_id, [])
    tasks.setdefault(user_id, [])

    # Rule-based task commands
    if msg_lower.startswith("task add"):
        task_name = msg[8:].strip()  # remove "task add"
        if not task_name:
            reply = "❌ Please provide a task name to add."
        else:
            tasks[user_id].append(task_name)
            reply = f"✅ Task added: {task_name}"

    elif msg_lower.startswith("task delete"):
        task_name = msg[11:].strip()  # remove "task delete"
        if not task_name:
            reply = "❌ Please provide a task name to delete."
        elif task_name in tasks[user_id]:
            tasks[user_id].remove(task_name)
            reply = f"🗑 Task deleted: {task_name}"
        else:
            reply = f"❌ Task not found: {task_name}"


    elif msg_lower in ["hello", "hi"]:
        replies = [
        "Hey 👋 Ready to manage your tasks today?",
        "Hello 😊 Tell me which task you want to add or delete.",
        "Hi there! 📝 I can help you organize your todo list.",
        "Welcome back 👋 What’s the next task?",
        "Hello! 💡 Try: task add Study",
        "Hi 😄 Your Todo Assistant is ready!"
        ]
        reply = random.choice(replies)



    elif msg_lower == "list tasks":
        user_tasks = tasks[user_id]
        if user_tasks:
            reply = "📝 Your tasks:\n" + "\n".join([f"- {t}" for t in user_tasks])
        else:
            reply = "You have no tasks yet."

    elif msg_lower == "clear tasks":
        tasks[user_id] = []
        reply = "✅ All tasks cleared."

    else:
        # Default fallback
        reply = f"🤖 You said: {msg}"

    # Save conversation
    conversations[user_id].append({"user": msg, "bot": reply})

    return {"message": reply}
