"""
Medical Named Entity Recognition using spaCy and scSpacy.

BRANCH-3: NLP Pipeline
Author: Boris (Claude Code)
"""

import re
from dataclasses import dataclass
from typing import List, Optional

import spacy
from spacy.tokens import Doc

from src.core.exceptions import ModelLoadingError, EntityExtractionError
from src.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MedicalEntity:
    """Medical entity extracted from text."""

    text: str
    entity_type: str  # MEDICATION, DOSAGE, CONDITION, SYMPTOM, PRICE, etc.
    start_char: int
    end_char: int
    confidence: float
    normalized: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "type": self.entity_type,
            "start": self.start_char,
            "end": self.end_char,
            "confidence": self.confidence,
            "normalized": self.normalized,
        }


class MedicalNER:
    """Medical Named Entity Recognizer using spaCy."""

    # Medical entity patterns for rule-based extraction
    DOSAGE_PATTERN = r"(\d+\.?\d*)\s*(mg|g|ml|tablet|capsule|unit|IU|mmol)"
    PRICE_PATTERN = r"(\d+\.?\d*)\s*(ETB|birr|USD|dollar|cent|EUR)"
    FREQUENCY_PATTERN = r"(once|twice|thrice|daily|every|per|times?)\s*(\d+)?(?:\s*(day|hour|week|month|year))?"

    def __init__(self, model_name: str = "en_core_sci_md"):
        """
        Initialize Medical NER.

        Args:
            model_name: spaCy model name

        Raises:
            ModelLoadingError: If model cannot be loaded
        """
        try:
            self.nlp = spacy.load(model_name)
            logger.info(f"Loaded medical NER model: {model_name}")
        except OSError as e:
            raise ModelLoadingError(
                f"Failed to load spaCy model: {model_name}",
                details={"error": str(e)}
            )

        # Initialize entity patterns
        self._init_patterns()

    def _init_patterns(self) -> None:
        """Initialize regex patterns for entity extraction."""
        self.dosage_regex = re.compile(self.DOSAGE_PATTERN, re.IGNORECASE)
        self.price_regex = re.compile(self.PRICE_PATTERN, re.IGNORECASE)
        self.frequency_regex = re.compile(self.FREQUENCY_PATTERN, re.IGNORECASE)

    def extract_entities(self, text: str) -> List[MedicalEntity]:
        """
        Extract medical entities from text.

        Args:
            text: Input text

        Returns:
            List of MedicalEntity objects

        Raises:
            EntityExtractionError: If extraction fails

        Example:
            >>> ner = MedicalNER()
            >>> entities = ner.extract_entities("Amoxicillin 500mg twice daily for fever")
            >>> len(entities) > 0
            True
        """
        try:
            entities = []

            # spaCy NER
            doc = self.nlp(text)
            spacy_entities = self._extract_spacy_entities(doc)
            entities.extend(spacy_entities)

            # Rule-based extraction
            rule_entities = self._extract_rule_based_entities(text)
            entities.extend(rule_entities)

            # Remove duplicates
            entities = self._deduplicate_entities(entities)

            logger.debug(f"Extracted {len(entities)} entities from text")
            return entities

        except Exception as e:
            raise EntityExtractionError(
                f"Failed to extract entities: {str(e)}",
                details={"text_length": len(text)}
            )

    def _extract_spacy_entities(self, doc: Doc) -> List[MedicalEntity]:
        """Extract entities using spaCy."""
        entities = []

        for ent in doc.ents:
            # Map spaCy entity types to medical types
            entity_type = self._map_entity_type(ent.label_)

            if entity_type:
                entities.append(
                    MedicalEntity(
                        text=ent.text,
                        entity_type=entity_type,
                        start_char=ent.start_char,
                        end_char=ent.end_char,
                        confidence=0.85,  # spaCy doesn't provide confidence by default
                    )
                )

        return entities

    def _extract_rule_based_entities(self, text: str) -> List[MedicalEntity]:
        """Extract entities using regex patterns."""
        entities = []

        # Dosage extraction
        for match in self.dosage_regex.finditer(text):
            entities.append(
                MedicalEntity(
                    text=match.group(0),
                    entity_type="DOSAGE",
                    start_char=match.start(),
                    end_char=match.end(),
                    confidence=0.90,
                )
            )

        # Price extraction
        for match in self.price_regex.finditer(text):
            entities.append(
                MedicalEntity(
                    text=match.group(0),
                    entity_type="PRICE",
                    start_char=match.start(),
                    end_char=match.end(),
                    confidence=0.88,
                )
            )

        # Frequency extraction
        for match in self.frequency_regex.finditer(text):
            entities.append(
                MedicalEntity(
                    text=match.group(0),
                    entity_type="FREQUENCY",
                    start_char=match.start(),
                    end_char=match.end(),
                    confidence=0.82,
                )
            )

        return entities

    def _map_entity_type(self, spacy_label: str) -> Optional[str]:
        """Map spaCy entity labels to medical entity types."""
        mapping = {
            "PRODUCT": "MEDICATION",
            "PERSON": None,  # Skip person names
            "GPE": None,  # Skip locations
            "ORG": "FACILITY",
            "QUANTITY": "DOSAGE",
            "DATE": "DATE",
        }
        return mapping.get(spacy_label, "ENTITY")

    def _deduplicate_entities(self, entities: List[MedicalEntity]) -> List[MedicalEntity]:
        """Remove overlapping entities, keeping highest confidence."""
        if not entities:
            return []

        # Sort by start position, then by confidence (descending)
        sorted_entities = sorted(
            entities,
            key=lambda e: (e.start_char, -e.confidence)
        )

        deduped = []
        for entity in sorted_entities:
            # Check if overlaps with existing entity
            overlaps = False
            for existing in deduped:
                if (entity.start_char >= existing.start_char and
                    entity.start_char < existing.end_char):
                    overlaps = True
                    break
            
            if not overlaps:
                deduped.append(entity)

        return sorted(deduped, key=lambda e: e.start_char)

    def get_entities_by_type(
        self,
        entities: List[MedicalEntity],
        entity_type: str
    ) -> List[MedicalEntity]:
        """
        Filter entities by type.

        Args:
            entities: List of entities
            entity_type: Entity type to filter

        Returns:
            Filtered entities
        """
        return [e for e in entities if e.entity_type == entity_type]

    def extract_medications(self, text: str) -> List[MedicalEntity]:
        """
        Extract medication entities.

        Args:
            text: Input text

        Returns:
            List of medication entities
        """
        entities = self.extract_entities(text)
        return self.get_entities_by_type(entities, "MEDICATION")

    def extract_conditions(self, text: str) -> List[MedicalEntity]:
        """
        Extract condition entities.

        Args:
            text: Input text

        Returns:
            List of condition entities
        """
        entities = self.extract_entities(text)
        return self.get_entities_by_type(entities, "CONDITION")