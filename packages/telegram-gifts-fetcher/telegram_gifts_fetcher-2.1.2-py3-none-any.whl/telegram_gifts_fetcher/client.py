"""Telegram client module for telegram-gifts-fetcher."""

from typing import Optional
from telethon import TelegramClient, types
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from colorama import Fore, Style, init

from .models import Gift, GiftsResponse
from .config import get_config

init(autoreset=True)

""" --- CLIENT --- """

class TelegramGiftsClient:
    """Async Telegram client for fetching gifts."""
    
    def __init__(self, api_id: Optional[int] = None, api_hash: Optional[str] = None, session_name: Optional[str] = None):
        """Initialize the Telegram client."""
        self.client: Optional[TelegramClient] = None
        self._is_connected = False
        self.config = get_config(api_id=api_id, api_hash=api_hash, session_name=session_name)
    
    async def connect(self) -> bool:
        """Connect to Telegram and authenticate."""
        try:
            # Use session file from config
            self.client = TelegramClient(
                self.config.session_name,
                self.config.api_id,
                self.config.api_hash
            )
            
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                print(f"{Fore.YELLOW}🔐 Session is not authorized. Starting authentication process...{Style.RESET_ALL}")
                await self._authenticate()
            
            self._is_connected = True
            print(f"{Fore.GREEN}✅ Successfully connected to Telegram{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to connect to Telegram: {e}{Style.RESET_ALL}")
            return False
    
    async def _authenticate(self) -> None:
        """Handle Telegram authentication process."""
        try:
            phone_number = input("Enter your phone number: ")
            await self.client.send_code_request(phone_number)
            print(f"{Fore.GREEN}📱 Code sent to {phone_number}{Style.RESET_ALL}")
            
            code = input("Enter the code you received: ")
            
            try:
                await self.client.sign_in(phone_number, code)
            except SessionPasswordNeededError:
                password = input("Two-factor authentication enabled. Enter your password: ")
                await self.client.sign_in(password=password)
            
            print(f"{Fore.GREEN}✅ Successfully authenticated{Style.RESET_ALL}")
            
        except KeyboardInterrupt:
            print(f"{Fore.RED}❌ Authentication cancelled by user{Style.RESET_ALL}")
            raise
        except PhoneCodeInvalidError:
            print(f"{Fore.RED}❌ Invalid phone code entered{Style.RESET_ALL}")
            raise
        except Exception as e:
            print(f"{Fore.RED}❌ Authentication failed: {e}{Style.RESET_ALL}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from Telegram."""
        if self.client and self._is_connected:
            await self.client.disconnect()
            self._is_connected = False
            print(f"{Fore.YELLOW}🔌 Disconnected from Telegram{Style.RESET_ALL}")
    
    async def get_user_gifts(self, username: str, limit: int = 100) -> GiftsResponse:
        """Fetch gifts received by a specific user using getUserStarGifts API."""
        if not self._is_connected or not self.client:
            raise RuntimeError("Client is not connected. Call connect() first.")
        
        try:
            # Remove @ symbol if present
            clean_username = username.lstrip('@')
            print(f"{Fore.CYAN}🎁 Fetching gifts for user: {clean_username}{Style.RESET_ALL}")
            
            # Determine the user input
            if clean_username.lower() in ['me', 'self']:
                user_input = types.InputUserSelf()
                print(f"{Fore.CYAN}👤 Fetching gifts for current user{Style.RESET_ALL}")
            else:
                # Get the user entity and create InputUser
                user = await self.client.get_entity(clean_username)
                user_input = types.InputUser(user_id=user.id, access_hash=user.access_hash)
                print(f"{Fore.CYAN}👤 Fetching gifts for user ID: {user.id}{Style.RESET_ALL}")
            
            # Try to use getUserStarGifts through custom TL object with pagination
            try:
                from .tl_objects import GetUserStarGifts
                
                all_gifts = []
                offset = ""
                batch_limit = min(limit, 100)  # API limit per request
                total_fetched = 0
                
                while total_fetched < limit:
                    # Create the request object
                    request = GetUserStarGifts(
                        user_id=user_input,
                        offset=offset,
                        limit=batch_limit
                    )
                    
                    # Send request
                    result = await self.client(request)
                    
                    # Parse result if successful
                    if hasattr(result, 'gifts') and result.gifts:
                        for user_gift in result.gifts:
                            if total_fetched >= limit:
                                break
                                
                            # Extract gift name and slug
                            gift_name = ""
                            gift_slug = ""
                            if hasattr(user_gift, 'gift') and user_gift.gift:
                                gift_name = getattr(user_gift.gift, 'title', "")
                                gift_slug = getattr(user_gift.gift, 'slug', "")
                            
                            # Extract message text properly
                            gift_message = None
                            if hasattr(user_gift, 'message') and user_gift.message:
                                if hasattr(user_gift.message, 'text'):
                                    gift_message = user_gift.message.text
                                elif isinstance(user_gift.message, str):
                                    gift_message = user_gift.message
                                else:
                                    gift_message = str(user_gift.message)
                            
                            gift = Gift(
                                received_date=int(getattr(user_gift, 'date', 0).timestamp()) if getattr(user_gift, 'date', None) else 0,
                                message=gift_message,
                                name_hidden=getattr(user_gift, 'name_hidden', True),
                                can_upgrade=getattr(user_gift, 'can_upgrade', False),
                                pinned_to_top=getattr(user_gift, 'pinned', False),
                                type="star_gift",
                                transfer_stars=getattr(user_gift, 'transfer_stars', 0),
                                user_convert_stars=getattr(user_gift, 'convert_stars', 0),
                                name=gift_name,
                                slug=gift_slug
                            )
                            all_gifts.append(gift)
                            total_fetched += 1
                        
                        # Check if we have more data to fetch
                        if hasattr(result, 'next_offset') and result.next_offset:
                            offset = result.next_offset
                            print(f"{Fore.CYAN}📦 Fetched {total_fetched} gifts, continuing with offset: {offset}{Style.RESET_ALL}")
                        else:
                            # No more data available
                            print(f"{Fore.GREEN}✅ No more gifts available, total fetched: {total_fetched}{Style.RESET_ALL}")
                            break
                    else:
                        # No gifts in this batch
                        print(f"{Fore.GREEN}✅ No more gifts found, total fetched: {total_fetched}{Style.RESET_ALL}")
                        break
                
                gifts = all_gifts
                
                if not gifts:
                    print(f"{Fore.YELLOW}⚠️ getUserStarGifts returned no gifts{Style.RESET_ALL}")
                    
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️ getUserStarGifts failed: {e}, falling back to message search{Style.RESET_ALL}")
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
                        print(f"{Fore.YELLOW}⚠️ Could not access dialog with {clean_username}: {dialog_error}{Style.RESET_ALL}")
                    
                    # Also search in saved messages for gifts from this user
                    async for message in self.client.iter_messages('me', limit=limit):
                        if (self._is_gift_message(message) and 
                            message.from_id and 
                            hasattr(message.from_id, 'user_id') and
                            message.from_id.user_id == target_user.id):
                            gift = self._extract_gift_from_message(message)
                            if gift:
                                gifts.append(gift)
            
            print(f"{Fore.GREEN}🎁 Found {len(gifts)} gifts for user {clean_username}{Style.RESET_ALL}")
            
            # Create response
            response = GiftsResponse(
                gifts=gifts,
                count_gifts=len(gifts)
            )
            
            return response
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error fetching gifts for {clean_username}: {e}{Style.RESET_ALL}")
            raise
    
    async def get_all_gifts(self, username: str) -> GiftsResponse:
        """Fetch ALL gifts received by a specific user without any limit."""
        if not self._is_connected or not self.client:
            raise RuntimeError("Client is not connected. Call connect() first.")
        
        try:
            # Remove @ symbol if present
            clean_username = username.lstrip('@')
            print(f"{Fore.CYAN}🎁 Fetching ALL gifts for user: {clean_username}{Style.RESET_ALL}")
            
            # Determine the user input
            if clean_username.lower() in ['me', 'self']:
                user_input = types.InputUserSelf()
                print(f"{Fore.CYAN}👤 Fetching all gifts for current user{Style.RESET_ALL}")
            else:
                # Get the user entity and create InputUser
                user = await self.client.get_entity(clean_username)
                user_input = types.InputUser(user_id=user.id, access_hash=user.access_hash)
                print(f"{Fore.CYAN}👤 Fetching all gifts for user ID: {user.id}{Style.RESET_ALL}")
            
            # Try to use getUserStarGifts through custom TL object with full pagination
            try:
                from .tl_objects import GetUserStarGifts
                
                all_gifts = []
                offset = ""
                batch_limit = 100  # API limit per request
                total_fetched = 0
                
                while True:
                    # Create the request object
                    request = GetUserStarGifts(
                        user_id=user_input,
                        offset=offset,
                        limit=batch_limit
                    )
                    
                    # Send request
                    result = await self.client(request)
                    
                    # Parse result if successful
                    if hasattr(result, 'gifts') and result.gifts:
                        for user_gift in result.gifts:
                            # Extract gift name and slug
                            gift_name = ""
                            gift_slug = ""
                            if hasattr(user_gift, 'gift') and user_gift.gift:
                                gift_name = getattr(user_gift.gift, 'title', "")
                                gift_slug = getattr(user_gift.gift, 'slug', "")
                            
                            # Extract message text properly
                            gift_message = None
                            if hasattr(user_gift, 'message') and user_gift.message:
                                if hasattr(user_gift.message, 'text'):
                                    gift_message = user_gift.message.text
                                elif isinstance(user_gift.message, str):
                                    gift_message = user_gift.message
                                else:
                                    gift_message = str(user_gift.message)
                            
                            gift = Gift(
                                received_date=int(getattr(user_gift, 'date', 0).timestamp()) if getattr(user_gift, 'date', None) else 0,
                                message=gift_message,
                                name_hidden=getattr(user_gift, 'name_hidden', True),
                                can_upgrade=getattr(user_gift, 'can_upgrade', False),
                                pinned_to_top=getattr(user_gift, 'pinned', False),
                                type="star_gift",
                                transfer_stars=getattr(user_gift, 'transfer_stars', 0),
                                user_convert_stars=getattr(user_gift, 'convert_stars', 0),
                                name=gift_name,
                                slug=gift_slug
                            )
                            all_gifts.append(gift)
                            total_fetched += 1
                        
                        # Check if we have more data to fetch
                        if hasattr(result, 'next_offset') and result.next_offset:
                            offset = result.next_offset
                            print(f"{Fore.CYAN}📦 Fetched {total_fetched} gifts, continuing with offset: {offset}{Style.RESET_ALL}")
                        else:
                            # No more data available
                            print(f"{Fore.GREEN}✅ No more gifts available, total fetched: {total_fetched}{Style.RESET_ALL}")
                            break
                    else:
                        # No gifts in this batch
                        print(f"{Fore.GREEN}✅ No more gifts found, total fetched: {total_fetched}{Style.RESET_ALL}")
                        break
                
                gifts = all_gifts
                
                if not gifts:
                    print(f"{Fore.YELLOW}⚠️ getUserStarGifts returned no gifts{Style.RESET_ALL}")
                    
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️ getUserStarGifts failed: {e}, falling back to message search{Style.RESET_ALL}")
                gifts = []
                
                # Fallback: search for gift messages without limit
                if clean_username.lower() in ['me', 'self']:
                    # Search in saved messages for current user
                    async for message in self.client.iter_messages('me'):
                        if self._is_gift_message(message):
                            gift = self._extract_gift_from_message(message)
                            if gift:
                                gifts.append(gift)
                else:
                    # Search in all dialogs for gifts to/from the target user
                    target_user = await self.client.get_entity(clean_username)
                    
                    # Search in dialog with the target user
                    try:
                        async for message in self.client.iter_messages(target_user):
                            if self._is_gift_message(message):
                                gift = self._extract_gift_from_message(message)
                                if gift:
                                    gifts.append(gift)
                    except Exception as dialog_error:
                        print(f"{Fore.YELLOW}⚠️ Could not access dialog with {clean_username}: {dialog_error}{Style.RESET_ALL}")
                    
                    # Also search in saved messages for gifts from this user
                    async for message in self.client.iter_messages('me'):
                        if (self._is_gift_message(message) and 
                            message.from_id and 
                            hasattr(message.from_id, 'user_id') and
                            message.from_id.user_id == target_user.id):
                            gift = self._extract_gift_from_message(message)
                            if gift:
                                gifts.append(gift)
            
            print(f"{Fore.GREEN}🎁 Found {len(gifts)} total gifts for user {clean_username}{Style.RESET_ALL}")
            
            # Create response
            response = GiftsResponse(
                gifts=gifts,
                count_gifts=len(gifts)
            )
            
            return response
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error fetching all gifts for {clean_username}: {e}{Style.RESET_ALL}")
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
            
            # Extract stars from different action types
            stars = 0
            if hasattr(action, 'stars'):
                stars = action.stars
            elif hasattr(action, 'gift'):
                gift_obj = action.gift
                if hasattr(gift_obj, 'stars'):
                    stars = gift_obj.stars
                elif hasattr(gift_obj, 'star_count'):
                    stars = gift_obj.star_count
            elif hasattr(action, 'star_count'):
                stars = action.star_count
            
            # Extract message text
            gift_message = None
            if hasattr(action, 'message'):
                if hasattr(action.message, 'text'):
                    gift_message = action.message.text
                elif isinstance(action.message, str):
                    gift_message = action.message
            
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
            print(f"{Fore.YELLOW}⚠️ Failed to extract gift from message {message.id}: {e}{Style.RESET_ALL}")
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