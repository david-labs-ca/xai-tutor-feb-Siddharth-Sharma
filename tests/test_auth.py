"""Tests for the authentication APIs: register and login."""

import pytest


class TestRegister:
    """POST /auth/register"""

    def test_register_creates_user_returns_201(self, client):
        """Register with valid email and password returns 201 and user data."""
        response = client.post(
            "/auth/register",
            json={"email": "newuser@example.com", "password": "secret123"},
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == "newuser@example.com"
        assert isinstance(data["id"], int)

    def test_register_email_normalized_to_lowercase(self, client):
        """Email is stored and returned in lowercase."""
        response = client.post(
            "/auth/register",
            json={"email": "MixedCase@Example.com", "password": "secret123"},
        )
        assert response.status_code == 201
        assert response.json()["email"] == "mixedcase@example.com"

    def test_register_duplicate_email_returns_409(self, client):
        """Registering the same email twice returns 409 Conflict."""
        payload = {"email": "duplicate@example.com", "password": "secret123"}
        client.post("/auth/register", json=payload)
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    def test_register_short_password_returns_400(self, client):
        """Password shorter than 6 characters returns 400."""
        response = client.post(
            "/auth/register",
            json={"email": "short@example.com", "password": "12345"},
        )
        assert response.status_code == 400
        assert "password" in response.json()["detail"].lower()

    def test_register_invalid_email_returns_422(self, client):
        """Invalid email format returns 422."""
        response = client.post(
            "/auth/register",
            json={"email": "not-an-email", "password": "secret123"},
        )
        assert response.status_code == 422


class TestLogin:
    """POST /auth/login"""

    def test_login_returns_token(self, client):
        """Login with valid credentials returns 200 and JWT."""
        client.post(
            "/auth/register",
            json={"email": "loginuser@example.com", "password": "mypass123"},
        )
        response = client.post(
            "/auth/login",
            json={"email": "loginuser@example.com", "password": "mypass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_wrong_password_returns_401(self, client):
        """Login with wrong password returns 401."""
        client.post(
            "/auth/register",
            json={"email": "wrongpass@example.com", "password": "correct123"},
        )
        response = client.post(
            "/auth/login",
            json={"email": "wrongpass@example.com", "password": "wrongpass"},
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_login_unknown_email_returns_401(self, client):
        """Login with unregistered email returns 401."""
        response = client.post(
            "/auth/login",
            json={"email": "nobody@example.com", "password": "anypass123"},
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_login_email_case_insensitive(self, client):
        """Login accepts email in any case (user was stored lowercase)."""
        client.post(
            "/auth/register",
            json={"email": "caseuser@example.com", "password": "pass123"},
        )
        response = client.post(
            "/auth/login",
            json={"email": "CaseUser@Example.com", "password": "pass123"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
