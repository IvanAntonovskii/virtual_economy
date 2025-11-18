from sqlalchemy import Column, Integer, String, Boolean, Enum
from app.core.database import Base
import enum

class ProductType(str, enum.Enum):
    CONSUMABLE = "consumable"
    PERMANENT = "permanent"

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Integer, nullable=False)
    type = Column(Enum(ProductType), nullable=False)
    is_active = Column(Boolean, default=True)