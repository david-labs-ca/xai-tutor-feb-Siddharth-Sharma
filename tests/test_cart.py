"""Tests for the Cart API (JWT-protected)."""

import uuid
import pytest


def _get_first_product_id(client):
    """Get id of first product from GET /products."""
    r = client.get("/products")
    r.raise_for_status()
    products = r.json()
    assert len(products) >= 1
    return products[0]["id"]


def _fresh_auth_headers(client):
    """Register a new user and return Authorization headers (for isolated cart state)."""
    email = f"cart_{uuid.uuid4().hex}@example.com"
    client.post("/auth/register", json={"email": email, "password": "pass123"})
    r = client.post("/auth/login", json={"email": email, "password": "pass123"})
    r.raise_for_status()
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestCartAuth:
    """Cart endpoints require JWT."""

    def test_get_cart_without_auth_returns_401(self, client):
        response = client.get("/cart")
        assert response.status_code == 401

    def test_add_item_without_auth_returns_401(self, client):
        response = client.post("/cart/items", json={"product_id": 1, "quantity": 1})
        assert response.status_code == 401


class TestAddCartItem:
    """POST /cart/items"""

    def test_add_item_returns_201(self, client, auth_headers):
        product_id = _get_first_product_id(client)
        response = client.post(
            "/cart/items",
            json={"product_id": product_id, "quantity": 2},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["product_id"] == product_id
        assert data["quantity"] == 2

    def test_add_item_invalid_product_returns_404(self, client, auth_headers):
        response = client.post(
            "/cart/items",
            json={"product_id": 99999, "quantity": 1},
            headers=auth_headers,
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_add_item_quantity_zero_returns_400(self, client, auth_headers):
        product_id = _get_first_product_id(client)
        response = client.post(
            "/cart/items",
            json={"product_id": product_id, "quantity": 0},
            headers=auth_headers,
        )
        assert response.status_code == 400


class TestGetCart:
    """GET /cart"""

    def test_get_cart_empty_returns_empty_list(self, client):
        headers = _fresh_auth_headers(client)
        response = client.get("/cart", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0.0
        assert data["status"] == "active"

    def test_get_cart_after_add_shows_items_and_total(self, client):
        headers = _fresh_auth_headers(client)
        product_id = _get_first_product_id(client)
        client.post(
            "/cart/items",
            json={"product_id": product_id, "quantity": 1},
            headers=headers,
        )
        response = client.get("/cart", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["product_id"] == product_id
        assert data["items"][0]["quantity"] == 1
        assert "product_name" in data["items"][0]
        assert "price" in data["items"][0]
        assert "subtotal" in data["items"][0]
        assert data["total"] >= 0


class TestUpdateCartItem:
    """PUT /cart/items/{itemId}"""

    def test_update_quantity_returns_200(self, client, auth_headers):
        product_id = _get_first_product_id(client)
        add_r = client.post(
            "/cart/items",
            json={"product_id": product_id, "quantity": 1},
            headers=auth_headers,
        )
        add_r.raise_for_status()
        item_id = add_r.json()["id"]
        response = client.put(
            f"/cart/items/{item_id}",
            json={"quantity": 3},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["quantity"] == 3
        get_r = client.get("/cart", headers=auth_headers)
        assert get_r.json()["items"][0]["quantity"] == 3

    def test_update_item_not_found_returns_404(self, client, auth_headers):
        response = client.put(
            "/cart/items/99999",
            json={"quantity": 2},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_update_quantity_invalid_returns_400(self, client, auth_headers):
        product_id = _get_first_product_id(client)
        add_r = client.post(
            "/cart/items",
            json={"product_id": product_id, "quantity": 1},
            headers=auth_headers,
        )
        add_r.raise_for_status()
        item_id = add_r.json()["id"]
        response = client.put(
            f"/cart/items/{item_id}",
            json={"quantity": 0},
            headers=auth_headers,
        )
        assert response.status_code == 400


class TestRemoveCartItem:
    """DELETE /cart/items/{itemId}"""

    def test_remove_item_returns_204(self, client, auth_headers):
        product_id = _get_first_product_id(client)
        add_r = client.post(
            "/cart/items",
            json={"product_id": product_id, "quantity": 1},
            headers=auth_headers,
        )
        add_r.raise_for_status()
        item_id = add_r.json()["id"]
        response = client.delete(f"/cart/items/{item_id}", headers=auth_headers)
        assert response.status_code == 204
        get_r = client.get("/cart", headers=auth_headers)
        assert get_r.json()["items"] == []
        assert get_r.json()["total"] == 0.0

    def test_remove_item_not_found_returns_404(self, client, auth_headers):
        response = client.delete("/cart/items/99999", headers=auth_headers)
        assert response.status_code == 404


class TestCheckout:
    """POST /cart/checkout"""

    def test_checkout_empty_cart_returns_message(self, client, auth_headers):
        response = client.post("/cart/checkout", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["total"] == 0.0

    def test_checkout_clears_cart(self, client, auth_headers):
        product_id = _get_first_product_id(client)
        client.post(
            "/cart/items",
            json={"product_id": product_id, "quantity": 1},
            headers=auth_headers,
        )
        response = client.post("/cart/checkout", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 0
        get_r = client.get("/cart", headers=auth_headers)
        assert get_r.json()["items"] == []
        assert get_r.json()["total"] == 0.0
