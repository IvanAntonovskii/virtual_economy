from app.repositories.user_repository import UserRepository
from app.repositories.transaction_repository import TransactionRepository
from app.core.cache import cache_manager
from app.exceptions import UserNotFoundError, DuplicateOperationError
from sqlalchemy.ext.asyncio import AsyncSession
import json


class UserService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.transaction_repo = TransactionRepository(session)

    async def add_funds(self, user_id: int, amount: int, idempotency_key: str) -> dict:
        # Проверка существования пользователя
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Проверка идемпотентности
        existing_tx = await self.transaction_repo.get_by_idempotency_key(idempotency_key)
        if existing_tx:
            raise DuplicateOperationError("This operation has already been processed")

        # Создание транзакции
        transaction = await self.transaction_repo.create(
            user_id=user_id,
            product_id=None,  # Для пополнения баланса
            amount=amount,
            idempotency_key=idempotency_key
        )

        try:
            # Обновление баланса
            updated_user = await self.user_repo.update_balance(user_id, amount)

            # Подтверждение транзакции
            await self.transaction_repo.update_status(transaction.id, "completed")

            await cache_manager.set_user_inventory(user_id, data)
            result = await cache_manager.get_user_inventory(user_id)

            return {
                "user_id": user_id,
                "new_balance": updated_user.balance,
                "transaction_id": transaction.id
            }
        except Exception as e:
            await self.transaction_repo.update_status(transaction.id, "failed")
            raise e