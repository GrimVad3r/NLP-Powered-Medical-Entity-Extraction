"""
Integration tests for API endpoints.

Tests all API routes with real database and NLP.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api.main import app
from src.database.connection import get_db_session
from src.database.models import Message, Channel, Entity
from datetime import datetime


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_channel(db_session):
    """Create test channel."""
    channel = Channel(
        name="test_channel",
        telegram_id=12345,
        description="Test Channel"
    )
    db_session.add(channel)
    db_session.commit()
    return channel


@pytest.fixture
def test_message(db_session, test_channel):
    """Create test message."""
    message = Message(
        telegram_id=1,
        channel_id=test_channel.id,
        text="Amoxicillin 500mg for fever treatment",
        date=datetime.utcnow(),
        is_medical=True,
        quality_score=0.85
    )
    db_session.add(message)
    db_session.commit()
    return message


class TestProductEndpoints:
    """Test product endpoints."""

    def test_get_top_products(self, client):
        """Test GET /api/v1/products/top10"""
        response = client.get("/api/v1/products/top10")
        assert response.status_code == 200
        assert "products" in response.json()
        assert "total" in response.json()

    def test_get_top_products_with_limit(self, client):
        """Test GET /api/v1/products/top10 with limit"""
        response = client.get("/api/v1/products/top10?limit=5")
        assert response.status_code == 200

    def test_search_products(self, client):
        """Test GET /api/v1/products/search/{query}"""
        response = client.get("/api/v1/products/search/amoxicillin")
        assert response.status_code == 200
        assert "products" in response.json()


class TestNLPEndpoints:
    """Test NLP endpoints."""

    def test_process_message(self, client):
        """Test POST /api/v1/nlp/process-message"""
        response = client.post(
            "/api/v1/nlp/process-message",
            json={"text": "I have fever and need paracetamol"}
        )
        assert response.status_code == 200
        result = response.json()
        assert "is_medical" in result
        assert "entities" in result
        assert "quality_score" in result

    def test_process_medical_message(self, client):
        """Test processing medical message"""
        response = client.post(
            "/api/v1/nlp/process-message",
            json={"text": "Amoxicillin 500mg twice daily for infection"}
        )
        assert response.status_code == 200
        result = response.json()
        assert result["is_medical"] == True
        assert len(result["entities"]) > 0

    def test_classify_text(self, client):
        """Test GET /api/v1/nlp/classify-text"""
        response = client.get(
            "/api/v1/nlp/classify-text?text=This is a medical message about fever"
        )
        assert response.status_code == 200
        result = response.json()
        assert "is_medical" in result
        assert "medical_confidence" in result

    def test_extract_entities(self, client):
        """Test GET /api/v1/nlp/extract-entities"""
        response = client.get(
            "/api/v1/nlp/extract-entities?text=Amoxicillin 500mg for infection"
        )
        assert response.status_code == 200
        result = response.json()
        assert "entities" in result
        assert "total_entities" in result

    def test_get_models_info(self, client):
        """Test GET /api/v1/nlp/models"""
        response = client.get("/api/v1/nlp/models")
        assert response.status_code == 200
        result = response.json()
        assert "models" in result
        assert "processors" in result


class TestAnalyticsEndpoints:
    """Test analytics endpoints."""

    def test_get_summary(self, client):
        """Test GET /api/v1/analytics/summary"""
        response = client.get("/api/v1/analytics/summary")
        assert response.status_code == 200
        result = response.json()
        assert "total_messages" in result
        assert "medical_messages" in result
        assert "medical_percentage" in result

    def test_get_daily_stats(self, client):
        """Test GET /api/v1/analytics/daily-stats"""
        response = client.get("/api/v1/analytics/daily-stats?days=7")
        assert response.status_code == 200
        result = response.json()
        assert "period_days" in result
        assert "daily_stats" in result

    def test_get_entity_distribution(self, client):
        """Test GET /api/v1/analytics/entity-distribution"""
        response = client.get("/api/v1/analytics/entity-distribution")
        assert response.status_code == 200
        result = response.json()
        assert "total_entities" in result
        assert "distribution" in result

    def test_get_top_medications(self, client):
        """Test GET /api/v1/analytics/top-medications"""
        response = client.get("/api/v1/analytics/top-medications")
        assert response.status_code == 200
        result = response.json()
        assert "medications" in result
        assert "total" in result

    def test_get_top_conditions(self, client):
        """Test GET /api/v1/analytics/top-conditions"""
        response = client.get("/api/v1/analytics/top-conditions")
        assert response.status_code == 200
        result = response.json()
        assert "conditions" in result
        assert "total" in result


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_endpoint(self, client):
        """Test accessing invalid endpoint"""
        response = client.get("/api/v1/invalid")
        assert response.status_code == 404

    def test_missing_required_param(self, client):
        """Test missing required parameters"""
        response = client.post("/api/v1/nlp/process-message", json={})
        assert response.status_code in [400, 422]

    def test_invalid_confidence_threshold(self, client):
        """Test invalid confidence threshold"""
        response = client.post(
            "/api/v1/nlp/process-message",
            json={"text": "test", "min_confidence": 1.5}  # Invalid
        )
        assert response.status_code in [400, 422]