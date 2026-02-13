"""
Unified medical message processing pipeline.

BRANCH-3: NLP Pipeline
Author: Boris (Claude Code)
"""

from dataclasses import dataclass, field
from typing import List, Optional

from src.core.logger import get_logger
from src.nlp.medical_ner import MedicalNER, MedicalEntity
from src.nlp.text_classifier import MedicalTextClassifier, ClassificationResult
from src.nlp.entity_linker import MedicalEntityLinker, LinkingResult

logger = get_logger(__name__)


@dataclass
class ProcessedMessage:
    """Result of processing a medical message."""

    text: str
    is_medical: bool
    medical_confidence: float
    entities: List[MedicalEntity] = field(default_factory=list)
    linked_entities: List[LinkingResult] = field(default_factory=list)
    quality_score: float = 0.0
    processing_status: str = "success"
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "is_medical": self.is_medical,
            "medical_confidence": self.medical_confidence,
            "entities": [e.to_dict() for e in self.entities],
            "linked_entities": [le.to_dict() for le in self.linked_entities],
            "quality_score": self.quality_score,
            "processing_status": self.processing_status,
            "error_message": self.error_message,
        }

    def get_medications(self) -> List[MedicalEntity]:
        """Get medication entities."""
        return [e for e in self.entities if e.entity_type == "MEDICATION"]

    def get_dosages(self) -> List[MedicalEntity]:
        """Get dosage entities."""
        return [e for e in self.entities if e.entity_type == "DOSAGE"]

    def get_conditions(self) -> List[MedicalEntity]:
        """Get condition entities."""
        return [e for e in self.entities if e.entity_type == "CONDITION"]

    def get_prices(self) -> List[MedicalEntity]:
        """Get price entities."""
        return [e for e in self.entities if e.entity_type == "PRICE"]


class MedicalMessageProcessor:
    """Process medical messages through NLP pipeline."""

    def __init__(
        self,
        use_gpu: bool = False,
        nlp_model: str = "en_core_sci_md",
        classifier_model: str = "distilbert-base-uncased-finetuned-sst-2-english"
    ):
        """
        Initialize message processor.

        Args:
            use_gpu: Whether to use GPU for inference
            nlp_model: spaCy model name
            classifier_model: Text classifier model name
        """
        self.ner = MedicalNER(model_name=nlp_model)
        self.classifier = MedicalTextClassifier(model_name=classifier_model)
        self.entity_linker = MedicalEntityLinker()

        logger.info("Medical message processor initialized")

    def process_message(self, text: str) -> ProcessedMessage:
        """
        Process a medical message through complete pipeline.

        Args:
            text: Input message text

        Returns:
            ProcessedMessage with all processing results

        Example:
            >>> processor = MedicalMessageProcessor()
            >>> result = processor.process_message("Malaria treatment with artemether")
            >>> result.is_medical
            True
        """
        logger.debug(f"Processing message: {text[:100]}...")

        try:
            # Step 1: Classify text
            classification = self.classifier.classify(text)

            # Step 2: Extract entities (always extract for better understanding)
            entities = self.ner.extract_entities(text)

            # Step 3: Link entities
            linked_entities = []
            if entities:
                linked_entities = self._link_entities(entities)

            # Step 4: Calculate quality score
            quality_score = self._calculate_quality_score(
                classification,
                entities,
                linked_entities,
                text
            )

            result = ProcessedMessage(
                text=text,
                is_medical=classification.is_medical(),
                medical_confidence=classification.confidence,
                entities=entities,
                linked_entities=linked_entities,
                quality_score=quality_score,
                processing_status="success"
            )

            logger.debug(f"Message processed successfully: {len(entities)} entities found")
            return result

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return ProcessedMessage(
                text=text,
                is_medical=False,
                medical_confidence=0.0,
                processing_status="error",
                error_message=str(e)
            )

    def _link_entities(self, entities: List[MedicalEntity]) -> List[LinkingResult]:
        """Link entities to knowledge bases."""
        linked = []

        for entity in entities:
            try:
                if entity.entity_type == "MEDICATION":
                    result = self.entity_linker.link_medication(entity.text)
                    linked.append(result)
            except Exception as e:
                logger.warning(f"Failed to link entity {entity.text}: {e}")
                continue

        return linked

    def _calculate_quality_score(
        self,
        classification: ClassificationResult,
        entities: List[MedicalEntity],
        linked_entities: List[LinkingResult],
        text: str
    ) -> float:
        """
        Calculate overall message quality score.

        Args:
            classification: Text classification result
            entities: Extracted entities
            linked_entities: Linked entities
            text: Original text

        Returns:
            Quality score between 0 and 1
        """
        scores = []

        # Medical relevance (0.3 weight)
        if classification.is_medical():
            scores.append(classification.confidence * 0.3)
        else:
            # Still give some credit for medical content even if not classified as medical
            if entities:
                scores.append(0.1 * 0.3)

        # Entity extraction (0.3 weight)
        entity_score = min(len(entities) / 5, 1.0)  # Normalize to 5+ entities
        scores.append(entity_score * 0.3)

        # Entity linking (0.2 weight)
        if linked_entities:
            linked_score = sum(e.confidence for e in linked_entities) / len(linked_entities)
            scores.append(linked_score * 0.2)

        # Text quality (0.2 weight)
        text_score = min(len(text.split()) / 30, 1.0)  # Normalize to 30+ words
        scores.append(text_score * 0.2)

        total_score = sum(scores)
        return min(total_score, 1.0)

    def batch_process(self, texts: List[str]) -> List[ProcessedMessage]:
        """
        Process multiple messages.

        Args:
            texts: List of message texts

        Returns:
            List of ProcessedMessage objects
        """
        return [self.process_message(text) for text in texts]

    def process_messages_generator(self, texts: List[str]):
        """
        Process messages as generator for memory efficiency.

        Args:
            texts: List of message texts

        Yields:
            ProcessedMessage objects
        """
        for text in texts:
            yield self.process_message(text)