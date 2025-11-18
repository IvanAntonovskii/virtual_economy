from fastapi import HTTPException, Request, status

# Упрощенный rate limiting для разработки
class RateLimiter:
    async def is_rate_limited(self, identifier: str, limit: int, window: int, cost: int = 1) -> bool:
        return False

rate_limiter = RateLimiter()

# Функции идентификации для rate limiting
def get_user_id_from_path(user_id: int) -> str:
    """Получает идентификатор из path параметра user_id"""
    return f"user:{user_id}"

def get_product_id_from_path(product_id: int) -> str:
    """Получает идентификатор из path параметра product_id"""
    return f"product:{product_id}"

def rate_limit(endpoint_name: str, identifier_func=None):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator
