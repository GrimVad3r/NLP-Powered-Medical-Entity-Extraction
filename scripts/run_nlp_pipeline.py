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
        logger.error(f"Failed to load messages from {input_file}: {e}")
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


def find_all_json_files(base_dir: str = "data/raw") -> List[Path]:
    """
    Find all JSON files in data/raw/*/**.json structure.

    Args:
        base_dir: Base directory to search (default: data/raw)

    Returns:
        List of Path objects for JSON files
    """
    base_path = Path(base_dir)
    
    if not base_path.exists():
        logger.warning(f"Directory {base_dir} does not exist")
        return []
    
    # Find all JSON files recursively
    json_files = list(base_path.rglob("*.json"))
    
    logger.info(f"Found {len(json_files)} JSON files in {base_dir}")
    
    # Log the structure
    channels = {}
    for json_file in json_files:
        # Get channel name (parent directory name)
        channel_name = json_file.parent.name
        if channel_name not in channels:
            channels[channel_name] = []
        channels[channel_name].append(json_file.name)
    
    for channel, files in channels.items():
        logger.info(f"  {channel}: {len(files)} files")
    
    return json_files


def process_single_file(
    input_file: Path,
    processor: MedicalMessageProcessor,
    output_base_dir: str = "./data/processed"
) -> Dict[str, Any]:
    """
    Process a single JSON file.

    Args:
        input_file: Path to input JSON file
        processor: MedicalMessageProcessor instance
        output_base_dir: Base directory for output files

    Returns:
        Dictionary with processing statistics
    """
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {input_file}")
        logger.info(f"{'='*60}")

        # Determine output file path
        # Input: data/raw/channel_name/filename.json
        # Output: data/processed/channel_name/filename.json
        channel_name = input_file.parent.name
        output_dir = Path(output_base_dir) / channel_name
        output_file = output_dir / input_file.name

        # Check if already processed
        if output_file.exists():
            logger.info(f"⏭️  Already processed, skipping: {output_file}")
            return {"status": "skipped", "file": str(input_file)}

        # Load messages
        messages = load_messages(str(input_file))

        if not messages:
            logger.warning(f"No messages found in {input_file}")
            return {"status": "no_messages", "file": str(input_file)}

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

                # Log progress every 100 messages
                if i % 100 == 0:
                    logger.info(f"  Progress: {i}/{len(messages)} messages...")

            except Exception as e:
                logger.warning(f"Error processing message {i}: {e}")
                continue

        # Calculate statistics
        processed_count = len(results)
        
        if processed_count == 0:
            logger.warning(f"No messages successfully processed from {input_file}")
            return {"status": "failed", "file": str(input_file)}

        medical_percentage = (medical_count / processed_count * 100)
        avg_quality_score = total_quality_score / processed_count
        avg_entities = total_entities / processed_count

        logger.info(f"\n{'='*60}")
        logger.info(f"Results for {input_file.name}")
        logger.info(f"{'='*60}")
        logger.info(f"Processed: {processed_count} messages")
        logger.info(f"Medical: {medical_count} ({medical_percentage:.1f}%)")
        logger.info(f"Total entities: {total_entities}")
        logger.info(f"Avg entities/message: {avg_entities:.2f}")
        logger.info(f"Avg quality score: {avg_quality_score:.3f}")

        # Save results
        save_results(results, str(output_file))
        logger.info(f"✅ Saved to: {output_file}")

        return {
            "status": "success",
            "file": str(input_file),
            "output": str(output_file),
            "processed": processed_count,
            "medical": medical_count,
            "entities": total_entities,
            "avg_quality": avg_quality_score
        }

    except Exception as e:
        logger.error(f"❌ Failed to process {input_file}: {e}")
        return {"status": "error", "file": str(input_file), "error": str(e)}


def run_nlp_pipeline(
    input_path: str = None,
    output_base_dir: str = "data/processed",
    batch_size: int = 32,
    use_gpu: bool = True,
    skip_existing: bool = True
):
    """
    Run NLP pipeline on messages.

    Args:
        input_path: Input file or directory (if None, processes all files in data/raw)
        output_base_dir: Base directory for output files
        batch_size: Batch size for processing
        use_gpu: Whether to use GPU
        skip_existing: Skip files that have already been processed
    """
    try:
        logger.info("=" * 60)
        logger.info("NLP Processing Pipeline")
        logger.info("=" * 60)

        # Initialize processor
        logger.info("Initializing NLP models...")
        processor = MedicalMessageProcessor(use_gpu=use_gpu)
        logger.info("✅ Models loaded successfully")

        # Determine input files
        if input_path:
            input_path_obj = Path(input_path)
            
            if input_path_obj.is_file():
                # Single file
                json_files = [input_path_obj]
            elif input_path_obj.is_dir():
                # Directory - find all JSON files
                json_files = find_all_json_files(str(input_path_obj))
            else:
                logger.error(f"Input path does not exist: {input_path}")
                return
        else:
            # Default: process all files in data/raw
            json_files = find_all_json_files("data/raw")

        if not json_files:
            logger.error("No JSON files found to process")
            return

        logger.info(f"\n{'='*60}")
        logger.info(f"Found {len(json_files)} files to process")
        logger.info(f"{'='*60}\n")

        # Process all files
        all_stats = []
        success_count = 0
        skip_count = 0
        error_count = 0

        for i, json_file in enumerate(json_files, 1):
            logger.info(f"\n[{i}/{len(json_files)}] Processing {json_file.name}...")
            
            stats = process_single_file(json_file, processor, output_base_dir)
            all_stats.append(stats)

            if stats["status"] == "success":
                success_count += 1
            elif stats["status"] == "skipped":
                skip_count += 1
            else:
                error_count += 1

        # Final summary
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total files: {len(json_files)}")
        logger.info(f"Successfully processed: {success_count}")
        logger.info(f"Skipped (already processed): {skip_count}")
        logger.info(f"Errors: {error_count}")

        # Aggregate statistics for successful files
        total_messages = sum(s.get("processed", 0) for s in all_stats if s["status"] == "success")
        total_medical = sum(s.get("medical", 0) for s in all_stats if s["status"] == "success")
        total_entities = sum(s.get("entities", 0) for s in all_stats if s["status"] == "success")

        if total_messages > 0:
            logger.info(f"\nTotal messages processed: {total_messages}")
            logger.info(f"Total medical messages: {total_medical} ({total_medical/total_messages*100:.1f}%)")
            logger.info(f"Total entities extracted: {total_entities}")
            logger.info(f"Avg entities per message: {total_entities/total_messages:.2f}")

        logger.info("\n" + "=" * 60)
        logger.info("✅ NLP pipeline completed!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {str(e)}")
        raise


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="NLP processing pipeline for medical message extraction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all files in data/raw/
  python run_nlp.py

  # Process specific file
  python run_nlp.py --input data/raw/CheMedTelegram/scrape_20240214.json

  # Process specific channel directory
  python run_nlp.py --input data/raw/CheMedTelegram/

  # Use GPU for faster processing
  python run_nlp.py --gpu

  # Force reprocessing of already processed files
  python run_nlp.py --force
        """
    )
    parser.add_argument(
        "--input",
        help="Input JSON file or directory (default: data/raw)"
    )
    parser.add_argument(
        "--output-dir",
        default="data/processed",
        help="Output base directory (default: data/processed)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for processing (default: 32)"
    )
    parser.add_argument(
        "--gpu",
        action="store_true",
        help="Use GPU for processing"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reprocessing of already processed files"
    )

    args = parser.parse_args()

    logger.info(f"Input: {args.input or 'data/raw (all files)'}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"GPU: {args.gpu}")
    logger.info(f"Force reprocess: {args.force}")

    run_nlp_pipeline(
        input_path=args.input,
        output_base_dir=args.output_dir,
        batch_size=args.batch_size,
        use_gpu=args.gpu,
        skip_existing=not args.force
    )


if __name__ == "__main__":
    main()