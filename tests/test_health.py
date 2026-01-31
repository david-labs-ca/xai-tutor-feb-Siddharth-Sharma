"""Tests for the health check API."""

import pytest


class TestHealth:
    """GET /health"""

    def test_health_returns_200(self, client):
        """Health endpoint returns 200 and healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data == {"status": "healthy"}
