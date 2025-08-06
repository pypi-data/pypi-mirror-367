from telethon import TelegramClient
from telegram_gifts_fetcher import (
    get_user_gifts_extended,
    handle_dependency_errors,
    DependencyError
)
import asyncio
from dotenv import load_dotenv
import os
from loguru import logger
from datetime import datetime

""" --- CONFIG --- """
load_dotenv()

""" --- UTILS --- """
def format_timestamp(timestamp):
    """Convert timestamp to readable date"""
    try:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(timestamp)



""" --- MAIN FUNCTION --- """
async def main():
    """Main function to fetch and display user gifts"""
    
    # Demonstrate dependency error handler
    try:
        logger.info("Running dependency error check...")
        handle_dependency_errors()
    except DependencyError as e:
        logger.error(f"Dependency error detected: {e}")
        print(f"⚠️  Dependency Error: {e}")
        print("Please fix the dependency issues and try again.")
        return
    except Exception as e:
        logger.warning(f"Dependency check failed: {e}")
    
    # Initialize Telegram client
    client = TelegramClient('account', int(os.getenv("API_ID")), os.getenv("API_HASH"))
    await client.start()
    
    try:
        # Get current user info
        me = await client.get_me()
        
        if me.username:
            # Fetch gifts using extended function
            gifts_data = await get_user_gifts_extended(client, me.username)
            
            # Display results
            print(f"\n🎁 Gift Summary for @{me.username}:")
            print(f"Total gifts found: {gifts_data['count_gifts']}")
            
            if gifts_data['gifts']:
                print("\n📋 Gift Details:")
                for i, gift in enumerate(gifts_data['gifts'], 1):
                    print(f"\n{i}. 🎁 Gift #{i}")
                    print(f"   📅 Received: {format_timestamp(gift['received_date'])}")
                    print(f"   👤 From ID: {gift['from_id'] if gift['from_id'] else 'Anonymous'}")
                    print(f"   🏷️  Type: {gift['type']}")
                    print(f"   🔒 Name hidden: {'Yes' if gift['name_hidden'] else 'No'}")
                    print(f"   💾 Saved: {'Yes' if not gift['unsaved'] else 'No'}")
                    print(f"   🔄 Refunded: {'Yes' if gift['refunded'] else 'No'}")
                    print(f"   ⬆️  Can upgrade: {'Yes' if gift['can_upgrade'] else 'No'}")
                    print(f"   📌 Pinned: {'Yes' if gift['pinned_to_top'] else 'No'}")
                    
                    # Show all star-related values
                    star_fields = [k for k in gift.keys() if 'star' in k.lower()]
                    if star_fields:
                        print(f"   ⭐ Star values:")
                        for field in star_fields:
                            print(f"      {field}: {gift[field]}")
                    
                    # Show timing fields
                    time_fields = [k for k in gift.keys() if any(x in k for x in ['_at', 'date'])]
                    if time_fields:
                        print(f"   ⏰ Timing info:")
                        for field in time_fields:
                            if field != 'received_date':  # Already shown
                                value = gift[field]
                                if isinstance(value, (int, float)) and len(str(value)) > 9:  # Timestamp
                                    value = format_timestamp(value)
                                print(f"      {field}: {value}")
                    
                    # Show gift-specific attributes
                    gift_attrs = [k for k in gift.keys() if k.startswith('gift_')]
                    if gift_attrs:
                        print(f"   🎁 Gift attributes:")
                        for attr in gift_attrs:
                            value = gift[attr]
                            # Clean up sticker display
                            if attr == 'gift_sticker' and hasattr(value, 'id'):
                                value = f"Sticker ID: {value.id}"
                            elif isinstance(value, str) and len(value) > 50:
                                value = value[:50] + "..."
                            elif str(value).startswith('Document('):
                                value = "Document object"
                            print(f"      {attr}: {value}")
                    

            else:
                print("\n❌ No gifts found")
                
        else:
            logger.warning("Current user has no username set")
            print("❌ You don't have a username set in Telegram")
            
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        print(f"❌ Error: {e}")
    
    finally:
        await client.disconnect()

""" --- STARTUP --- """
if __name__ == "__main__":
    asyncio.run(main())