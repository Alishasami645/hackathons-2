#!/usr/bin/env python
"""Quick script to register a test user."""
import asyncio
import sys

# Add backend to path
sys.path.insert(0, 'E:/Quarter-4/Q4/Hackathons2/todo-app/backend')

from app.config import settings
from app.models.user import UserCreate
from app.services.auth import AuthService
from app.dependencies.database import async_session, init_db

async def main():
    # Initialize database
    await init_db()
    
    # Create session
    async with async_session() as session:
        # Register test user
        user_data = UserCreate(
            email="alisha4@gmail.com",
            password="123455asdfghj"
        )
        
        try:
            result = await AuthService.register(session, user_data)
            print(f"✅ User registered successfully!")
            print(f"Email: {result.user.email}")
            print(f"Token: {result.accessToken[:50]}...")
        except ValueError as e:
            print(f"⚠ {e}")

if __name__ == "__main__":
    asyncio.run(main())
