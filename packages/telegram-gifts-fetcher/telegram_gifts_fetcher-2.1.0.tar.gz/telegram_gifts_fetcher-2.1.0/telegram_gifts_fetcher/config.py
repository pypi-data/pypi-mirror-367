"""Configuration module for telegram-gifts-fetcher."""

import os
import sys
from typing import Optional
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


""" --- CONFIG --- """

class Config:
    """Configuration class for the application."""
    
    def __init__(self, api_id: Optional[int] = None, api_hash: Optional[str] = None, session_name: Optional[str] = None):
        """Initialize configuration from parameters, environment variables or user input."""
        # Priority: parameters > environment variables > user input
        self.api_id: Optional[int] = api_id or self._get_env_int('API_ID')
        self.api_hash: Optional[str] = api_hash or os.getenv('API_HASH')
        self.session_name: str = session_name or os.getenv('SESSION_NAME', 'account')
        
        # If credentials are not found, prompt user for them
        if not self.api_id or not self.api_hash:
            self._prompt_for_credentials()
    
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
    
    def _prompt_for_credentials(self) -> None:
        """Prompt user for API credentials if not found in environment."""
        print("\n🔑 Telegram API credentials not found in environment variables.")
        print("Please obtain your API credentials from https://my.telegram.org/apps")
        print("")
        
        try:
            if not self.api_id:
                while True:
                    try:
                        api_id_input = input("Enter your API ID: ").strip()
                        self.api_id = int(api_id_input)
                        break
                    except ValueError:
                        print("❌ Invalid API ID. Please enter a valid number.")
                    except KeyboardInterrupt:
                        print("\n❌ Setup cancelled by user.")
                        raise
            
            if not self.api_hash:
                while True:
                    try:
                        api_hash_input = input("Enter your API Hash: ").strip()
                        if api_hash_input:
                            self.api_hash = api_hash_input
                            break
                        else:
                            print("❌ API Hash cannot be empty.")
                    except KeyboardInterrupt:
                        print("\n❌ Setup cancelled by user.")
                        raise
            
            print("✅ API credentials configured successfully!")
            print("")
        except KeyboardInterrupt:
            print("\n❌ Configuration cancelled.")
            sys.exit(1)
    
    def _validate_config(self) -> None:
        """Validate that all required configuration is present."""
        if not self.api_id or not self.api_hash:
            logger.error("API credentials are required but not provided")
            raise ValueError("API credentials are required but not provided")
    
    @property
    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        return all([
            self.api_id,
            self.api_hash,
            self.session_name
        ])


# Global configuration instance (can be overridden)
config = None

def get_config(api_id: Optional[int] = None, api_hash: Optional[str] = None, session_name: Optional[str] = None) -> Config:
    """Get or create configuration instance."""
    global config
    if config is None or api_id or api_hash or session_name:
        config = Config(api_id=api_id, api_hash=api_hash, session_name=session_name)
    return config