from typing import Optional, Dict, List
from telethon import TelegramClient
from telethon.tl.types import InputUser
from telethon.tl import TLObject, TLRequest
from telethon.tl.types import TypeStarGift, TypeInputUser, TypeUser, TypeTextWithEntities
from loguru import logger
import struct
import subprocess
import sys
import os


""" --- DEPENDENCY ERROR HANDLER --- """

class DependencyError(Exception):
    """Custom exception for dependency-related errors."""
    pass


def check_circular_dependencies(package_name: str = "telegram-gifts-fetcher") -> bool:
    """
    Check for circular dependencies in package configuration files.
    
    Args:
        package_name: Name of the package to check for circular dependencies
        
    Returns:
        bool: True if circular dependencies found, False otherwise
    """
    try:
        current_dir = os.getcwd()
        config_files = [
            os.path.join(current_dir, "setup.py"),
            os.path.join(current_dir, "pyproject.toml"),
            os.path.join(current_dir, "requirements.txt")
        ]
        
        circular_deps_found = False
        
        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for self-dependency patterns
                if package_name in content and any(dep_indicator in content for dep_indicator in 
                    ["install_requires", "dependencies", "==" , ">="]):
                    
                    # More specific check to avoid false positives
                    lines = content.split('\n')
                    for line in lines:
                        line = line.strip()
                        if (package_name in line and 
                            any(indicator in line for indicator in ["==", ">=", "~="]) and
                            not line.startswith('#') and
                            not line.startswith('name')):
                            
                            logger.error(f"Circular dependency detected in {config_file}: {line}")
                            circular_deps_found = True
                            
        return circular_deps_found
        
    except Exception as e:
        logger.warning(f"Error checking circular dependencies: {e}")
        return False


def fix_circular_dependencies(package_name: str = "telegram-gifts-fetcher") -> bool:
    """
    Automatically fix circular dependencies in package configuration files.
    
    Args:
        package_name: Name of the package to remove from dependencies
        
    Returns:
        bool: True if fixes were applied, False otherwise
    """
    try:
        current_dir = os.getcwd()
        config_files = [
            os.path.join(current_dir, "setup.py"),
            os.path.join(current_dir, "pyproject.toml"),
            os.path.join(current_dir, "requirements.txt")
        ]
        
        fixes_applied = False
        
        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                new_lines = []
                for line in lines:
                    # Skip lines that contain circular dependencies
                    if (package_name in line and 
                        any(indicator in line for indicator in ["==", ">=", "~="]) and
                        not line.strip().startswith('#') and
                        not line.strip().startswith('name')):
                        
                        logger.info(f"Removing circular dependency from {config_file}: {line.strip()}")
                        fixes_applied = True
                        continue
                        
                    new_lines.append(line)
                    
                if fixes_applied:
                    with open(config_file, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
                        
        return fixes_applied
        
    except Exception as e:
        logger.error(f"Error fixing circular dependencies: {e}")
        return False


def handle_dependency_errors():
    """
    Main handler for dependency-related errors.
    Checks for and fixes circular dependencies automatically.
    """
    try:
        package_name = "telegram-gifts-fetcher"
        
        logger.info("Checking for circular dependencies...")
        
        if check_circular_dependencies(package_name):
            logger.warning("Circular dependencies detected! Attempting to fix...")
            
            if fix_circular_dependencies(package_name):
                logger.success("Circular dependencies fixed successfully!")
                logger.info("You can now try installing the package again with: pip install .")
            else:
                logger.error("Failed to automatically fix circular dependencies")
                raise DependencyError(
                    f"Circular dependency detected for package '{package_name}'. "
                    "Please manually remove self-references from setup.py, pyproject.toml, and requirements.txt"
                )
        else:
            logger.info("No circular dependencies detected.")
            
    except Exception as e:
        logger.error(f"Dependency error handler failed: {e}")
        raise DependencyError(f"Failed to handle dependency errors: {e}")


""" --- TELEGRAM GIFT CLASSES --- """


class UserStarGift(TLObject):
    """Represents a single gift received by a user."""
    CONSTRUCTOR_ID = 0xeea49a6e
    SUBCLASS_OF_ID = None

    def __init__(self, gift: 'TypeStarGift', date: int, name_hidden: Optional[bool] = None,
                 unsaved: Optional[bool] = None, from_id: Optional[int] = None,
                 message: Optional['TypeTextWithEntities'] = None, msg_id: Optional[int] = None,
                 convert_stars: Optional[int] = None):
        self.gift = gift
        self.date = date
        self.name_hidden = name_hidden
        self.unsaved = unsaved
        self.from_id = from_id
        self.message = message
        self.msg_id = msg_id
        self.convert_stars = convert_stars

    def to_dict(self):
        return {
            '_': 'UserStarGift',
            'gift': self.gift.to_dict() if isinstance(self.gift, TLObject) else self.gift,
            'date': self.date,
            'name_hidden': self.name_hidden,
            'unsaved': self.unsaved,
            'from_id': self.from_id,
            'message': self.message.to_dict() if isinstance(self.message, TLObject) else self.message,
            'msg_id': self.msg_id,
            'convert_stars': self.convert_stars
        }

    def _bytes(self):
        flags = 0
        if self.name_hidden:
            flags |= 1
        if self.from_id is not None:
            flags |= 2
        if self.message is not None:
            flags |= 4
        if self.msg_id is not None:
            flags |= 8
        if self.convert_stars is not None:
            flags |= 16
        if self.unsaved:
            flags |= 32
        return b''.join((
            b'\x6e\x9a\xa4\xee',
            struct.pack('<I', flags),
            struct.pack('<q', self.from_id) if self.from_id is not None else b'',
            struct.pack('<i', self.date),
            self.gift._bytes(),
            self.message._bytes() if self.message is not None else b'',
            struct.pack('<i', self.msg_id) if self.msg_id is not None else b'',
            struct.pack('<q', self.convert_stars) if self.convert_stars is not None else b'',
        ))

    @classmethod
    def from_reader(cls, reader):
        flags = reader.read_int()
        name_hidden = bool(flags & 1)
        from_id = reader.read_long() if flags & 2 else None
        date = reader.read_int()
        gift = reader.tgread_object()
        message = reader.tgread_object() if flags & 4 else None
        msg_id = reader.read_int() if flags & 8 else None
        convert_stars = reader.read_long() if flags & 16 else None
        unsaved = bool(flags & 32)
        return cls(gift=gift, date=date, name_hidden=name_hidden, unsaved=unsaved,
                   from_id=from_id, message=message, msg_id=msg_id, convert_stars=convert_stars)


class UserStarGifts(TLObject):
    """Represents a collection of user gifts."""
    CONSTRUCTOR_ID = 0x6b65b517
    SUBCLASS_OF_ID = None

    def __init__(self, count: int, gifts: List['UserStarGift'], users: List['TypeUser'],
                 next_offset: Optional[str] = None):
        self.count = count
        self.gifts = gifts
        self.next_offset = next_offset
        self.users = users

    def to_dict(self):
        return {
            '_': 'UserStarGifts',
            'count': self.count,
            'gifts': [x.to_dict() if isinstance(x, TLObject) else x for x in self.gifts],
            'next_offset': self.next_offset,
            'users': [x.to_dict() if isinstance(x, TLObject) else x for x in self.users]
        }

    def _bytes(self):
        flags = 0 if self.next_offset is None else 1
        return b''.join((
            b'\x17\xb5\x65\x6b',
            struct.pack('<I', flags),
            struct.pack('<i', self.count),
            b'\x15\xc4\xb5\x1c', struct.pack('<i', len(self.gifts)),
            b''.join(x._bytes() for x in self.gifts),
            self.serialize_bytes(self.next_offset.encode('utf-8')) if self.next_offset else b'',
            b'\x15\xc4\xb5\x1c', struct.pack('<i', len(self.users)),
            b''.join(x._bytes() for x in self.users),
        ))

    @classmethod
    def from_reader(cls, reader):
        flags = reader.read_int()
        count = reader.read_int()
        reader.read_int()  # Vector header
        gifts = [reader.tgread_object() for _ in range(reader.read_int())]
        next_offset = reader.tgread_string() if flags & 1 else None
        reader.read_int()  # Vector header
        users = [reader.tgread_object() for _ in range(reader.read_int())]
        return cls(count=count, gifts=gifts, next_offset=next_offset, users=users)


class GetUserStarGifts(TLRequest):
    """Request to fetch user gifts."""
    CONSTRUCTOR_ID = 0x5e72c7e1
    SUBCLASS_OF_ID = 0x6b65b517

    def __init__(self, user_id: 'TypeInputUser', offset: str, limit: int):
        self.user_id = user_id
        self.offset = offset
        self.limit = limit

    def to_dict(self):
        return {
            '_': 'GetUserStarGifts',
            'user_id': self.user_id.to_dict() if isinstance(self.user_id, TLObject) else self.user_id,
            'offset': self.offset,
            'limit': self.limit
        }

    def _bytes(self):
        return b''.join((
            b'\xe1\xc7\x72\x5e',
            self.user_id._bytes(),
            self.serialize_bytes(self.offset.encode('utf-8')),
            struct.pack('<i', self.limit),
        ))

    @classmethod
    def from_reader(cls, reader):
        user_id = reader.tgread_object()
        offset = reader.tgread_string()
        limit = reader.read_int()
        return cls(user_id=user_id, offset=offset, limit=limit)

async def _resolve_username(client: TelegramClient, username: str) -> Optional[tuple]:
    """
    Resolve a Telegram username to user ID and access hash.
    """
    from telethon.tl.functions import contacts
    response = await client(contacts.ResolveUsernameRequest(username=username))
    if not response.users:
        logger.warning(f"No user found for username '{username}'")
        return None
    user = response.users[0]
    return user.id, user.access_hash


async def get_user_gifts_extended(client: TelegramClient, username: str, offset: str = "", limit: int = 100) -> Dict:
    """
    Extended version that processes ALL gift types including StarGiftRegular.
    """
    user_data = await _resolve_username(client, username)
    if user_data is None:
        return {'gifts': [], 'count_gifts': 0}
    
    user_id, access_hash = user_data
    user = InputUser(user_id=user_id, access_hash=access_hash)
    request = GetUserStarGifts(user_id=user, offset=offset, limit=limit)
    response = await client(request)

    filtered_gifts = []



    for user_gift in response.gifts:
        gift = user_gift.gift
        received_date = int(user_gift.date.timestamp())
        
        # Get common gift info
        gift_data = {
            "received_date": received_date,
            "constructor_id": hex(gift.CONSTRUCTOR_ID),
            "from_id": user_gift.from_id.user_id if user_gift.from_id else None,
            "message": user_gift.message,
            "msg_id": user_gift.msg_id,
            "saved_id": user_gift.saved_id,
            "name_hidden": user_gift.name_hidden,
            "unsaved": user_gift.unsaved,
            "refunded": user_gift.refunded,
            "can_upgrade": user_gift.can_upgrade,
            "pinned_to_top": user_gift.pinned_to_top
        }
        
        if gift.CONSTRUCTOR_ID == 0x2cc73c8:  # StarGift
            gift_data.update({
                "type": "StarGift",
                "id": gift.id,
                "stars": gift.stars,
                "convert_stars": gift.convert_stars,
            })
            pass
            
        elif gift.CONSTRUCTOR_ID == 0x5c62d151:  # StarGiftUnique
            gift_data.update({
                "type": "StarGiftUnique",
                "id": gift.id,
                "title": gift.title,
                "slug": gift.slug,
                "num": gift.num,
                "availability_issued": gift.availability_issued,
                "availability_total": gift.availability_total,
            })
            
        elif gift.CONSTRUCTOR_ID == 0x736b72c7:  # StarGiftRegular
            gift_data.update({
                "type": "StarGiftRegular",
                "id": getattr(gift, 'id', None),
                "sticker": str(getattr(gift, 'sticker', None)),
                "stars": getattr(gift, 'stars', 0),
                "convert_stars": getattr(gift, 'convert_stars', 0),
                "first_sale_date": getattr(gift, 'first_sale_date', None),
                "last_sale_date": getattr(gift, 'last_sale_date', None),
            })
            pass
                
        else:
            # Handle unknown gift types - extract as much info as possible
            gift_data.update({
                "type": "Unknown",
                "raw_data": str(gift)[:500],
            })
            
            for attr in ['id', 'stars', 'convert_stars', 'sticker', 'title', 'slug']:
                if hasattr(gift, attr):
                    gift_data[f'gift_{attr}'] = getattr(gift, attr)
                    
            pass
                

        
        # Add additional fields if they exist in user_gift
        additional_fields = [
            'convert_stars', 'upgrade_stars', 'transfer_stars', 
            'can_export_at', 'can_transfer_at', 'can_resell_at',
            'first_sale_date', 'last_sale_date', 'availability_issued',
            'availability_total', 'price', 'original_price'
        ]
        
        for field in additional_fields:
            if hasattr(user_gift, field):
                value = getattr(user_gift, field)
                if value is not None:
                    gift_data[f'user_{field}'] = value
                    
                    pass
            
        filtered_gifts.append(gift_data)


    
    return {
        "gifts": filtered_gifts,
        "count_gifts": len(filtered_gifts)
    }