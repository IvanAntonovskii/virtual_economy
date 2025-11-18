from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.cache import cache_manager
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import PopularProductsResponse, RevenueStats
from app.core.rate_limiting import rate_limit
import json

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/popular-products", response_model=PopularProductsResponse)
@rate_limit("analytics")
async def get_popular_products(
        request: Request,
        days: int = 7,
        limit: int = 5,
        db: AsyncSession = Depends(get_db)
):
    try:
        cache_key = f"popular_products:{days}:{limit}"

        # Проверка кэша
        cached = await cache_manager.redis.get(cache_key) if cache_manager.redis else None
        if cached:
            return PopularProductsResponse(**json.loads(cached))

        service = AnalyticsService(db)
        popular_products = await service.get_popular_products(days, limit)

        response_data = {
            "days": days,
            "limit": limit,
            "products": popular_products
        }

        # Кэшируем на 1 час (если Redis настроен)
        if cache_manager.redis:
            await cache_manager.redis.setex(cache_key, 3600, json.dumps(response_data))

        return PopularProductsResponse(**response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/revenue", response_model=RevenueStats)
@rate_limit("analytics")
async def get_revenue_stats(
        request: Request,
        days: int = 30,
        db: AsyncSession = Depends(get_db)
):
    try:
        service = AnalyticsService(db)
        revenue_stats = await service.get_revenue_stats(days)

        return RevenueStats(**revenue_stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user-stats")
@rate_limit("analytics")
async def get_user_stats(
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    try:
        from sqlalchemy import select, func
        from app.models.user import User
        from app.models.transaction import Transaction

        # Общее количество пользователей
        total_users_result = await db.execute(select(func.count(User.id)))
        total_users = total_users_result.scalar()

        # Пользователи с покупками
        users_with_purchases_result = await db.execute(
            select(func.count(func.distinct(Transaction.user_id)))
            .where(Transaction.status == 'completed')
            .where(Transaction.amount < 0)
        )
        users_with_purchases = users_with_purchases_result.scalar()

        # Средний баланс
        avg_balance_result = await db.execute(select(func.avg(User.balance)))
        average_balance = avg_balance_result.scalar() or 0

        return {
            "total_users": total_users,
            "users_with_purchases": users_with_purchases,
            "average_balance": round(average_balance, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))