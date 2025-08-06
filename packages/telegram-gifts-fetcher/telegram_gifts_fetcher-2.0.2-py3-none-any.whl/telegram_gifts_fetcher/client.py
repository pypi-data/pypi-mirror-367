"""Telegram client module for telegram-gifts-fetcher."""

from typing import Optional, List
from telethon import TelegramClient, functions, types
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from colorama import Fore, Style, init

from .models import Gift, GiftsResponse
from .config import config

# Initialize colorama
init(autoreset=True)

def log_info(message: str):
    print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} {message}")

def log_warning(message: str):
    print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {message}")

def log_error(message: str):
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}")

def log_debug(message: str):
    print(f"{Fore.CYAN}[DEBUG]{Style.RESET_ALL} {message}")

""" --- CLIENT --- """

class TelegramGiftsClient:
    """Async Telegram client for fetching gifts."""
    
    def __init__(self):
        """Initialize the Telegram client."""
        self.client: Optional[TelegramClient] = None
        self._is_connected = False
    
    async def connect(self) -> bool:
        """Connect to Telegram and authenticate."""
        try:
            # Use existing session file 'account'
            self.client = TelegramClient(
                'account',
                config.api_id,
                config.api_hash
            )
            
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                log_error("Session is not authorized. Please run the original authentication first.")
                return False
            
            self._is_connected = True
            log_info("Successfully connected to Telegram using existing session")
            return True
            
        except Exception as e:
            log_error(f"Failed to connect to Telegram: {e}")
            return False
    
    async def _authenticate(self) -> None:
        """Handle Telegram authentication process."""
        try:
            phone_number = input("Enter your phone number: ")
            await self.client.send_code_request(phone_number)
            log_info(f"Code sent to {phone_number}")
            
            code = input("Enter the code you received: ")
            
            try:
                await self.client.sign_in(phone_number, code)
            except SessionPasswordNeededError:
                password = input("Two-factor authentication enabled. Enter your password: ")
                await self.client.sign_in(password=password)
            
            log_info("Successfully authenticated")
            
        except PhoneCodeInvalidError:
            log_error("Invalid phone code entered")
            raise
        except Exception as e:
            log_error(f"Authentication failed: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from Telegram."""
        if self.client and self._is_connected:
            await self.client.disconnect()
            self._is_connected = False
            log_info("Disconnected from Telegram")
    
    async def get_user_gifts(self, username: str, limit: int = 100) -> GiftsResponse:
        """Fetch gifts received by a specific user using getUserStarGifts API."""
        if not self._is_connected or not self.client:
            raise RuntimeError("Client is not connected. Call connect() first.")
        
        try:
            # Remove @ symbol if present
            clean_username = username.lstrip('@')
            log_info(f"Fetching gifts for user: {clean_username}")
            
            # Determine the user input
            if clean_username.lower() in ['me', 'self']:
                user_input = types.InputUserSelf()
                log_info("Fetching gifts for current user")
            else:
                # Get the user entity and create InputUser
                user = await self.client.get_entity(clean_username)
                user_input = types.InputUser(user_id=user.id, access_hash=user.access_hash)
                log_info(f"Fetching gifts for user ID: {user.id}")
            
            # Try to use getUserStarGifts through custom TL object
            try:
                from .tl_objects import GetUserStarGifts
                
                # Create the request object
                request = GetUserStarGifts(
                    user_id=user_input,
                    offset="",
                    limit=limit
                )
                
                # Send request
                result = await self.client(request)
                
                gifts = []
                # Parse result if successful
                if hasattr(result, 'gifts'):
                    for user_gift in result.gifts:
                        # Extract gift name and slug
                        gift_name = ""
                        gift_slug = ""
                        if hasattr(user_gift, 'gift') and user_gift.gift:
                            gift_name = getattr(user_gift.gift, 'title', "")
                            gift_slug = getattr(user_gift.gift, 'slug', "")
                        
                        gift = Gift(
                            received_date=int(getattr(user_gift, 'date', 0).timestamp()) if getattr(user_gift, 'date', None) else 0,
                            message=getattr(user_gift, 'message', None),
                            name_hidden=getattr(user_gift, 'name_hidden', True),
                            can_upgrade=getattr(user_gift, 'can_upgrade', False),
                            pinned_to_top=getattr(user_gift, 'pinned', False),
                            type="star_gift",
                            transfer_stars=getattr(user_gift, 'transfer_stars', 0),
                            user_convert_stars=getattr(user_gift, 'convert_stars', 0),
                            name=gift_name,
                            slug=gift_slug
                        )
                        gifts.append(gift)
                else:
                    log_warning("getUserStarGifts returned unexpected result format")
                    gifts = []
                    
            except Exception as e:
                log_warning(f"getUserStarGifts failed: {e}, falling back to message search")
                gifts = []
                
                # Fallback: search for gift messages
                if clean_username.lower() in ['me', 'self']:
                    # Search in saved messages for current user
                    async for message in self.client.iter_messages('me', limit=limit):
                        if self._is_gift_message(message):
                            gift = self._extract_gift_from_message(message)
                            if gift:
                                gifts.append(gift)
                else:
                    # Search in all dialogs for gifts to/from the target user
                    target_user = await self.client.get_entity(clean_username)
                    
                    # Search in dialog with the target user
                    try:
                        async for message in self.client.iter_messages(target_user, limit=limit):
                            if self._is_gift_message(message):
                                gift = self._extract_gift_from_message(message)
                                if gift:
                                    gifts.append(gift)
                    except Exception as dialog_error:
                        log_warning(f"Could not access dialog with {clean_username}: {dialog_error}")
                    
                    # Also search in saved messages for gifts from this user
                    async for message in self.client.iter_messages('me', limit=limit):
                        if (self._is_gift_message(message) and 
                            message.from_id and 
                            hasattr(message.from_id, 'user_id') and
                            message.from_id.user_id == target_user.id):
                            gift = self._extract_gift_from_message(message)
                            if gift:
                                gifts.append(gift)
            
            log_info(f"Found {len(gifts)} gifts for user {clean_username}")
            
            # Create response
            response = GiftsResponse(
                gifts=gifts,
                count_gifts=len(gifts)
            )
            
            return response
            
        except Exception as e:
            log_error(f"Error fetching gifts for {clean_username}: {e}")
            raise
    
    def _is_gift_message(self, message) -> bool:
        """Check if message contains a gift."""
        if not hasattr(message, 'action'):
            return False
        
        action_class_name = message.action.__class__.__name__.lower()
        return ('gift' in action_class_name or 
                'stargift' in action_class_name or
                'messagegift' in action_class_name)
    
    def _extract_gift_from_message(self, message) -> Optional[Gift]:
        """Extract gift data from a message."""
        try:
            action = message.action
            action_class_name = action.__class__.__name__
            
            # Debug: log action details
            log_debug(f"Processing gift message {message.id}, action type: {action_class_name}")
            log_debug(f"Action attributes: {[attr for attr in dir(action) if not attr.startswith('_')]}")
            
            # Extract stars from different action types
            stars = 0
            if hasattr(action, 'stars'):
                stars = action.stars
                log_debug(f"Found stars in action.stars: {stars}")
            elif hasattr(action, 'gift'):
                gift_obj = action.gift
                log_debug(f"Found gift object: {gift_obj.__class__.__name__}")
                if hasattr(gift_obj, 'stars'):
                    stars = gift_obj.stars
                    log_debug(f"Found stars in action.gift.stars: {stars}")
                elif hasattr(gift_obj, 'star_count'):
                    stars = gift_obj.star_count
                    log_debug(f"Found stars in action.gift.star_count: {stars}")
            elif hasattr(action, 'star_count'):
                stars = action.star_count
                log_debug(f"Found stars in action.star_count: {stars}")
            
            # Extract message text
            gift_message = None
            if hasattr(action, 'message'):
                if hasattr(action.message, 'text'):
                    gift_message = action.message.text
                elif isinstance(action.message, str):
                    gift_message = action.message
                log_debug(f"Found gift message: {gift_message}")
            
            # Extract sender ID
            sender_id = None
            if message.from_id:
                if hasattr(message.from_id, 'user_id'):
                    sender_id = message.from_id.user_id
                elif isinstance(message.from_id, int):
                    sender_id = message.from_id
                else:
                    # Handle PeerUser and other peer types
                    sender_id = getattr(message.from_id, 'user_id', None)
                log_debug(f"Found sender ID: {sender_id} (type: {type(message.from_id)})")
            
            # Extract crypto data if available
            crypto_currency = getattr(action, 'crypto_currency', None)
            crypto_amount = getattr(action, 'crypto_amount', None)
            
            log_debug(f"Extracted gift data: stars={stars}, sender_id={sender_id}, message={gift_message}")
            
            return Gift(
                received_date=int(message.date.timestamp()) if message.date else 0,
                message=gift_message,
                name_hidden=sender_id is None,
                can_upgrade=getattr(action, 'can_upgrade', False),
                pinned_to_top=getattr(message, 'pinned', False),
                type="star_gift",
                transfer_stars=stars,
                user_convert_stars=stars,
                name="",
                slug=""
            )
            
        except Exception as e:
            log_warning(f"Failed to extract gift from message {message.id}: {e}")
            return None
    
    def _determine_gift_type_from_star_gift(self, star_gift) -> str:
        """Determine the type of gift based on the StarGift object."""
        # StarGift objects from getUserStarGifts are always star gifts
        return "star_gift"
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()