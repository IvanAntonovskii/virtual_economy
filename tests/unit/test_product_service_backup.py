import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.product_service import ProductService
from app.exceptions import ProductNotFoundError, InsufficientFundsError, DuplicatePurchaseError


@pytest.mark.asyncio
class TestProductService:

    async def test_purchase_consumable_success(self, test_session):
        # Mock данных
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.balance = 1000

        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.price = 100
        mock_product.type = "consumable"
        mock_product.is_active = True

        # Mock репозиториев
        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_id.return_value = mock_user

        mock_product_repo = AsyncMock()
        mock_product_repo.get_by_id.return_value = mock_product

        mock_inventory_repo = AsyncMock()
        mock_inventory_repo.get_user_product.return_value = None

        mock_transaction_repo = AsyncMock()
        mock_transaction_repo.create.return_value = MagicMock(id=1)

        # Сервис с моками
        service = ProductService(test_session)
        service.user_repo = mock_user_repo
        service.product_repo = mock_product_repo
        service.inventory_repo = mock_inventory_repo
        service.transaction_repo = mock_transaction_repo

        # Вызов
        result = await service.purchase_product(1, 1)

        # Проверки
        assert result["user_id"] == 1
        assert result["product_id"] == 1
        mock_user_repo.update_balance.assert_called_once_with(1, -100)
        mock_inventory_repo.add_consumable.assert_called_once_with(1, 1)

    async def test_purchase_insufficient_funds(self, test_session):
        mock_user = MagicMock()
        mock_user.balance = 50

        mock_product = MagicMock()
        mock_product.price = 100
        mock_product.is_active = True

        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_id.return_value = mock_user

        mock_product_repo = AsyncMock()
        mock_product_repo.get_by_id.return_value = mock_product

        service = ProductService(test_session)
        service.user_repo = mock_user_repo
        service.product_repo = mock_product_repo

        with pytest.raises(InsufficientFundsError):
            await service.purchase_product(1, 1)

    async def test_purchase_product_not_found(self, test_session):
        # Создаем мок сессии
        mock_session = AsyncMock()

        mock_product_repo = AsyncMock()
        mock_product_repo.get_by_id.return_value = None

        service = ProductService(mock_session)  # Используем mock_session вместо test_session
        service.product_repo = mock_product_repo

        with pytest.raises(ProductNotFoundError):
            await service.purchase_product(1, 999)