"""
Telegram API client wrapper using telethon.

BRANCH-2: Data Extraction
Author: Boris (Claude Code)
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any

from telethon import TelegramClient, events
from telethon import connection  # FIXED: Missing import

from src.core.config import get_settings
from src.core.exceptions import TelegramClientError, TelegramAuthenticationError
from src.core.logger import get_logger

logger = get_logger(__name__)


class TelegramClientWrapper:
    """Wrapper around Telethon client with error handling."""

    def __init__(
        self, 
        api_id: int, 
        api_hash: str, 
        phone: str,
        proxy_addr: str,
        proxy_port: int,
        proxy_secret: str,
        session_name: str = "medical_bot"
    ):
        """
        Initialize Telegram client.

        Args:
            api_id: Telegram API ID
            api_hash: Telegram API hash
            phone: Phone number with country code
            proxy_addr: MTProto proxy address
            proxy_port: MTProto proxy port
            proxy_secret: MTProto proxy secret
            session_name: Session file name

        Raises:
            TelegramClientError: If initialization fails
        """
        try:
            self.api_id = api_id
            self.api_hash = api_hash
            self.phone = phone
            self.session_name = session_name

            self.proxy_addr = proxy_addr
            self.proxy_port = int(proxy_port) if proxy_port else None
            self.proxy_secret = proxy_secret

            # FIXED: Proper syntax for TelegramClient initialization
            # FIXED: Only set proxy if all proxy parameters are provided
            if self.proxy_addr and self.proxy_port and self.proxy_secret:
                self.client = TelegramClient(
                    session_name, 
                    api_id, 
                    api_hash,
                    connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
                    proxy=(self.proxy_addr, self.proxy_port, self.proxy_secret)
                )
                logger.info(f"Telegram client initialized with MTProto proxy for {phone}")
            else:
                # No proxy - direct connection
                self.client = TelegramClient(session_name, api_id, api_hash)
                logger.info(f"Telegram client initialized (no proxy) for {phone}")

        except Exception as e:
            raise TelegramClientError(
                f"Failed to initialize Telegram client: {str(e)}",
                details={"phone": phone}
            )

    async def connect(self) -> bool:
        """
        Connect to Telegram.

        Returns:
            True if connected successfully

        Raises:
            TelegramAuthenticationError: If authentication fails
        """
        try:
            await self.client.connect()

            # Check if already authorized
            if not await self.client.is_user_authorized():
                # Send code request
                await self.client.send_code_request(self.phone)
                
                # Get code from user
                code = input("Enter the code you received: ")
                try:
                    await self.client.sign_in(self.phone, code)
                except Exception as e:
                    # FIXED: Better error handling for 2FA
                    if "password" in str(e).lower():
                        password = input("Two-factor authentication enabled. Enter your password: ")
                        await self.client.sign_in(password=password)
                    else:
                        raise TelegramAuthenticationError(
                            f"Failed to sign in: {str(e)}"
                        )

            logger.info("Successfully connected to Telegram")
            return True

        except TelegramAuthenticationError:
            raise
        except Exception as e:
            raise TelegramClientError(
                f"Connection failed: {str(e)}"
            )

    async def disconnect(self) -> None:
        """Disconnect from Telegram."""
        try:
            await self.client.disconnect()
            logger.info("Disconnected from Telegram")
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")

    async def get_messages(
        self,
        channel: str,
        limit: int = 100,
        min_id: int = 0,
        max_id: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get messages from a channel.

        Args:
            channel: Channel name or ID
            limit: Number of messages to retrieve
            min_id: Minimum message ID
            max_id: Maximum message ID

        Returns:
            List of message dictionaries

        Raises:
            TelegramClientError: If retrieval fails
        """
        try:
            logger.debug(f"Fetching {limit} messages from {channel}")

            messages = []
            async for message in self.client.iter_messages(
                channel,
                limit=limit,
                min_id=min_id,
                max_id=max_id,
            ):
                msg_dict = {
                    "id": message.id,
                    "text": message.text or "",
                    "date": message.date,
                    "views": message.views or 0,
                    "forwards": message.forwards or 0,
                    "sender_id": message.sender_id,
                    "media": message.media is not None,
                    "media_type": type(message.media).__name__ if message.media else None,
                }
                messages.append(msg_dict)

            logger.info(f"Retrieved {len(messages)} messages from {channel}")
            return messages

        except Exception as e:
            raise TelegramClientError(
                f"Failed to get messages from {channel}: {str(e)}",
                details={"channel": channel, "limit": limit}
            )

    async def download_media(
        self,
        message_id: int,
        channel: str,
        download_path: str = "./downloads"
    ) -> Optional[str]:
        """
        Download media from message.

        Args:
            message_id: Message ID
            channel: Channel name
            download_path: Path to save media

        Returns:
            Path to downloaded file or None

        Raises:
            TelegramClientError: If download fails
        """
        try:
            message = await self.client.get_messages(channel, ids=message_id)

            if not message.media:
                logger.warning(f"Message {message_id} has no media")
                return None

            file_path = await self.client.download_media(
                message.media,
                file=download_path
            )

            logger.info(f"Downloaded media to {file_path}")
            return str(file_path)

        except Exception as e:
            raise TelegramClientError(
                f"Failed to download media: {str(e)}",
                details={"message_id": message_id, "channel": channel}
            )

    async def get_channel_info(self, channel: str) -> Dict[str, Any]:
        """
        Get channel information.

        Args:
            channel: Channel name

        Returns:
            Channel information dictionary
        """
        try:
            entity = await self.client.get_entity(channel)

            return {
                "name": entity.title,
                "id": entity.id,
                "participants": entity.participants_count if hasattr(entity, 'participants_count') else None,
                "description": entity.description if hasattr(entity, 'description') else None,
            }

        except Exception as e:
            logger.error(f"Failed to get channel info: {e}")
            raise TelegramClientError(f"Failed to get channel info: {str(e)}")

    async def is_connected(self) -> bool:
        """Check if client is connected."""
        try:
            return self.client.is_connected()
        except Exception:
            return False


async def create_telegram_client() -> TelegramClientWrapper:
    """
    Create and connect Telegram client.

    Returns:
        Connected TelegramClientWrapper instance
    """
    settings = get_settings()

    # FIXED: Pass proxy parameters to wrapper
    client = TelegramClientWrapper(
        api_id=settings.telegram_api_id,
        api_hash=settings.telegram_api_hash,
        phone=settings.telegram_phone,
        proxy_addr=getattr(settings, 'telegram_proxy_addr', None),
        proxy_port=getattr(settings, 'telegram_proxy_port', None),
        proxy_secret=getattr(settings, 'telegram_proxy_secret', None),
    )

    await client.connect()
    return client


if __name__ == "__main__":
    import sys

    async def main():
        """Test client."""
        client = await create_telegram_client()

        # Get messages from a channel
        messages = await client.get_messages("CheMedTelegram", limit=10)
        print(f"Retrieved {len(messages)} messages")

        await client.disconnect()

    # FIXED: Simplified asyncio.run check
    asyncio.run(main())