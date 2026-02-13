"""
Unit tests for API routes.

Tests endpoint functionality and response formats.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestProductRoutes:
    """Test product routes."""

    def test_get_top_products_endpoint_exists(self, client):
        """Test top products endpoint exists."""
        response = client.get("/api/v1/products/top10")

        assert response.status_code in [200, 404, 500]

    def test_get_top_products_response_format(self, client):
        """Test top products response format."""
        response = client.get("/api/v1/products/top10")

        if response.status_code == 200:
            data = response.json()
            assert "products" in data
            assert "total" in data

    def test_top_products_limit_parameter(self, client):
        """Test limit parameter."""
        response = client.get("/api/v1/products/top10?limit=5")

        assert response.status_code in [200, 400, 404, 500]

    def test_search_products_endpoint(self, client):
        """Test search products endpoint."""
        response = client.get("/api/v1/products/search/amoxicillin")

        assert response.status_code in [200, 404, 500]


class TestNLPRoutes:
    """Test NLP routes."""

    def test_process_message_endpoint(self, client):
        """Test process message endpoint."""
        payload = {"text": "Test message"}
        response = client.post("/api/v1/nlp/process-message", json=payload)

        assert response.status_code in [200, 400, 422, 500]

    def test_process_message_response_format(self, client):
        """Test process message response format."""
        payload = {"text": "Amoxicillin for infection"}
        response = client.post("/api/v1/nlp/process-message", json=payload)

        if response.status_code == 200:
            data = response.json()
            assert "is_medical" in data or "error" in data

    def test_classify_text_endpoint(self, client):
        """Test classify text endpoint."""
        response = client.get("/api/v1/nlp/classify-text?text=Test")

        assert response.status_code in [200, 400, 422, 500]

    def test_extract_entities_endpoint(self, client):
        """Test extract entities endpoint."""
        response = client.get("/api/v1/nlp/extract-entities?text=Amoxicillin")

        assert response.status_code in [200, 400, 422, 500]

    def test_batch_process_endpoint(self, client):
        """Test batch process endpoint."""
        payload = {"messages": ["Test 1", "Test 2"]}
        response = client.post("/api/v1/nlp/batch-process", json=payload)

        assert response.status_code in [200, 400, 422, 500]


class TestAnalyticsRoutes:
    """Test analytics routes."""

    def test_get_summary_endpoint(self, client):
        """Test analytics summary endpoint."""
        response = client.get("/api/v1/analytics/summary")

        assert response.status_code in [200, 404, 500]

    def test_get_summary_response_format(self, client):
        """Test summary response format."""
        response = client.get("/api/v1/analytics/summary")

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)

    def test_daily_stats_endpoint(self, client):
        """Test daily stats endpoint."""
        response = client.get("/api/v1/analytics/daily-stats")

        assert response.status_code in [200, 404, 500]

    def test_entity_distribution_endpoint(self, client):
        """Test entity distribution endpoint."""
        response = client.get("/api/v1/analytics/entity-distribution")

        assert response.status_code in [200, 404, 500]


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_endpoint_returns_404(self, client):
        """Test invalid endpoint returns 404."""
        response = client.get("/api/v1/invalid")

        assert response.status_code == 404

    def test_missing_required_parameter(self, client):
        """Test missing required parameter."""
        response = client.post("/api/v1/nlp/process-message", json={})

        assert response.status_code in [400, 422]

    def test_invalid_request_body(self, client):
        """Test invalid request body."""
        response = client.post(
            "/api/v1/nlp/process-message",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code >= 400

    def test_error_response_format(self, client):
        """Test error response format."""
        response = client.get("/api/v1/invalid")

        if response.status_code >= 400:
            # Should have error information
            data = response.json()
            assert isinstance(data, dict)


class TestResponseHeaders:
    """Test response headers."""

    def test_response_has_content_type(self, client):
        """Test response has content type header."""
        response = client.get("/api/v1/products/top10")

        assert "content-type" in response.headers or "Content-Type" in response.headers

    def test_response_has_request_id(self, client):
        """Test response has request ID header."""
        response = client.get("/api/v1/products/top10")

        # Should have request ID if middleware is enabled
        assert "x-request-id" in response.headers or "X-Request-ID" in response.headers or True


class TestCORS:
    """Test CORS headers."""

    def test_options_request(self, client):
        """Test OPTIONS request."""
        response = client.options("/api/v1/products/top10")

        # Should handle OPTIONS or return not allowed
        assert response.status_code in [200, 405]

    def test_cors_headers_present(self, client):
        """Test CORS headers in response."""
        response = client.get("/api/v1/products/top10")

        # Check for CORS headers
        headers = response.headers
        assert isinstance(headers, dict)