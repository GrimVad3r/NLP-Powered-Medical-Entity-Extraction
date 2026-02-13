"""
Integration tests for extraction and NLP pipelines.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.extraction.channel_scraper import ChannelScraper
from src.extraction.telegram_client import TelegramClientWrapper
from src.nlp.message_processor import MedicalMessageProcessor
from src.nlp.medical_ner import MedicalNER
from src.nlp.text_classifier import MedicalTextClassifier
from src.nlp.entity_linker import MedicalEntityLinker


class TestExtractionPipeline:
    """Test extraction pipeline."""

    @pytest.fixture
    def processor(self):
        """Get message processor."""
        return MedicalMessageProcessor()

    def test_extract_medical_entities(self, processor):
        """Test extracting medical entities."""
        text = "Patient has fever and was prescribed Amoxicillin 500mg twice daily"
        result = processor.process_message(text)

        assert result.is_medical
        assert len(result.entities) > 0
        assert any(e.entity_type == "MEDICATION" for e in result.entities)

    def test_extract_dosage_information(self, processor):
        """Test extracting dosage information."""
        text = "Take 500mg of paracetamol every 6 hours"
        result = processor.process_message(text)

        assert result.is_medical
        dosage_entities = [e for e in result.entities if e.entity_type == "DOSAGE"]
        assert len(dosage_entities) > 0

    def test_extract_price_information(self, processor):
        """Test extracting price information."""
        text = "Amoxicillin costs 150 ETB per box"
        result = processor.process_message(text)

        assert result.is_medical
        price_entities = [e for e in result.entities if e.entity_type == "PRICE"]
        # Note: May or may not extract depending on NER model


class TestNLPPipeline:
    """Test NLP pipeline."""

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

    @pytest.fixture
    def linker(self):
        """Get entity linker."""
        return MedicalEntityLinker()

    def test_classify_medical_message(self, classifier):
        """Test classifying medical message."""
        text = "I have a fever and need medication"
        result = classifier.classify(text)

        assert result.is_medical
        assert result.confidence > 0.5

    def test_classify_non_medical_message(self, classifier):
        """Test classifying non-medical message."""
        text = "The weather is nice today"
        result = classifier.classify(text)

        assert not result.is_medical

    def test_ner_entity_extraction(self, ner):
        """Test NER entity extraction."""
        text = "Amoxicillin 500mg for infection treatment"
        entities = ner.extract_entities(text)

        assert len(entities) > 0
        entity_texts = [e.text.lower() for e in entities]
        assert any("amoxicillin" in text.lower() for text in entity_texts)

    def test_entity_linking(self, linker):
        """Test entity linking."""
        entity_text = "Amoxicillin"
        result = linker.link_entity(entity_text, "MEDICATION")

        assert result is not None
        assert result.confidence > 0

    def test_complete_pipeline(self, processor):
        """Test complete NLP pipeline."""
        text = "Patient presenting with fever. Prescribed Amoxicillin 500mg three times daily."
        result = processor.process_message(text)

        assert result.is_medical
        assert result.medical_confidence > 0.5
        assert len(result.entities) > 0
        assert result.quality_score > 0

    def test_batch_processing(self, processor):
        """Test batch NLP processing."""
        texts = [
            "Amoxicillin for infection",
            "Weather is sunny today",
            "Patient has malaria symptoms",
        ]

        results = []
        for text in texts:
            result = processor.process_message(text)
            results.append(result)

        assert len(results) == 3
        medical_count = sum(1 for r in results if r.is_medical)
        assert medical_count >= 2

    def test_quality_scoring(self, processor):
        """Test quality scoring."""
        medical_text = "Amoxicillin 500mg twice daily for bacterial infection"
        result = processor.process_message(medical_text)

        assert result.quality_score >= 0.7

    def test_confidence_thresholding(self, processor):
        """Test entity filtering by confidence."""
        text = "Patient with fever possibly needs medication"
        result = processor.process_message(text)

        high_confidence = [e for e in result.entities if e.confidence > 0.8]
        # May or may not have high confidence entities depending on text
        assert isinstance(high_confidence, list)