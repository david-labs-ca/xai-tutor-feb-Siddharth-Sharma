"""Tests for the Products API (read-only)."""

import pytest


class TestListProducts:
    """GET /products"""

    def test_list_products_returns_200(self, client):
        """List products returns 200 and an array."""
        response = client.get("/products")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_products_each_has_id_name_price(self, client):
        """Each product has id, name, and price."""
        response = client.get("/products")
        assert response.status_code == 200
        for product in response.json():
            assert "id" in product
            assert "name" in product
            assert "price" in product
            assert isinstance(product["id"], int)
            assert isinstance(product["name"], str)
            assert isinstance(product["price"], (int, float))

    def test_list_products_seeded_data_present(self, client):
        """Products table is seeded with sample data (from migration)."""
        response = client.get("/products")
        assert response.status_code == 200
        products = response.json()
        assert len(products) >= 1
        names = [p["name"] for p in products]
        prices = [p["price"] for p in products]
        assert all(isinstance(n, str) and len(n) > 0 for n in names)
        assert all(isinstance(pr, (int, float)) and pr >= 0 for pr in prices)
