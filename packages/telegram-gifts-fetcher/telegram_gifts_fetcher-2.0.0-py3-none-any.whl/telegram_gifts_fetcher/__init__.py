"""Telegram Gifts Fetcher - A tool to fetch Telegram gift data."""

__version__ = "2.0.0"
__author__ = "Th3ryks"
__email__ = "th3ryks@example.com"

from .client import TelegramGiftsClient
from .models import Gift, GiftsResponse
from .config import config

__all__ = [
    "TelegramGiftsClient",
    "Gift",
    "GiftsResponse",
    "config"
]