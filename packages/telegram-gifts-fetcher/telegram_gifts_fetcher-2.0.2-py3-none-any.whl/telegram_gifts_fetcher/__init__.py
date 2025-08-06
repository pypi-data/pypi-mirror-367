"""Telegram Gifts Fetcher - A tool to fetch Telegram gift data."""

__version__ = "2.0.2"
__author__ = "Th3ryks"


from .client import TelegramGiftsClient
from .models import Gift, GiftsResponse
from .config import config

__all__ = [
    "TelegramGiftsClient",
    "Gift",
    "GiftsResponse",
    "config"
]