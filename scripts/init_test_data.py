import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


async def init_test_data():
    """Добавляет тестовые данные в базу"""
    from app.core.database import async_session
    from app.repositories.product_repository import ProductRepository
    from app.repositories.user_repository import UserRepository

    async with async_session() as session:
        # Тестовые товары
        product_repo = ProductRepository(session)

        test_products = [
            {
                "name": "Буст на день",
                "description": "Увеличивает доход на 50% на 24 часа",
                "price": 100,
                "type": "consumable",
                "is_active": True
            },
            {
                "name": "Премиум-статус",
                "description": "Постоянный доступ к премиум-контенту",
                "price": 500,
                "type": "permanent",
                "is_active": True
            },
            {
                "name": "Набор ресурсов",
                "description": "Пакет из 1000 игровых ресурсов",
                "price": 200,
                "type": "consumable",
                "is_active": True
            }
        ]

        for product_data in test_products:
            await product_repo.create(product_data)
            print(f"✅ Создан товар: {product_data['name']}")

        # Тестовый пользователь
        user_repo = UserRepository(session)
        test_user = await user_repo.create({
            "username": "test_user",
            "email": "test@example.com",
            "balance": 1000
        })

        print(f"✅ Создан пользователь: {test_user.username}")
        print("🎉 Тестовые данные успешно добавлены!")


if __name__ == "__main__":
    asyncio.run(init_test_data())