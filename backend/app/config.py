"""Application configuration.

Loads settings from environment variables.
Reference: specs/001-todo-web-app/plan.md - Technical Context
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "sqlite:///./test.db"

    # JWT
    jwt_secret: str = "ee8e24f2-f7f4-4885-9807-dc600fb3e4d5"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore" 


settings = Settings()
