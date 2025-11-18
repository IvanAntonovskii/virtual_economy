from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.transaction_repository import TransactionRepository
from app.core.cache import cache_manager
from app.exceptions import (
    ProductNotFoundError,
    UserNotFoundError,
    InsufficientFundsError,
    DuplicatePurchaseError
)
from sqlalchemy.ext.asyncio import AsyncSession
import json
import time


class ProductService:
    def __init__(self, session: AsyncSession):
        self.product_repo = ProductRepository(session)
        self.user_repo = UserRepository(session)
        self.inventory_repo = InventoryRepository(session)
        self.transaction_repo = TransactionRepository(session)

    async def purchase_product(self, user_id: int, product_id: int) -> dict:
        # Проверка существования пользователя и товара
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        product = await self.product_repo.get_by_id(product_id)
        if not product or not product.is_active:
            raise ProductNotFoundError(product_id)

        # Проверка баланса
        if user.balance < product.price:
            raise InsufficientFundsError(user.balance, product.price)

        # Для permanent товаров проверяем дубликаты
        if product.type == "permanent":
            existing_item = await self.inventory_repo.get_user_product(user_id, product_id)
            if existing_item:
                raise DuplicatePurchaseError("Permanent product already owned")

        # Создание транзакции
        transaction = await self.transaction_repo.create(
            user_id=user_id,
            product_id=product_id,
            amount=-product.price,  # Отрицательная сумма для списания
            idempotency_key=f"purchase_{user_id}_{product_id}_{int(time.time())}"
        )

        try:
            # Списание средств
            await self.user_repo.update_balance(user_id, -product.price)

            # Добавление в инвентарь
            if product.type == "consumable":
                await self.inventory_repo.add_consumable(user_id, product_id)
            else:
                await self.inventory_repo.add_permanent(user_id, product_id)

            # Подтверждение транзакции
            await self.transaction_repo.update_status(transaction.id, "completed")

            return {
                "user_id": user_id,
                "product_id": product_id,
                "new_balance": user.balance - product.price,
                "transaction_id": transaction.id
            }

        except Exception as e:
            await self.transaction_repo.update_status(transaction.id, "failed")
            raise e