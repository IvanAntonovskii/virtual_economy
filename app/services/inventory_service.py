from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.exceptions import InventoryItemNotFoundError, ProductNotFoundError
from sqlalchemy.ext.asyncio import AsyncSession


class InventoryService:
    def __init__(self, session: AsyncSession):
        self.inventory_repo = InventoryRepository(session)
        self.product_repo = ProductRepository(session)

    async def get_user_inventory(self, user_id: int) -> list:
        inventory_items = await self.inventory_repo.get_user_inventory(user_id)

        result = []
        for item in inventory_items:
            product = await self.product_repo.get_by_id(item.product_id)
            if product:
                result.append({
                    "inventory_id": item.id,
                    "product_id": item.product_id,
                    "product_name": product.name,
                    "product_type": product.type,
                    "quantity": item.quantity,
                    "purchased_at": item.purchased_at.isoformat() if item.purchased_at else None
                })

        return result

    async def use_consumable_item(self, user_id: int, product_id: int, quantity: int = 1) -> dict:
        # Проверяем, что товар существует и является consumable
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(product_id)

        if product.type != "consumable":
            return {"error": "Can only use consumable products"}

        # Используем товар
        updated_item = await self.inventory_repo.use_consumable(user_id, product_id, quantity)

        if not updated_item:
            raise InventoryItemNotFoundError(f"Item not found or insufficient quantity")

        return {
            "user_id": user_id,
            "product_id": product_id,
            "remaining_quantity": 0 if updated_item is None else updated_item.quantity,
            "product_name": product.name
        }