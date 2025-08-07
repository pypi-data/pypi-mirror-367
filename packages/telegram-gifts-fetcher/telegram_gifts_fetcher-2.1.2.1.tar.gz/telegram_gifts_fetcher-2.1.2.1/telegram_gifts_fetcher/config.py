"""Configuration module for telegram-gifts-fetcher."""

import os
from typing import Optional
from colorama import Fore, Style, init
from dotenv import load_dotenv

# Initialize colorama
init(autoreset=True)

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
                print(f"{Fore.RED}❌ Invalid integer value for {key}: {value}{Style.RESET_ALL}")
                return None
        return None
    
    def _prompt_for_credentials(self) -> None:
        """Show message about missing credentials without prompting for input."""
        print(f"\n{Fore.RED}❌ Telegram API credentials not found!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}📋 Please add your API credentials to the .env file or pass them as parameters.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🔗 Get your credentials from: https://my.telegram.org/apps{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Example .env file:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}API_ID=12345678{Style.RESET_ALL}")
        print(f"{Fore.GREEN}API_HASH=abcdef1234567890abcdef1234567890{Style.RESET_ALL}")
        print(f"{Fore.GREEN}SESSION_NAME=account{Style.RESET_ALL}")
        print("")
        raise ValueError("API credentials are required but not provided")
    
    def _validate_config(self) -> None:
        """Validate that all required configuration is present."""
        if not self.api_id or not self.api_hash:
            print(f"{Fore.RED}❌ API credentials are required but not provided{Style.RESET_ALL}")
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