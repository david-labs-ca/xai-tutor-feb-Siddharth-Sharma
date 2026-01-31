"""
Pytest configuration and shared fixtures for API tests.
Uses a separate test database so the main app.db is not modified.
"""

import os
import sys

# Use a test database before any app/database imports
TEST_DB = os.path.join(os.path.dirname(__file__), "test_app.db")
os.environ["DATABASE_PATH"] = TEST_DB

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

# Run migrations against test DB (imports use DATABASE_PATH from env)
from migrate import run_migrations

from app.main import app


def _ensure_migrations():
    """Run migrations on the test database (idempotent)."""
    run_migrations("upgrade")


@pytest.fixture(scope="session")
def _migrate():
    """Run migrations once per test session."""
    _ensure_migrations()
    yield


@pytest.fixture
def client(_migrate):
    """FastAPI TestClient using the test database."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client):
    """Register a user (or use existing), login, and return Authorization headers with JWT."""
    email = "authtest@example.com"
    password = "password123"
    client.post("/auth/register", json={"email": email, "password": password})
    # If already registered (409), login still works
    r = client.post("/auth/login", json={"email": email, "password": password})
    r.raise_for_status()
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
