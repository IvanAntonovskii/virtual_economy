from pydantic import BaseModel, validator
from typing import Optional
from app.models.product import ProductType

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    type: ProductType

class ProductCreate(ProductBase):
    @validator('price')
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('Price cannot be negative')
        return v

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    is_active: Optional[bool] = None

class Product(ProductBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True