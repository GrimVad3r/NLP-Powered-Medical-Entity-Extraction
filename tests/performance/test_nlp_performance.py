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


class TestNLPPerformance:
    """Performance tests for NLP operations."""

    @pytest.fixture
    def processor(self):
        """Get message processor."""
        return MedicalMessageProcessor()

    @pytest.fixture
    def ner(self):
        """Get NER."""
        return MedicalNER()

    @pytest.fixture
    def classifier(self):
        """Get classifier."""
        return MedicalTextClassifier()

    def test_ner_performance(self, ner, benchmark):
        """Test NER extraction performance."""
        text = "Amoxicillin 500mg twice daily for bacterial infection treatment"

        def extract():
            return ner.extract_entities(text)

        result = benchmark(extract)
        assert len(result) > 0

    def test_classification_performance(self, classifier, benchmark):
        """Test text classification performance."""
        text = "Patient has fever and needs medication for treatment"

        def classify():
            return classifier.classify(text)

        result = benchmark(classify)
        assert result.is_medical

    def test_message_processing_performance(self, processor, benchmark):
        """Test message processing performance."""
        text = "Amoxicillin 500mg for infection. Patient needs follow-up in 5 days."

        def process():
            return processor.process_message(text)

        result = benchmark(process)
        assert result is not None

    def test_batch_processing_performance(self, processor):
        """Test batch processing performance."""
        texts = [
            "Amoxicillin 500mg for infection",
            "Patient has fever symptoms",
            "Paracetamol 500mg twice daily",
        ] * 10  # 30 messages

        start_time = time.time()
        for text in texts:
            processor.process_message(text)
        elapsed = time.time() - start_time

        # Should process 30 messages in reasonable time
        assert elapsed < 30  # Adjust threshold as needed
        avg_time = elapsed / len(texts)
        assert avg_time < 1.0  # Less than 1 second per message

    def test_ner_extraction_throughput(self, ner):
        """Test NER extraction throughput."""
        text = "Amoxicillin 500mg for infection"
        repetitions = 100

        start_time = time.time()
        for _ in range(repetitions):
            ner.extract_entities(text)
        elapsed = time.time() - start_time

        throughput = repetitions / elapsed
        assert throughput > 10  # At least 10 extractions per second
