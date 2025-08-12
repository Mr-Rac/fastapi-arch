import inspect
from functools import wraps


def skip_auth():
    def decorator(func):
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

        setattr(wrapper, "_skip_auth", True)
        return wrapper

    return decorator
