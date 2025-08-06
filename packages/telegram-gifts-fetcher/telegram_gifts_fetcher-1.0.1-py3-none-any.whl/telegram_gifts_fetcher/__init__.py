"""Telegram Gifts Fetcher - The first library to fetch Telegram Star Gifts"""

from .fetcher import (
    get_user_gifts_extended,
    handle_dependency_errors,
    check_circular_dependencies,
    fix_circular_dependencies,
    DependencyError
)

__version__ = "1.0.0"
__author__ = "Th3ryks"
__email__ = ""
__description__ = "The first and only library to fetch Telegram Star Gifts from user profiles"

__all__ = [
    "get_user_gifts_extended",
    "handle_dependency_errors",
    "check_circular_dependencies",
    "fix_circular_dependencies",
    "DependencyError"
]