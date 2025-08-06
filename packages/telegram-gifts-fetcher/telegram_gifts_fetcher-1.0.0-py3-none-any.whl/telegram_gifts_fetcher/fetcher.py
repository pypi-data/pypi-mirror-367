import asyncio
from typing import Optional, Dict
from telethon import TelegramClient
from telethon.tl.types import InputUser
from telegram_gift_fetcher.tl_objects import GetUserStarGifts
from loguru import logger


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
                "raw_data": str(gift)[:500],  # First 500 chars of raw data
            })
            
            # Try to extract common fields from unknown types
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