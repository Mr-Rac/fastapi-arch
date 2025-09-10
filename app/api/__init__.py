from fastapi import APIRouter

from app.api.routes import (
    auth,
    user,
)

__all__ = ["api_router"]

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(user.router)
