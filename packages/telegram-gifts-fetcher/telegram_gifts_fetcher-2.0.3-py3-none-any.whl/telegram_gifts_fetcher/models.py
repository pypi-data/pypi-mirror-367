"""Data models for telegram-gifts-fetcher."""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any, List
import json


""" --- MODELS --- """

@dataclass
class Gift:
    """Gift data model."""
    received_date: int  # Unix timestamp
    message: Optional[str] = None  # Gift message (if any)
    name_hidden: bool = True  # Whether sender name is hidden
    can_upgrade: bool = False  # Whether gift can be upgraded
    pinned_to_top: bool = False  # Whether gift is pinned
    type: str = "star_gift"  # Gift type classification
    transfer_stars: int = 0  # Stars value for transfer (if applicable)
    user_convert_stars: int = 0  # Stars value for conversion (if applicable)
    name: str = ""  # Gift name
    slug: str = ""  # Gift slug
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert gift to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Gift':
        """Create gift from dictionary."""
        return cls(**data)
    
    @property
    def is_anonymous(self) -> bool:
        """Check if gift is anonymous."""
        return self.from_id is None or self.name_hidden


@dataclass
class GiftsResponse:
    """Response model for gifts data."""
    gifts: List[Gift]
    count_gifts: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            'gifts': [gift.to_dict() for gift in self.gifts],
            'count_gifts': self.count_gifts
        }