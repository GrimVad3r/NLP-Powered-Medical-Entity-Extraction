#!/usr/bin/env python3
"""
Run NLP processing pipeline on extracted messages.

Author: Boris (Claude Code)
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.logger import get_logger
from src.nlp.message_processor import MedicalMessageProcessor

logger = get_logger(__name__)


def load_messages(input_file: str) -> List[str]:
    """
    Load messages from JSON file.

    Args:
        input_file: Path to JSON file with messages

    Returns:
        List of message texts
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle different formats
        if isinstance(data, list):
            messages = [msg.get('text', '') if isinstance(msg, dict) else str(msg) for msg in data]
        elif isinstance(data, dict) and 'messages' in data:
            messages = [msg.get('text', '') for msg in data['messages']]
        else:
            messages = []

        logger.info(f"Loaded {len(messages)} messages from {input_file}")
        return messages

    except Exception as e:
        logger.error(f"Failed to load messages: {e}")
        return []


def save_results(results: List[Dict[str, Any]], output_file: str) -> None:
    """
    Save processing results to JSON file.

    Args:
        results: List of processing results
        output_file: Path to output file
    """
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([r.to_dict() for r in results], f, indent=2, default=str)

        logger.info(f"Saved {len(results)} results to {output_file}")

    except Exception as e:
        logger.error(f"Failed to save results: {e}")


def run_nlp_pipeline(
    input_file: str,
    output_file: str = None,
    batch_size: int = 32,
    use_gpu: bool = False,
):
    """
    Run NLP pipeline on messages.

    Args:
        input_file: Input JSON file with messages
        output_file: Output JSON file for results
        batch_size: Batch size for processing
        use_gpu: Whether to use GPU
    """
    try:
        logger.info("=" * 60)
        logger.info("NLP Processing Pipeline")
        logger.info("=" * 60)

        # Initialize processor
        logger.info("Initializing NLP models...")
        processor = MedicalMessageProcessor(use_gpu=use_gpu)
        logger.info("✅ Models loaded successfully")

        # Load messages
        logger.info(f"Loading messages from {input_file}...")
        messages = load_messages(input_file)

        if not messages:
            logger.error("No messages found")
            return

        # Process messages
        logger.info(f"Processing {len(messages)} messages...")
        results = []
        medical_count = 0
        total_entities = 0
        total_quality_score = 0.0

        for i, message in enumerate(messages, 1):
            if not message or not message.strip():
                continue

            try:
                result = processor.process_message(message)
                results.append(result)

                if result.is_medical:
                    medical_count += 1

                total_entities += len(result.entities)
                total_quality_score += result.quality_score

                # Log progress
                if i % 100 == 0:
                    logger.info(f"  Processed {i}/{len(messages)} messages...")

            except Exception as e:
                logger.warning(f"Error processing message {i}: {e}")
                continue

        # Calculate statistics
        logger.info("\n" + "=" * 60)
        logger.info("Processing Results")
        logger.info("=" * 60)

        processed_count = len(results)
        medical_percentage = (medical_count / processed_count * 100) if processed_count > 0 else 0
        avg_quality_score = total_quality_score / processed_count if processed_count > 0 else 0
        avg_entities = total_entities / processed_count if processed_count > 0 else 0

        logger.info(f"Processed: {processed_count} messages")
        logger.info(f"Medical: {medical_count} ({medical_percentage:.1f}%)")
        logger.info(f"Non-medical: {processed_count - medical_count} ({100 - medical_percentage:.1f}%)")
        logger.info(f"Total entities: {total_entities}")
        logger.info(f"Avg entities per message: {avg_entities:.2f}")
        logger.info(f"Avg quality score: {avg_quality_score:.3f}")

        # Save results
        if output_file:
            save_results(results, output_file)

        logger.info("\n" + "=" * 60)
        logger.info("NLP pipeline completed!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {str(e)}")
        raise


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="NLP processing pipeline")
    parser.add_argument(
        "--input",
        required=True,
        help="Input JSON file with messages"
    )
    parser.add_argument(
        "--output",
        help="Output JSON file for results"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for processing"
    )
    parser.add_argument(
        "--gpu",
        action="store_true",
        help="Use GPU"
    )

    args = parser.parse_args()

    logger.info(f"Input file: {args.input}")
    logger.info(f"Output file: {args.output}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"GPU: {args.gpu}")

    run_nlp_pipeline(
        args.input,
        args.output,
        args.batch_size,
        args.gpu
    )


if __name__ == "__main__":
    main()