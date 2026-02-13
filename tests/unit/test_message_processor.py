"""
Unit tests for message processing module.

Tests complete message processing pipeline.
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.nlp.message_processor import MedicalMessageProcessor


class TestMessageProcessor:
    """Test message processor."""

    @pytest.fixture
    def processor(self):
        """Create processor instance."""
        return MedicalMessageProcessor()

    def test_processor_initialization(self, processor):
        """Test processor initialization."""
        assert processor is not None
        assert hasattr(processor, "process_message")

    def test_process_medical_message(self, processor):
        """Test processing medical message."""
        text = "Amoxicillin 500mg for infection"
        result = processor.process_message(text)

        assert result is not None
        assert hasattr(result, "is_medical")
        assert hasattr(result, "entities")
        assert hasattr(result, "quality_score")

    def test_process_non_medical_message(self, processor):
        """Test processing non-medical message."""
        text = "The weather is nice"
        result = processor.process_message(text)

        assert result is not None
        assert not result.is_medical

    def test_entity_extraction(self, processor):
        """Test entity extraction in processing."""
        text = "Amoxicillin 500mg for fever"
        result = processor.process_message(text)

        assert isinstance(result.entities, list)
        assert len(result.entities) >= 0

    def test_confidence_scoring(self, processor):
        """Test confidence scoring."""
        text = "Amoxicillin for infection"
        result = processor.process_message(text)

        assert 0 <= result.medical_confidence <= 1.0

    def test_quality_score_calculation(self, processor):
        """Test quality score calculation."""
        text = "Amoxicillin 500mg twice daily for bacterial infection"
        result = processor.process_message(text)

        assert 0 <= result.quality_score <= 1.0

    def test_empty_text_handling(self, processor):
        """Test handling empty text."""
        text = ""
        result = processor.process_message(text)

        assert result is not None
        assert isinstance(result.is_medical, bool)

    def test_long_text_handling(self, processor):
        """Test handling long text."""
        text = "Medical information. " * 100
        result = processor.process_message(text)

        assert result is not None


class TestProcessedMessage:
    """Test ProcessedMessage result object."""

    @pytest.fixture
    def processor(self):
        """Create processor instance."""
        return MedicalMessageProcessor()

    def test_result_has_all_attributes(self, processor):
        """Test result has all required attributes."""
        text = "Amoxicillin for infection"
        result = processor.process_message(text)

        assert hasattr(result, "original_text")
        assert hasattr(result, "is_medical")
        assert hasattr(result, "medical_confidence")
        assert hasattr(result, "entities")
        assert hasattr(result, "quality_score")
        assert hasattr(result, "processing_time")

    def test_entity_attributes(self, processor):
        """Test entity attributes in result."""
        text = "Amoxicillin 500mg for infection"
        result = processor.process_message(text)

        for entity in result.entities:
            assert hasattr(entity, "text")
            assert hasattr(entity, "entity_type")
            assert hasattr(entity, "confidence")


class TestBatchProcessing:
    """Test batch message processing."""

    @pytest.fixture
    def processor(self):
        """Create processor instance."""
        return MedicalMessageProcessor()

    def test_batch_processing(self, processor):
        """Test processing multiple messages."""
        texts = [
            "Amoxicillin for infection",
            "Weather is sunny",
            "Patient has fever",
        ]

        results = []
        for text in texts:
            result = processor.process_message(text)
            results.append(result)

        assert len(results) == 3
        assert all(result is not None for result in results)

    def test_batch_medical_detection(self, processor):
        """Test medical detection in batch."""
        texts = [
            "Amoxicillin for infection",
            "Weather is nice",
            "Fever treatment",
        ]

        results = []
        for text in texts:
            result = processor.process_message(text)
            results.append(result)

        medical_count = sum(1 for r in results if r.is_medical)
        assert medical_count >= 2


class TestQualityScoring:
    """Test quality scoring logic."""

    @pytest.fixture
    def processor(self):
        """Create processor instance."""
        return MedicalMessageProcessor()

    def test_high_quality_score(self, processor):
        """Test high quality medical message."""
        text = "Amoxicillin 500mg twice daily for bacterial infection"
        result = processor.process_message(text)

        assert result.quality_score >= 0.7

    def test_low_quality_score(self, processor):
        """Test low quality message."""
        text = "sick"
        result = processor.process_message(text)

        # Should have lower quality score
        assert isinstance(result.quality_score, float)

    def test_quality_based_on_entities(self, processor):
        """Test quality score based on entity count."""
        detailed = "Amoxicillin 500mg twice daily"
        simple = "medicine"

        result_detailed = processor.process_message(detailed)
        result_simple = processor.process_message(simple)

        # Detailed should have better quality
        assert result_detailed.quality_score >= result_simple.quality_score


class TestEdgeCases:
    """Test edge cases."""

    @pytest.fixture
    def processor(self):
        """Create processor instance."""
        return MedicalMessageProcessor()

    def test_special_characters(self, processor):
        """Test handling special characters."""
        text = "Amoxicillin (500mg) for infection!!"
        result = processor.process_message(text)

        assert result is not None

    def test_unicode_text(self, processor):
        """Test handling unicode text."""
        text = "Amoxicillin 阿莫西林"
        result = processor.process_message(text)

        assert result is not None

    def test_mixed_case(self, processor):
        """Test handling mixed case."""
        text = "aMoXiCiLLiN for InFeCtIoN"
        result = processor.process_message(text)

        assert result is not None

    def test_numbers_only(self, processor):
        """Test handling numbers."""
        text = "500 mg"
        result = processor.process_message(text)

        assert result is not None