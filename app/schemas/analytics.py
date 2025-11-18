from pydantic import BaseModel
from typing import List, Dict

class PopularProduct(BaseModel):
    product_id: int
    product_name: str
    purchase_count: int

class PopularProductsResponse(BaseModel):
    days: int
    limit: int
    products: List[PopularProduct]

class RevenueStats(BaseModel):
    period_days: int
    total_revenue: int
