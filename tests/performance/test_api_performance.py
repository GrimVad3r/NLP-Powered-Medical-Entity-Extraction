"""
Performance tests for NLP and API operations.
"""

import pytest
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.nlp.message_processor import MedicalMessageProcessor
from src.nlp.medical_ner import MedicalNER
from src.nlp.text_classifier import MedicalTextClassifier
from fastapi.testclient import TestClient
from src.api.main import app


class TestAPIPerformance:
    """Performance tests for API endpoints."""

    @pytest.fixture
    def client(self):
        """Get test client."""
        return TestClient(app)

    def test_nlp_endpoint_response_time(self, client, benchmark):
        """Test NLP endpoint response time."""
        payload = {"text": "Amoxicillin 500mg for infection"}

        def request():
            return client.post("/api/v1/nlp/process-message", json=payload)

        response = benchmark(request)
        assert response.status_code == 200

    def test_analytics_endpoint_response_time(self, client, benchmark):
        """Test analytics endpoint response time."""
        def request():
            return client.get("/api/v1/analytics/summary")

        response = benchmark(request)
        assert response.status_code == 200

    def test_products_endpoint_response_time(self, client, benchmark):
        """Test products endpoint response time."""
        def request():
            return client.get("/api/v1/products/top10")

        response = benchmark(request)
        assert response.status_code == 200

    def test_concurrent_nlp_requests(self, client):
        """Test handling concurrent NLP requests."""
        import concurrent.futures

        payload = {"text": "Amoxicillin 500mg for infection"}

        def make_request():
            return client.post("/api/v1/nlp/process-message", json=payload)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(results) == 20
        assert all(r.status_code == 200 for r in results)

    def test_endpoint_load(self, client):
        """Test API under load."""
        payload = {"text": "Amoxicillin 500mg for infection"}
        requests_count = 100

        start_time = time.time()
        for _ in range(requests_count):
            response = client.post("/api/v1/nlp/process-message", json=payload)
            assert response.status_code == 200
        elapsed = time.time() - start_time

        avg_response_time = elapsed / requests_count
        assert avg_response_time < 1.0  # Less than 1 second per request

    def test_memory_usage_under_load(self, client):
        """Test memory usage under load."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        payload = {"text": "Amoxicillin 500mg for infection"}
        for _ in range(50):
            client.post("/api/v1/nlp/process-message", json=payload)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100