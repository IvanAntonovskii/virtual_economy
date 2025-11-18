from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    balance: Optional[int] = None

    @validator('balance')
    def validate_balance(cls, v):
        if v is not None and v < 0:
            raise ValueError('Balance cannot be negative')
        return v

class User(UserBase):
    id: int
    balance: int
    created_at: datetime

    class Config:
        from_attributes = True

class AddFundsRequest(BaseModel):
    amount: int
    idempotency_key: str

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        if v > 100000:  # Максимальный лимит
            raise ValueError('Amount exceeds maximum limit')
        return v