from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.cache import cache_manager
from app.services.inventory_service import InventoryService
from app.core.rate_limiting import rate_limit, get_user_id_from_path

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/users/{user_id}/items")
@rate_limit("inventory", identifier_func=lambda **kwargs: get_user_id_from_path(kwargs.get('user_id')))
async def get_user_inventory(
        request: Request,
        user_id: int,
        db: AsyncSession = Depends(get_db)
):
    try:
        # Проверка кэша
        cached = await cache_manager.get_user_inventory(user_id)
        if cached:
            return {"cached": True, "data": cached}

        service = InventoryService(db)
        inventory = await service.get_user_inventory(user_id)

        # Кэшируем результат
        await cache_manager.set_user_inventory(user_id, inventory)

        return {"cached": False, "data": inventory}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/items/{item_id}/use")
@rate_limit("use_product", identifier_func=lambda **kwargs: get_user_id_from_path(kwargs.get('user_id')))
async def use_consumable_item(
        request: Request,
        item_id: int,
        user_id: int,
        quantity: int = 1,
        db: AsyncSession = Depends(get_db)
):
    try:
        service = InventoryService(db)
        result = await service.use_consumable_item(user_id, item_id, quantity)

        # Инвалидируем кэш инвентаря
        await cache_manager.invalidate_user_inventory(user_id)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))