import pytest
from fastapi import status


class TestAPIEndpoints:

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"

    def test_get_products(self, client, test_data):
        response = client.get("/products")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "products" in data
        assert len(data["products"]) == 2

    def test_add_funds(self, client, test_data):
        user_id = test_data["user"].id
        payload = {
            "amount": 100,
            "idempotency_key": "test_key_123"
        }

        response = client.post(f"/users/{user_id}/add-funds", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == user_id
        assert "new_balance" in data

    def test_purchase_product(self, client, test_data):
        user_id = test_data["user"].id
        product_id = test_data["products"][0].id

        response = client.post(f"/products/{product_id}/purchase?user_id={user_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == user_id
        assert data["product_id"] == product_id

    def test_get_user_inventory(self, client, test_data):
        user_id = test_data["user"].id
        response = client.get(f"/inventory/users/{user_id}/items")
        assert response.status_code == status.HTTP_200_OK

    def test_analytics_popular_products(self, client):
        response = client.get("/analytics/popular-products")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "products" in data
        assert "days" in data
        assert "limit" in data