from datetime import datetime

from pydantic import EmailStr
from sqlmodel import SQLModel, Field


class UserCreate(SQLModel):
    username: str = Field(unique=True, index=True, max_length=255)
    password: str = Field(min_length=6, max_length=128)
    email: EmailStr | None = Field(default=None, unique=True, index=True, max_length=255)


class UserUpdate(SQLModel):
    username: str = Field(unique=True, index=True, max_length=255)
    password: str | None = Field(default=None, min_length=6, max_length=128)
    email: EmailStr | None = Field(default=None, unique=True, index=True, max_length=255)


class UserPublic(SQLModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
