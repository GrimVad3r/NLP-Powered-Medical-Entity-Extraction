"""Media downloading utilities."""
import asyncio
from pathlib import Path
from typing import Optional
from ..core.logger import get_logger
from ..core.exceptions import MediaDownloadError
logger = get_logger(name)
class MediaDownloader:
"""Download media from messages."""
def __init__(self, download_dir: str = "data/media"):
    """Initialize downloader."""
    self.download_dir = Path(download_dir)
    self.download_dir.mkdir(parents=True, exist_ok=True)

async def download_image(self, message_id: int, file_path: str) -> Optional[str]:
    """Download image."""
    try:
        logger.debug(f"Downloading image for message {message_id}")
        # Placeholder - actual implementation would use telethon client
        return file_path
    except Exception as e:
        raise MediaDownloadError(f"Failed to download image: {e}")

def organize_by_date(self, file_path: Path) -> Path:
    """Organize files by date."""
    from datetime import datetime
    today = datetime.now()
    date_dir = self.download_dir / str(today.year) / f"{today.month:02d}"
    date_dir.mkdir(parents=True, exist_ok=True)
    return date_dir / file_path.name

def validate_media_file(self, file_path: Path) -> bool:
    """Validate downloaded media file."""
    return file_path.exists() and file_path.stat().st_size > 0