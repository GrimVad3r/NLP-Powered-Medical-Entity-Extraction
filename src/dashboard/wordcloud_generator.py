"""
Word cloud visualization for medical terms.

BRANCH-7: Dashboard
Author: Boris (Claude Code)
"""

from collections import Counter
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import streamlit as st
from wordcloud import WordCloud

from src.core.logger import get_logger

logger = get_logger(__name__)


class MedicalWordCloudGenerator:
    """Generate word clouds from medical data."""

    # Stop words to exclude
    STOP_WORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "was", "are", "were", "be", "been",
        "been", "has", "have", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "must", "can", "patient", "use",
        "using", "available", "please", "contact", "call", "visit", "channel"
    }

    def __init__(
        self,
        width: int = 1200,
        height: int = 600,
        background_color: str = "white",
        colormap: str = "viridis"
    ):
        """
        Initialize word cloud generator.

        Args:
            width: Width of word cloud
            height: Height of word cloud
            background_color: Background color
            colormap: Matplotlib colormap
        """
        self.width = width
        self.height = height
        self.background_color = background_color
        self.colormap = colormap
        logger.info("Word cloud generator initialized")

    def generate_from_text(self, text: str) -> WordCloud:
        """
        Generate word cloud from text.

        Args:
            text: Input text

        Returns:
            WordCloud object

        Example:
            >>> generator = MedicalWordCloudGenerator()
            >>> wc = generator.generate_from_text("malaria fever treatment")
            >>> isinstance(wc, WordCloud)
            True
        """
        try:
            wordcloud = WordCloud(
                width=self.width,
                height=self.height,
                background_color=self.background_color,
                colormap=self.colormap,
                stopwords=self.STOP_WORDS,
                max_words=100,
                relative_scaling=0.5,
                min_font_size=10
            ).generate(text)

            logger.debug("Word cloud generated from text")
            return wordcloud

        except Exception as e:
            logger.error(f"Failed to generate word cloud: {e}")
            raise

    def generate_from_entities(
        self,
        entity_texts: List[str],
        entity_frequencies: Optional[Dict[str, int]] = None
    ) -> WordCloud:
        """
        Generate word cloud from medical entities.

        Args:
            entity_texts: List of entity texts
            entity_frequencies: Optional frequency dictionary

        Returns:
            WordCloud object
        """
        try:
            if entity_frequencies:
                wordcloud = WordCloud(
                    width=self.width,
                    height=self.height,
                    background_color=self.background_color,
                    colormap=self.colormap,
                    max_words=100,
                    relative_scaling=0.5,
                    min_font_size=10
                ).generate_from_frequencies(entity_frequencies)
            else:
                # Create frequency map from entities
                freq = Counter(entity_texts)
                wordcloud = WordCloud(
                    width=self.width,
                    height=self.height,
                    background_color=self.background_color,
                    colormap=self.colormap,
                    max_words=100,
                    relative_scaling=0.5,
                    min_font_size=10
                ).generate_from_frequencies(freq)

            logger.debug(f"Word cloud generated from {len(entity_texts)} entities")
            return wordcloud

        except Exception as e:
            logger.error(f"Failed to generate word cloud from entities: {e}")
            raise

    def get_entity_frequencies(
        self,
        entities: List[str]
    ) -> Dict[str, int]:
        """
        Calculate entity frequencies.

        Args:
            entities: List of entity texts

        Returns:
            Dictionary of frequencies
        """
        frequencies = Counter(entity_texts)
        return dict(frequencies.most_common(100))

    def plot_word_cloud(self, wordcloud: WordCloud) -> plt.Figure:
        """
        Create matplotlib figure from word cloud.

        Args:
            wordcloud: WordCloud object

        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        return fig

    def display_in_streamlit(self, wordcloud: WordCloud, title: str = "Medical Terms Word Cloud") -> None:
        """
        Display word cloud in Streamlit.

        Args:
            wordcloud: WordCloud object
            title: Title to display
        """
        fig = self.plot_word_cloud(wordcloud)
        st.pyplot(fig)
        st.caption(title)

    def generate_statistics(
        self,
        entity_frequencies: Dict[str, int]
    ) -> Dict:
        """
        Generate statistics from word cloud data.

        Args:
            entity_frequencies: Entity frequency dictionary

        Returns:
            Dictionary of statistics
        """
        total_words = sum(entity_frequencies.values())
        unique_words = len(entity_frequencies)

        top_10 = sorted(
            entity_frequencies.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        stats = {
            "total_word_occurrences": total_words,
            "unique_words": unique_words,
            "top_10": dict(top_10),
            "average_frequency": total_words / unique_words if unique_words > 0 else 0,
            "most_common": top_10[0][0] if top_10 else None,
            "most_common_frequency": top_10[0][1] if top_10 else 0,
        }

        return stats


class StreamlitWordCloudDashboard:
    """Streamlit dashboard for word cloud visualization."""

    def __init__(self):
        """Initialize dashboard."""
        self.generator = MedicalWordCloudGenerator()

    def display_medication_wordcloud(self, medications: List[str]) -> None:
        """
        Display medications word cloud.

        Args:
            medications: List of medication names
        """
        st.subheader("💊 Medication Word Cloud")

        if not medications:
            st.warning("No medications found")
            return

        try:
            wordcloud = self.generator.generate_from_entities(medications)
            self.generator.display_in_streamlit(
                wordcloud,
                "Top Medications Mentioned"
            )

            # Display statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Medications", len(medications))
            with col2:
                st.metric("Unique Medications", len(set(medications)))
            with col3:
                st.metric("Most Common", max(set(medications), key=medications.count) if medications else "N/A")

            # Display top medications
            st.subheader("Top 10 Medications")
            freq = Counter(medications)
            top_meds = freq.most_common(10)
            
            for idx, (med, count) in enumerate(top_meds, 1):
                st.write(f"{idx}. **{med}** - {count} mentions")

        except Exception as e:
            logger.error(f"Error displaying medication word cloud: {e}")
            st.error(f"Error: {str(e)}")

    def display_condition_wordcloud(self, conditions: List[str]) -> None:
        """
        Display conditions word cloud.

        Args:
            conditions: List of condition names
        """
        st.subheader("🏥 Condition Word Cloud")

        if not conditions:
            st.warning("No conditions found")
            return

        try:
            wordcloud = self.generator.generate_from_entities(conditions)
            self.generator.display_in_streamlit(
                wordcloud,
                "Medical Conditions Mentioned"
            )

            # Display statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Mentions", len(conditions))
            with col2:
                st.metric("Unique Conditions", len(set(conditions)))
            with col3:
                st.metric("Most Common", max(set(conditions), key=conditions.count) if conditions else "N/A")

        except Exception as e:
            logger.error(f"Error displaying condition word cloud: {e}")
            st.error(f"Error: {str(e)}")

    def display_entity_wordcloud(self, entities: List[Tuple[str, int]]) -> None:
        """
        Display generic entity word cloud.

        Args:
            entities: List of (entity, frequency) tuples
        """
        st.subheader("🏷️ Entity Word Cloud")

        if not entities:
            st.warning("No entities found")
            return

        try:
            freq_dict = dict(entities)
            wordcloud = self.generator.generate_from_entities(
                list(freq_dict.keys()),
                freq_dict
            )
            self.generator.display_in_streamlit(
                wordcloud,
                "All Entities"
            )

            # Statistics
            stats = self.generator.generate_statistics(freq_dict)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Entities", stats["total_word_occurrences"])
            with col2:
                st.metric("Unique Entities", stats["unique_words"])
            with col3:
                st.metric("Average Frequency", f"{stats['average_frequency']:.1f}")

        except Exception as e:
            logger.error(f"Error displaying entity word cloud: {e}")
            st.error(f"Error: {str(e)}")