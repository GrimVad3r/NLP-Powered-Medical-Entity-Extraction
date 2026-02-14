#!/usr/bin/env python3

# ══════════════════════════════════════════════════════════════════════
# CRITICAL: SSL bypass must happen BEFORE any huggingface imports
# ══════════════════════════════════════════════════════════════════════

import os

# Method 1: Disable SSL verification for huggingface_hub (most reliable)
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["CURL_CA_BUNDLE"] = ""  # Disable for huggingface_hub
os.environ["REQUESTS_CA_BUNDLE"] = ""  # Disable for requests

# Method 2: For older versions, try this
os.environ["HF_HUB_OFFLINE"] = "0"  # Ensure online mode

import sys
import subprocess
from pathlib import Path
import urllib3
import warnings

# Suppress SSL warnings since we're bypassing verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

from src.core.logger import get_logger
logger = get_logger(__name__)

# ──────────────────────────────────────────────
#  CONFIG
# ──────────────────────────────────────────────

MODEL_DIR = Path("./models/nlp_models")
SCISPACY_MODEL_URL = "https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_md-0.5.4.tar.gz"
TRANSFORMER_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
CORP_CA_PATH = os.getenv("CORP_CA_PATH")  # Define this variable


def is_spacy_model_installed(model_name: str = "en_core_sci_md") -> bool:
    try:
        import spacy
        spacy.load(model_name)
        return True
    except (ImportError, OSError):
        return False


def download_spacy_models():
    if is_spacy_model_installed():
        logger.info("en_core_sci_md already installed → skipping")
        return True

    try:
        logger.info("Installing scispacy + en_core_sci_md model...")

        pip_base = [sys.executable, "-m", "pip", "install", "--quiet"]

        # Add trusted-host flags for SSL bypass
        extra_pip_args = [
            "--trusted-host", "s3-us-west-2.amazonaws.com",
            "--trusted-host", "pypi.org",
            "--trusted-host", "files.pythonhosted.org",
        ]

        # 1. Install scispacy library (from PyPI)
        subprocess.run(
            pip_base + extra_pip_args + ["scispacy"],
            check=True
        )

        # 2. Install model from direct URL
        subprocess.run(
            pip_base + extra_pip_args + [SCISPACY_MODEL_URL],
            check=True
        )

        # Smoke test
        import spacy
        _ = spacy.load("en_core_sci_md")
        logger.info("✅ scispaCy model ready")
        return True

    except Exception as e:
        logger.error(f"scispaCy installation failed: {e}")
        logger.info("Tip: If SSL still fails → download tar.gz manually via browser → pip install ./en_core_sci_md-0.5.4.tar.gz")
        return False


def is_transformer_model_present() -> bool:
    return (MODEL_DIR / "classifier" / "config.json").is_file()


def download_transformers_models():
    if is_transformer_model_present():
        logger.info("Transformer model already exists → skipping download")
        return True

    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        
        logger.warning(
            "⚠️ Using insecure mode (SSL verification disabled) for Hugging Face downloads. "
            "This is temporary — strongly prefer getting the corporate root CA PEM from IT."
        )

        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        save_path = MODEL_DIR / "classifier"

        logger.info(f"Downloading {TRANSFORMER_MODEL} → {save_path}")

        # The environment variables set at the top will handle SSL bypass
        tokenizer = AutoTokenizer.from_pretrained(
            TRANSFORMER_MODEL,
            cache_dir=save_path,
        )
        model = AutoModelForSequenceClassification.from_pretrained(
            TRANSFORMER_MODEL,
            cache_dir=save_path,
        )

        tokenizer.save_pretrained(save_path)
        model.save_pretrained(save_path)

        logger.info(f"✅ Saved to {save_path}")
        return True

    except Exception as e:
        logger.error(f"Transformers download failed: {e}")
        logger.info(
            "Fallback options (try in order):\n"
            "1. Verify environment variables are set before running:\n"
            "   set CURL_CA_BUNDLE=\n"
            "   set REQUESTS_CA_BUNDLE=\n"
            "2. Use git environment variable:\n"
            "   set GIT_SSL_NO_VERIFY=1\n"
            "3. Manual download (safest):\n"
            "   - On unrestricted machine: from_pretrained() + save_pretrained('./classifier')\n"
            "   - Copy folder to ./models/nlp_models/classifier\n"
            "4. Get corporate CA certificate from IT and set:\n"
            "   set REQUESTS_CA_BUNDLE=C:\\path\\to\\corp-ca.pem"
        )
        return False


def main():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Environment SSL settings:")
    logger.info(f"  CURL_CA_BUNDLE: {os.getenv('CURL_CA_BUNDLE', 'not set')}")
    logger.info(f"  REQUESTS_CA_BUNDLE: {os.getenv('REQUESTS_CA_BUNDLE', 'not set')}")

    spacy_ok = download_spacy_models()
    trans_ok = download_transformers_models()

    if spacy_ok and trans_ok:
        logger.info("✅ All models are ready!")
    else:
        logger.error("❌ Some downloads failed.")
        logger.info("\nNext steps:")
        logger.info("  1. Ask IT for the corporate root CA PEM file")
        logger.info("  2. Set environment variable: REQUESTS_CA_BUNDLE=C:\\path\\to\\corp-ca.pem")
        logger.info("  3. Or accept security risk and run with SSL verification disabled (current mode)")


if __name__ == "__main__":
    main()