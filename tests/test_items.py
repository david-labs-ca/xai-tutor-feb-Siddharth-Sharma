"""Tests for the items API: list, get, create, update, delete."""

import pytest


class TestListItems:
    """GET /items"""

    def test_list_items_returns_200_and_array(self, client):
        """List items returns 200 and an items array (may be empty or seeded)."""
        response = client.get("/items")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_list_items_each_has_id_and_name(self, client):
        """Each item in the list has id and name."""
        response = client.get("/items")
        assert response.status_code == 200
        for item in response.json()["items"]:
            assert "id" in item
            assert "name" in item
            assert isinstance(item["id"], int)
            assert isinstance(item["name"], str)


class TestGetItem:
    """GET /items/{item_id}"""

    def test_get_item_returns_200(self, client):
        """Get existing item by id returns 200 and item data."""
        create_resp = client.post("/items", json={"name": "GetTestItem"})
        assert create_resp.status_code == 201
        item_id = create_resp.json()["id"]
        response = client.get(f"/items/{item_id}")
        assert response.status_code == 200
        assert response.json() == {"id": item_id, "name": "GetTestItem"}

    def test_get_item_not_found_returns_404(self, client):
        """Get non-existent item returns 404."""
        response = client.get("/items/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestCreateItem:
    """POST /items"""

    def test_create_item_returns_201(self, client):
        """Create item returns 201 and created item with id."""
        response = client.post("/items", json={"name": "NewItem"})
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == "NewItem"
        assert isinstance(data["id"], int)

    def test_create_item_missing_name_returns_422(self, client):
        """Create without name returns 422."""
        response = client.post("/items", json={})
        assert response.status_code == 422


class TestUpdateItem:
    """PUT /items/{item_id}"""

    def test_update_item_returns_200(self, client):
        """Update existing item returns 200 and updated data."""
        create_resp = client.post("/items", json={"name": "Original"})
        item_id = create_resp.json()["id"]
        response = client.put(f"/items/{item_id}", json={"name": "Updated"})
        assert response.status_code == 200
        assert response.json() == {"id": item_id, "name": "Updated"}
        get_resp = client.get(f"/items/{item_id}")
        assert get_resp.json()["name"] == "Updated"

    def test_update_item_not_found_returns_404(self, client):
        """Update non-existent item returns 404."""
        response = client.put("/items/99999", json={"name": "Any"})
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestDeleteItem:
    """DELETE /items/{item_id}"""

    def test_delete_item_returns_204(self, client):
        """Delete existing item returns 204 and item is gone."""
        create_resp = client.post("/items", json={"name": "ToDelete"})
        item_id = create_resp.json()["id"]
        response = client.delete(f"/items/{item_id}")
        assert response.status_code == 204
        get_resp = client.get(f"/items/{item_id}")
        assert get_resp.status_code == 404

    def test_delete_item_not_found_returns_404(self, client):
        """Delete non-existent item returns 404."""
        response = client.delete("/items/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
