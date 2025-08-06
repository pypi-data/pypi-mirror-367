"""Configuration module for telegram-gifts-fetcher."""

import os
from typing import Optional
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


""" --- CONFIG --- """

class Config:
    """Configuration class for the application."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self.api_id: Optional[int] = self._get_env_int('API_ID')
        self.api_hash: Optional[str] = os.getenv('API_HASH')

        self._validate_config()
    
    def _get_env_int(self, key: str) -> Optional[int]:
        """Get integer value from environment variable."""
        value = os.getenv(key)
        if value:
            try:
                return int(value)
            except ValueError:
                logger.error(f"Invalid integer value for {key}: {value}")
                return None
        return None
    
    def _validate_config(self) -> None:
        """Validate that all required configuration is present."""
        missing_vars = []
        
        if not self.api_id:
            missing_vars.append('API_ID')
        if not self.api_hash:
            missing_vars.append('API_HASH')

        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    @property
    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        return all([
            self.api_id,
            self.api_hash
        ])


# Global configuration instance
config = Config()