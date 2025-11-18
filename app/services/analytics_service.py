from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.transaction import Transaction
from app.models.product import Product
from typing import List, Dict
from datetime import datetime, timedelta

class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_popular_products(self, days: int = 7, limit: int = 5) -> List[Dict]:
        """Топ товаров по количеству покупок за указанный период"""
        start_date = datetime.now() - timedelta(days=days)

        result = await self.session.execute(
            select(
                Product.id,
                Product.name,
                func.count(Transaction.id).label('purchase_count')
            )
            .join(Transaction, Transaction.product_id == Product.id)
            .where(Transaction.created_at >= start_date)
            .where(Transaction.status == 'completed')
            .group_by(Product.id, Product.name)
            .order_by(desc('purchase_count'))
            .limit(limit)
        )

        popular_products = result.all()

        return [
            {
                "product_id": product_id,
                "product_name": product_name,
                "purchase_count": purchase_count
            }
            for product_id, product_name, purchase_count in popular_products
        ]
