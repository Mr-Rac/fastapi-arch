from .auth import router as auth_router

__all__ = ["routers"]

routers = [
    auth_router,  # 鉴权
]
