import pytest
from pydantic import ValidationError


def test_basic_schemas():
    """Тестируем базовые схемы"""
    try:
        from app.schemas.user import UserCreate
        from app.schemas.product import ProductCreate

        # Тест создания пользователя
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "balance": 1000
        }
        user = UserCreate(**user_data)
        assert user.username == "testuser"
        assert user.email == "test@example.com"

        # Тест создания продукта
        product_data = {
            "name": "Test Product",
            "description": "Test Description",
            "price": 100,
            "type": "consumable"
        }
        product = ProductCreate(**product_data)
        assert product.name == "Test Product"

        print("✓ Schemas imported successfully")

    except ImportError as e:
        pytest.fail(f"Import failed: {e}")
    except ValidationError as e:
        pytest.fail(f"Validation failed: {e}")


def test_schema_validation():
    """Тест валидации схем"""
    try:
        from app.schemas.user import UserCreate

        # Должен пройти
        valid_user = UserCreate(
            username="validuser",
            email="valid@example.com",
            balance=1000
        )
        assert valid_user.username == "validuser"

        print("✓ Schema validation passed")

    except Exception as e:
        pytest.fail(f"Schema validation test failed: {e}")