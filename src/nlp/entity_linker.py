"""
Entity linking and medication normalization.

BRANCH-3: NLP Pipeline
Author: Boris (Claude Code)
"""

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import List, Optional

from src.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class LinkingResult:
    """Result of entity linking."""

    original: str
    canonical: str
    category: str
    confidence: float
    found: bool
    match_type: str  # "exact", "fuzzy", "partial"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "original": self.original,
            "canonical": self.canonical,
            "category": self.category,
            "confidence": self.confidence,
            "found": self.found,
            "match_type": self.match_type,
        }


class MedicalEntityLinker:
    """Link medical entities to knowledge bases."""

    # Knowledge base of medications
    MEDICATIONS_KB = {
        # Antibiotics
        "amoxicillin": {"canonical": "Amoxicillin", "category": "Antibiotics", "aliases": ["amoxycillin", "amoxil"]},
        "penicillin": {"canonical": "Penicillin", "category": "Antibiotics", "aliases": ["penicllin"]},
        "cephalexin": {"canonical": "Cephalexin", "category": "Antibiotics", "aliases": ["cefalexin", "keflex"]},
        "tetracycline": {"canonical": "Tetracycline", "category": "Antibiotics", "aliases": ["tetracyclin"]},
        "azithromycin": {"canonical": "Azithromycin", "category": "Antibiotics", "aliases": ["azithomycin", "zithromax"]},

        # Antimalarials
        "artemether": {"canonical": "Artemether", "category": "Antimalarials", "aliases": ["artether"]},
        "quinine": {"canonical": "Quinine", "category": "Antimalarials", "aliases": []},
        "chloroquine": {"canonical": "Chloroquine", "category": "Antimalarials", "aliases": ["chloroquin"]},
        "artemisinin": {"canonical": "Artemisinin", "category": "Antimalarials", "aliases": ["artemisinin"]},

        # Analgesics
        "paracetamol": {"canonical": "Paracetamol", "category": "Analgesics", "aliases": ["acetaminophen", "tylenol"]},
        "ibuprofen": {"canonical": "Ibuprofen", "category": "Analgesics", "aliases": ["ibuprofen"]},
        "aspirin": {"canonical": "Aspirin", "category": "Analgesics", "aliases": ["acetylsalicylic acid"]},

        # Antihistamines
        "cetirizine": {"canonical": "Cetirizine", "category": "Antihistamines", "aliases": ["zyrtec"]},
        "loratadine": {"canonical": "Loratadine", "category": "Antihistamines", "aliases": ["claritin"]},

        # Other common medications
        "metformin": {"canonical": "Metformin", "category": "Antidiabetics", "aliases": ["glucophage"]},
        "lisinopril": {"canonical": "Lisinopril", "category": "Antihypertensives", "aliases": ["prinivil"]},
        "atorvastatin": {"canonical": "Atorvastatin", "category": "Statins", "aliases": ["lipitor"]},
    }

    # Conditions knowledge base
    CONDITIONS_KB = {
        "malaria": {"canonical": "Malaria", "category": "Infectious Disease"},
        "fever": {"canonical": "Fever", "category": "Symptom"},
        "cough": {"canonical": "Cough", "category": "Symptom"},
        "headache": {"canonical": "Headache", "category": "Symptom"},
        "pain": {"canonical": "Pain", "category": "Symptom"},
        "infection": {"canonical": "Infection", "category": "Condition"},
        "diabetes": {"canonical": "Diabetes", "category": "Chronic Disease"},
        "hypertension": {"canonical": "Hypertension", "category": "Chronic Disease"},
        "asthma": {"canonical": "Asthma", "category": "Respiratory Disease"},
    }

    def __init__(self):
        """Initialize entity linker."""
        self.medications_kb = self.MEDICATIONS_KB
        self.conditions_kb = self.CONDITIONS_KB
        logger.info("Entity linker initialized with knowledge bases")

    def link_medication(self, medication_text: str) -> LinkingResult:
        """
        Link medication to knowledge base.

        Args:
            medication_text: Medication name/text

        Returns:
            LinkingResult with linking information

        Example:
            >>> linker = MedicalEntityLinker()
            >>> result = linker.link_medication("Amoxycillin")
            >>> result.canonical
            'Amoxicillin'
        """
        medication_lower = medication_text.lower().strip()

        # Try exact match
        if medication_lower in self.medications_kb:
            kb_entry = self.medications_kb[medication_lower]
            return LinkingResult(
                original=medication_text,
                canonical=kb_entry["canonical"],
                category=kb_entry["category"],
                confidence=1.0,
                found=True,
                match_type="exact"
            )

        # Try alias match
        for med_key, med_data in self.medications_kb.items():
            if medication_lower in med_data.get("aliases", []):
                return LinkingResult(
                    original=medication_text,
                    canonical=med_data["canonical"],
                    category=med_data["category"],
                    confidence=0.95,
                    found=True,
                    match_type="alias"
                )

        # Try fuzzy match
        fuzzy_result = self._fuzzy_match(medication_lower, self.medications_kb)
        if fuzzy_result:
            return fuzzy_result

        # Not found
        return LinkingResult(
            original=medication_text,
            canonical=medication_text,
            category="Unknown",
            confidence=0.0,
            found=False,
            match_type="none"
        )

    def link_condition(self, condition_text: str) -> LinkingResult:
        """
        Link condition to knowledge base.

        Args:
            condition_text: Condition name/text

        Returns:
            LinkingResult with linking information
        """
        condition_lower = condition_text.lower().strip()

        # Try exact match
        if condition_lower in self.conditions_kb:
            kb_entry = self.conditions_kb[condition_lower]
            return LinkingResult(
                original=condition_text,
                canonical=kb_entry["canonical"],
                category=kb_entry["category"],
                confidence=1.0,
                found=True,
                match_type="exact"
            )

        # Try fuzzy match
        fuzzy_result = self._fuzzy_match(condition_lower, self.conditions_kb)
        if fuzzy_result:
            return fuzzy_result

        # Not found
        return LinkingResult(
            original=condition_text,
            canonical=condition_text,
            category="Unknown",
            confidence=0.0,
            found=False,
            match_type="none"
        )

    def _fuzzy_match(
        self,
        text: str,
        knowledge_base: dict,
        threshold: float = 0.8
    ) -> Optional[LinkingResult]:
        """
        Perform fuzzy string matching.

        Args:
            text: Text to match
            knowledge_base: Knowledge base dictionary
            threshold: Similarity threshold (0-1)

        Returns:
            LinkingResult or None if no match
        """
        best_match = None
        best_score = threshold

        for kb_key, kb_data in knowledge_base.items():
            # Match against key
            similarity = SequenceMatcher(None, text, kb_key).ratio()

            if similarity > best_score:
                best_score = similarity
                best_match = (kb_key, kb_data, similarity)

            # Also match against aliases
            for alias in kb_data.get("aliases", []):
                alias_similarity = SequenceMatcher(None, text, alias).ratio()
                if alias_similarity > best_score:
                    best_score = alias_similarity
                    best_match = (kb_key, kb_data, alias_similarity)

        if best_match:
            kb_key, kb_data, similarity = best_match
            return LinkingResult(
                original=text,
                canonical=kb_data["canonical"],
                category=kb_data["category"],
                confidence=similarity,
                found=True,
                match_type="fuzzy"
            )

        return None

    def add_medication(
        self,
        name: str,
        canonical: str,
        category: str,
        aliases: Optional[List[str]] = None
    ) -> None:
        """Add medication to knowledge base."""
        self.medications_kb[name.lower()] = {
            "canonical": canonical,
            "category": category,
            "aliases": [a.lower() for a in (aliases or [])],
        }
        logger.debug(f"Added medication: {name} -> {canonical}")

    def add_condition(
        self,
        name: str,
        canonical: str,
        category: str
    ) -> None:
        """Add condition to knowledge base."""
        self.conditions_kb[name.lower()] = {
            "canonical": canonical,
            "category": category,
        }
        logger.debug(f"Added condition: {name} -> {canonical}")