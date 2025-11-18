from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import create_tables
from app.core.cache import cache_manager
from app.api.endpoints import users, products, inventory, analytics, health
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Virtual Economy Service",
    version="1.0.0",
    description="Микросервис для управления виртуальной экономикой",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрация routers
app.include_router(health.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(analytics.router)


@app.on_event("startup")
async def startup_event():
    # Инициализация базы данных
    await create_tables()

    # Инициализация Redis
    await cache_manager.init_redis()

    print("🚀 Virtual Economy Service запущен!")
    print("📊 База данных: инициализирована")
    print("🔮 Redis: подключен" if cache_manager.redis else "🔮 Redis: заглушка")


@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 Virtual Economy Service остановлен")


@app.get("/")
async def root():
    return {
        "message": "Virtual Economy Service",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )