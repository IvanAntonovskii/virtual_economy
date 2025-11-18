from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.user import User, AddFundsRequest
from app.services.user_service import UserService
from app.core.cache import cache_manager
from app.exceptions import UserNotFoundError, DuplicateOperationError
from app.core.rate_limiting import rate_limit, get_user_id_from_path

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/{user_id}/add-funds", response_model=dict)
@rate_limit("add_funds", identifier_func=lambda **kwargs: get_user_id_from_path(kwargs.get('user_id')))
async def add_funds(
        request: Request,
        user_id: int,
        request_data: AddFundsRequest,
        db: AsyncSession = Depends(get_db)
):
    try:
        user_service = UserService(db)
        result = await user_service.add_funds(
            user_id=user_id,
            amount=request_data.amount,
            idempotency_key=request_data.idempotency_key
        )
        return result
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except DuplicateOperationError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This operation has already been processed"
        )


@router.get("/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        from app.repositories.user_repository import UserRepository
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "balance": user.balance,
            "created_at": user.created_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))