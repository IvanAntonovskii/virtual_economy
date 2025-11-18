from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.inventory import Inventory
from typing import Optional, List


class InventoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_product(self, user_id: int, product_id: int) -> Optional[Inventory]:
        result = await self.session.execute(
            select(Inventory)
            .where(Inventory.user_id == user_id)
            .where(Inventory.product_id == product_id)
        )
        return result.scalar_one_or_none()

    async def add_consumable(self, user_id: int, product_id: int) -> Inventory:
        # Проверяем, есть ли уже такой товар у пользователя
        existing = await self.get_user_product(user_id, product_id)

        if existing:
            # Увеличиваем количество для consumable товаров
            result = await self.session.execute(
                update(Inventory)
                .where(Inventory.id == existing.id)
                .values(quantity=Inventory.quantity + 1)
                .returning(Inventory)
            )
            await self.session.commit()
            return result.scalar_one()
        else:
            # Создаем новую запись
            inventory = Inventory(
                user_id=user_id,
                product_id=product_id,
                quantity=1
            )
            self.session.add(inventory)
            await self.session.commit()
            await self.session.refresh(inventory)
            return inventory

    async def add_permanent(self, user_id: int, product_id: int) -> Inventory:
        # Для permanent товаров создаем новую запись
        inventory = Inventory(
            user_id=user_id,
            product_id=product_id,
            quantity=1  # Для permanent товаров quantity всегда 1
        )
        self.session.add(inventory)
        await self.session.commit()
        await self.session.refresh(inventory)
        return inventory

    async def get_user_inventory(self, user_id: int) -> List[Inventory]:
        result = await self.session.execute(
            select(Inventory)
            .where(Inventory.user_id == user_id)
        )
        return result.scalars().all()

    async def use_consumable(self, user_id: int, product_id: int, quantity: int = 1) -> Optional[Inventory]:
        inventory_item = await self.get_user_product(user_id, product_id)

        if not inventory_item or inventory_item.quantity < quantity:
            return None

        if inventory_item.quantity == quantity:
            # Удаляем запись, если количество становится 0
            await self.session.delete(inventory_item)
        else:
            # Уменьшаем количество
            result = await self.session.execute(
                update(Inventory)
                .where(Inventory.id == inventory_item.id)
                .values(quantity=Inventory.quantity - quantity)
                .returning(Inventory)
            )
            inventory_item = result.scalar_one()

        await self.session.commit()
        return inventory_item