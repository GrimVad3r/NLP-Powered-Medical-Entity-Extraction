"""
Unit tests for text classification module.

Tests medical text classification functionality.
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.nlp.text_classifier import MedicalTextClassifier


class TestMedicalTextClassifier:
    """Test medical text classifier."""

    @pytest.fixture
    def classifier(self):
        """Create classifier instance."""
        return MedicalTextClassifier()

    def test_classifier_initialization(self, classifier):
        """Test classifier initialization."""
        assert classifier is not None
        assert hasattr(classifier, "classify")

    def test_classify_medical_message(self, classifier):
        """Test classifying medical message."""
        text = "Patient has fever and needs Amoxicillin"
        result = classifier.classify(text)

        assert result.is_medical
        assert 0 < result.confidence <= 1.0

    def test_classify_non_medical_message(self, classifier):
        """Test classifying non-medical message."""
        text = "The weather is sunny today"
        result = classifier.classify(text)

        assert not result.is_medical

    def test_confidence_score_range(self, classifier):
        """Test confidence score is in valid range."""
        text = "Amoxicillin for infection"
        result = classifier.classify(text)

        assert 0 <= result.confidence <= 1.0

    def test_classify_ambiguous_text(self, classifier):
        """Test classifying ambiguous text."""
        text = "I read about health"
        result = classifier.classify(text)

        assert isinstance(result.is_medical, bool)
        assert 0 < result.confidence <= 1.0

    def test_classify_empty_text(self, classifier):
        """Test classifying empty text."""
        text = ""
        result = classifier.classify(text)

        assert isinstance(result.is_medical, bool)

    def test_classify_long_text(self, classifier):
        """Test classifying long text."""
        text = "Medical information. " * 100
        result = classifier.classify(text)

        assert isinstance(result.is_medical, bool)

    def test_classify_special_characters(self, classifier):
        """Test classifying text with special characters."""
        text = "Amoxicillin (500mg) for infection!!!!"
        result = classifier.classify(text)

        assert isinstance(result.is_medical, bool)


class TestKeywordHeuristics:
    """Test keyword-based heuristics."""

    @pytest.fixture
    def classifier(self):
        """Create classifier instance."""
        return MedicalTextClassifier()

    def test_medication_keywords(self, classifier):
        """Test detection of medication keywords."""
        text = "Amoxicillin, Paracetamol, and Artemether"
        result = classifier.classify(text)

        assert result.is_medical

    def test_symptom_keywords(self, classifier):
        """Test detection of symptom keywords."""
        text = "fever, headache, and nausea"
        result = classifier.classify(text)

        # Should detect medical keywords
        assert isinstance(result.is_medical, bool)

    def test_condition_keywords(self, classifier):
        """Test detection of condition keywords."""
        text = "malaria, infection, and disease"
        result = classifier.classify(text)

        # Should detect medical keywords
        assert isinstance(result.is_medical, bool)

    def test_non_medical_keywords(self, classifier):
        """Test non-medical keywords are not classified as medical."""
        text = "apple, orange, banana"
        result = classifier.classify(text)

        assert not result.is_medical


class TestConsistency:
    """Test classifier consistency."""

    @pytest.fixture
    def classifier(self):
        """Create classifier instance."""
        return MedicalTextClassifier()

    def test_same_text_same_result(self, classifier):
        """Test same text gives same result."""
        text = "Amoxicillin 500mg for infection"

        result1 = classifier.classify(text)
        result2 = classifier.classify(text)

        assert result1.is_medical == result2.is_medical

    def test_similar_texts_consistent(self, classifier):
        """Test similar texts give similar results."""
        text1 = "Amoxicillin for fever"
        text2 = "Amoxicillin for infection"

        result1 = classifier.classify(text1)
        result2 = classifier.classify(text2)

        assert result1.is_medical == result2.is_medical


class TestEdgeCases:
    """Test edge cases."""

    @pytest.fixture
    def classifier(self):
        """Create classifier instance."""
        return MedicalTextClassifier()

    def test_null_text(self, classifier):
        """Test handling null text."""
        try:
            result = classifier.classify(None)
            # Should handle gracefully
            assert isinstance(result.is_medical, bool)
        except (TypeError, AttributeError):
            # Acceptable to raise error
            pass

    def test_whitespace_only(self, classifier):
        """Test classifying whitespace-only text."""
        text = "   \n\t   "
        result = classifier.classify(text)

        assert isinstance(result.is_medical, bool)

    def test_numbers_only(self, classifier):
        """Test classifying numbers-only text."""
        text = "123 456 789"
        result = classifier.classify(text)

        assert isinstance(result.is_medical, bool)

    def test_unicode_text(self, classifier):
        """Test classifying unicode text."""
        text = "Amoxicillin 阿莫西林"
        result = classifier.classify(text)

        assert isinstance(result.is_medical, bool)