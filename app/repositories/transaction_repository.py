from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.transaction import Transaction
from typing import Optional, List

class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, product_id: Optional[int], amount: int, idempotency_key: str) -> Transaction:
        transaction = Transaction(
            user_id=user_id,
            product_id=product_id,
            amount=amount,
            idempotency_key=idempotency_key
        )
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def get_by_idempotency_key(self, idempotency_key: str) -> Optional[Transaction]:
        result = await self.session.execute(
            select(Transaction).where(Transaction.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none()

    async def update_status(self, transaction_id: int, status: str) -> Transaction:
        result = await self.session.execute(
            update(Transaction)
            .where(Transaction.id == transaction_id)
            .values(status=status)
            .returning(Transaction)
        )
        await self.session.commit()
        return result.scalar_one()