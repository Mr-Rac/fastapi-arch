from datetime import datetime

from pydantic import EmailStr
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(..., unique=True, index=True, max_length=255)
    password: str = Field(..., max_length=128)
    email: EmailStr | None = Field(default=None, unique=True, index=True, max_length=255)
    created_at: datetime | None = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
