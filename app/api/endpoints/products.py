from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.product_service import ProductService
from app.exceptions import (
    ProductNotFoundError,
    UserNotFoundError,
    InsufficientFundsError,
    DuplicatePurchaseError
)
from app.core.rate_limiting import rate_limit, get_user_id_from_path

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/{product_id}/purchase", response_model=dict)
@rate_limit("purchase", identifier_func=lambda **kwargs: get_user_id_from_path(kwargs.get('user_id')))
async def purchase_product(
        request: Request,
        product_id: int,
        user_id: int,
        db: AsyncSession = Depends(get_db)
):
    try:
        product_service = ProductService(db)
        result = await product_service.purchase_product(user_id, product_id)
        return result
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except ProductNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactive"
        )
    except InsufficientFundsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient funds: balance {e.balance}, required {e.required}"
        )
    except DuplicatePurchaseError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permanent product already owned"
        )


@router.get("/")
async def get_products(db: AsyncSession = Depends(get_db)):
    try:
        from app.repositories.product_repository import ProductRepository
        product_repo = ProductRepository(db)
        products = await product_repo.get_active_products()

        return {
            "products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "price": p.price,
                    "type": p.type,
                    "is_active": p.is_active
                }
                for p in products
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))