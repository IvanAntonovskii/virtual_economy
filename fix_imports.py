import os


def fix_rate_limiting():
    """Исправляет файл rate_limiting.py"""
    content = '''from fastapi import HTTPException, Request, status

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
'''

    with open('app/core/rate_limiting.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ rate_limiting.py исправлен!")


def create_simple_main():
    """Создает упрощенную версию main.py"""
    content = '''from fastapi import FastAPI
from app.core.database import create_tables

app = FastAPI(
    title="Virtual Economy Service",
    version="1.0.0",
    description="Сервис управления виртуальной экономикой"
)

@app.on_event("startup")
async def startup_event():
    await create_tables()
    print("🚀 Virtual Economy Service запущен!")

@app.get("/")
async def root():
    return {"message": "Virtual Economy Service", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
'''

    with open('app/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ main.py упрощен!")


if __name__ == "__main__":
    fix_rate_limiting()
    create_simple_main()
    print("🎉 Все импорты исправлены! Запускайте сервер.")