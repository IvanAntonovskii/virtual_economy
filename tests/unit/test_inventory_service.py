import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.user_service import UserService
from app.exceptions import UserNotFoundError, DuplicateOperationError


@pytest.mark.asyncio
class TestUserService:

    async def test_add_funds_success(self, test_session):
        # Mock репозиториев
        mock_user_repo = AsyncMock()
        mock_transaction_repo = AsyncMock()

        # Настройка моков
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.balance = 100
        mock_user_repo.get_by_id.return_value = mock_user
        mock_user_repo.update_balance.return_value = mock_user

        mock_transaction_repo.get_by_idempotency_key.return_value = None
        mock_transaction_repo.create.return_value = MagicMock(id=1)

        # Создание сервиса с моками
        service = UserService(test_session)
        service.user_repo = mock_user_repo
        service.transaction_repo = mock_transaction_repo

        # Вызов метода
        result = await service.add_funds(
            user_id=1,
            amount=100,
            idempotency_key="test_key"
        )

        # Проверки
        assert result["user_id"] == 1
        assert result["new_balance"] == 100
        mock_user_repo.update_balance.assert_called_once_with(1, 100)
        mock_transaction_repo.update_status.assert_called_once_with(1, "completed")

    async def test_add_funds_user_not_found(self, test_session):
        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_id.return_value = None

        service = UserService(test_session)
        service.user_repo = mock_user_repo

        with pytest.raises(UserNotFoundError):
            await service.add_funds(999, 100, "test_key")

    async def test_add_funds_duplicate_operation(self, test_session):
        mock_transaction_repo = AsyncMock()
        mock_transaction_repo.get_by_idempotency_key.return_value = MagicMock()

        service = UserService(test_session)
        service.transaction_repo = mock_transaction_repo

        with pytest.raises(DuplicateOperationError):
            await service.add_funds(1, 100, "duplicate_key")