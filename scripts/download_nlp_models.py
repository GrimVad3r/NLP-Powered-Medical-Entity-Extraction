#!/usr/bin/env python3
"""
Download required NLP models.

Author: Boris (Claude Code)
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.logger import get_logger

logger = get_logger(__name__)


def download_spacy_models():
    """Download spaCy models."""
    try:
        import spacy

        logger.info("Downloading spaCy medical model...")
        spacy.cli.download("en_core_sci_md")
        logger.info("✅ spaCy model downloaded")

        return True

    except Exception as e:
        logger.error(f"Failed to download spaCy model: {e}")
        return False


def download_transformers_models():
    """Download HuggingFace transformer models."""
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification

        logger.info("Downloading transformer models...")
        model_name = "distilbert-base-uncased-finetuned-sst-2-english"

        logger.info(f"  - Downloading {model_name}...")
        AutoTokenizer.from_pretrained(model_name)
        AutoModelForSequenceClassification.from_pretrained(model_name)

        logger.info("✅ Transformer models downloaded")
        return True

    except Exception as e:
        logger.error(f"Failed to download transformer models: {e}")
        return False


def create_model_directory():
    """Create model storage directory."""
    model_dir = Path("data/nlp_models")
    model_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"✅ Model directory created: {model_dir}")


def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("NLP Models Downloader")
    logger.info("=" * 60)

    try:
        # Create model directory
        create_model_directory()

        # Download spaCy models
        if not download_spacy_models():
            logger.warning("spaCy model download failed")

        # Download transformer models
        if not download_transformers_models():
            logger.warning("Transformer model download failed")

        logger.info("\n" + "=" * 60)
        logger.info("NLP models download complete!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Download failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()