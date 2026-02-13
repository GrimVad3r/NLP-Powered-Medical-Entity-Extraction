"""
Medical text classification using transformers.

BRANCH-3: NLP Pipeline
Author: Boris (Claude Code)
"""

from dataclasses import dataclass
from typing import Tuple

from transformers import pipeline

from src.core.exceptions import ModelLoadingError, TextClassificationError
from src.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ClassificationResult:
    """Text classification result."""

    label: str  # "medical" or "non-medical"
    confidence: float
    reasoning: str = ""

    def is_medical(self) -> bool:
        """Check if text is classified as medical."""
        return self.label.lower() == "medical"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "label": self.label,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
        }


class MedicalTextClassifier:
    """Classify text as medical or non-medical."""

    MEDICAL_KEYWORDS = {
        "medication", "drug", "medicine", "treatment", "disease",
        "symptom", "patient", "doctor", "hospital", "clinic",
        "fever", "cough", "pain", "infection", "vaccine",
        "tablet", "capsule", "injection", "dosage", "prescription",
        "health", "medical", "pharma", "antibiotics", "malaria",
        "malaria treatment", "artemether", "amoxicillin", "paracetamol"
    }

    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        """
        Initialize classifier.

        Args:
            model_name: HuggingFace model name

        Raises:
            ModelLoadingError: If model fails to load
        """
        try:
            self.classifier = pipeline(
                "text-classification",
                model=model_name,
                device=-1  # CPU, set to 0 for GPU
            )
            logger.info(f"Loaded text classifier: {model_name}")
        except Exception as e:
            raise ModelLoadingError(
                f"Failed to load classifier model: {model_name}",
                details={"error": str(e)}
            )

    def classify(self, text: str) -> ClassificationResult:
        """
        Classify text as medical or non-medical.

        Args:
            text: Input text to classify

        Returns:
            ClassificationResult with label and confidence

        Raises:
            TextClassificationError: If classification fails

        Example:
            >>> classifier = MedicalTextClassifier()
            >>> result = classifier.classify("Malaria treatment available")
            >>> result.is_medical()
            True
        """
        if not text or not text.strip():
            return ClassificationResult(
                label="non-medical",
                confidence=1.0,
                reasoning="Empty text"
            )

        try:
            # Truncate if too long (transformer limits)
            text = text[:512]

            # Use keyword-based heuristic
            medical_score = self._keyword_based_score(text)

            # Use transformer model
            result = self.classifier(text)[0]

            # Combine scores
            confidence, label, reasoning = self._combine_scores(
                medical_score,
                result,
                text
            )

            return ClassificationResult(
                label=label,
                confidence=confidence,
                reasoning=reasoning
            )

        except Exception as e:
            raise TextClassificationError(
                f"Failed to classify text: {str(e)}",
                details={"text_length": len(text)}
            )

    def _keyword_based_score(self, text: str) -> float:
        """
        Calculate medical relevance score based on keywords.

        Args:
            text: Input text

        Returns:
            Score between 0 and 1
        """
        text_lower = text.lower()
        keyword_matches = sum(
            1 for keyword in self.MEDICAL_KEYWORDS
            if keyword in text_lower
        )

        # Normalize score
        max_matches = len(self.MEDICAL_KEYWORDS)
        score = min(keyword_matches / max(5, max_matches / 10), 1.0)

        return score

    def _combine_scores(
        self,
        keyword_score: float,
        transformer_result: dict,
        text: str
    ) -> Tuple[float, str, str]:
        """
        Combine keyword and transformer scores.

        Args:
            keyword_score: Score from keyword matching
            transformer_result: Result from transformer model
            text: Original text

        Returns:
            Tuple of (confidence, label, reasoning)
        """
        # Extract transformer score
        transformer_score = transformer_result["score"]
        transformer_label = transformer_result["label"]

        # Map transformer labels
        is_positive = transformer_label in ["POSITIVE", "medical"]

        # Combine scores (weighted average)
        combined_score = (keyword_score * 0.4) + (transformer_score * 0.6)

        # Determine final label
        if combined_score > 0.6:
            final_label = "medical"
        else:
            final_label = "non-medical"

        # Generate reasoning
        reasoning = self._generate_reasoning(
            keyword_score,
            transformer_score,
            text
        )

        return combined_score, final_label, reasoning

    def _generate_reasoning(
        self,
        keyword_score: float,
        transformer_score: float,
        text: str
    ) -> str:
        """Generate explanation for classification."""
        reasoning_parts = []

        if keyword_score > 0.5:
            reasoning_parts.append(f"Medical keywords detected (score: {keyword_score:.2f})")

        if transformer_score > 0.6:
            reasoning_parts.append(f"Transformer model confidence: {transformer_score:.2f}")

        if len(text.split()) < 5:
            reasoning_parts.append("Short text, may have lower confidence")

        return "; ".join(reasoning_parts) if reasoning_parts else "Default classification"

    def batch_classify(self, texts: list[str]) -> list[ClassificationResult]:
        """
        Classify multiple texts.

        Args:
            texts: List of texts to classify

        Returns:
            List of ClassificationResult objects
        """
        return [self.classify(text) for text in texts]

    def add_medical_keyword(self, keyword: str) -> None:
        """Add custom medical keyword."""
        self.MEDICAL_KEYWORDS.add(keyword.lower())
        logger.debug(f"Added medical keyword: {keyword}")

    def remove_medical_keyword(self, keyword: str) -> None:
        """Remove medical keyword."""
        self.MEDICAL_KEYWORDS.discard(keyword.lower())
        logger.debug(f"Removed medical keyword: {keyword}")