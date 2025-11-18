import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


async def init_database():
    """Инициализирует базу данных и создает таблицы"""
    print("🔄 Инициализация базы данных...")

    from app.core.database import engine, Base
    from app.models.user import User
    from app.models.product import Product
    from app.models.inventory import Inventory
    from app.models.transaction import Transaction

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Все таблицы успешно созданы!")


if __name__ == "__main__":
    asyncio.run(init_database())