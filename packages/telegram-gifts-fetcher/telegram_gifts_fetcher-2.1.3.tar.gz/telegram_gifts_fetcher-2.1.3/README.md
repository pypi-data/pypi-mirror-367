# 🎁 Telegram Gifts Fetcher

[![PyPI version](https://badge.fury.io/py/telegram-gifts-fetcher.svg)](https://badge.fury.io/py/telegram-gifts-fetcher)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/badge/GitHub-Th3ryks-blue)](https://github.com/Th3ryks/TelegramGiftsFetcher)

**A powerful Python library to fetch and analyze Telegram Gifts! 🌟**

This library provides a comprehensive solution for programmatically fetching, analyzing, and managing Telegram Gifts from user profiles using the official Telegram API.

## ✨ Features

- 🎁 **Complete Gift Support** - Handles all Telegram gift types (StarGift, StarGiftUnique, StarGiftRegular)
- 🚀 **Async/Await Ready** - Built with modern Python async patterns
- 🛡️ **Robust Error Handling** - Comprehensive error management and type safety
- 📱 **Developer Friendly** - Simple, intuitive API design
- 💾 **Multiple Export Formats** - JSON, CSV, and custom data exports
- 🔍 **Smart Filtering** - Advanced gift filtering by date, type, value, and more

## 📦 Installation

```bash
pip install telegram-gifts-fetcher
```

## 🚀 Quick Start

### 1. Get Telegram API Credentials

1. Visit [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Navigate to "API Development Tools"
4. Create a new application
5. Save your `API_ID` and `API_HASH`

### 2. Configuration

Create a `.env` file in your project root:
```env
API_ID=your_api_id_here
API_HASH=your_api_hash_here
SESSION_NAME=account
```

## 📖 Usage Examples

### Example 1: Basic Gift Fetching (v2.1.3+)

```python
from telegram_gifts_fetcher import TelegramGiftsClient
import asyncio

async def main():
    # Method 1: Graceful error handling (Recommended)
    client = TelegramGiftsClient(strict=False)
    
    if not await client.connect():
        print("❌ Failed to connect. Please check your .env file.")
        return
    
    try:
        result = await client.get_user_gifts('username', limit=50)
        print(f"📊 Found {result.count_gifts} gifts!")
        
        for gift in result.gifts[:5]:
            print(f"🎁 {gift.name} - {gift.message or 'No message'}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()

asyncio.run(main())
```

### Example 1b: Traditional Error Handling

```python
from telegram_gifts_fetcher import TelegramGiftsClient
import asyncio

async def main():
    try:
        # This will raise ValueError if credentials are missing
        client = TelegramGiftsClient()  # strict=True by default
        
        await client.connect()
        result = await client.get_user_gifts('username', limit=50)
        print(f"📊 Found {result.count_gifts} gifts!")
        
        for gift in result.gifts[:5]:
            print(f"🎁 {gift.name} - {gift.message or 'No message'}")
            
        await client.disconnect()
        
    except ValueError as e:
        if "API credentials are required" in str(e):
            print("❌ Missing API credentials!")
            print("📋 Please create a .env file with your Telegram API credentials.")
            print("🔗 Get them from: https://my.telegram.org/apps")
        else:
            print(f"❌ Configuration error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

asyncio.run(main())
```

### Example 2: Get ALL Gifts (No Limit)

```python
from telegram_gifts_fetcher import TelegramGiftsClient
from colorama import Fore, Style, init
import asyncio

# Initialize colorama
init(autoreset=True)

async def main():
    # Use strict=False for graceful error handling
    client = TelegramGiftsClient(strict=False)
    
    if not await client.connect():
        print(f"{Fore.RED}❌ Failed to connect. Please check your .env file.{Style.RESET_ALL}")
        return
    
    try:
        print(f"{Fore.GREEN}✓ Connected to Telegram{Style.RESET_ALL}")
        
        # Get all gifts for current user
        print(f"{Fore.CYAN}Fetching all gifts for current user...{Style.RESET_ALL}")
        my_gifts = await client.get_all_gifts("me")
        print(f"{Fore.YELLOW}Found {my_gifts.count_gifts} total gifts{Style.RESET_ALL}")
        
        # Display recent gifts
        if my_gifts.gifts:
            print(f"{Fore.MAGENTA}Recent gifts:{Style.RESET_ALL}")
            for i, gift in enumerate(my_gifts.gifts[:3]):
                print(f"{Fore.WHITE}  {i+1}. {gift.name} - {gift.message or 'No message'}{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    finally:
        await client.disconnect()
        print(f"{Fore.GREEN}✓ Disconnected{Style.RESET_ALL}")

asyncio.run(main())
```

### Example 3: Gift Analysis and Export

```python
from telegram_gifts_fetcher import TelegramGiftsClient
from collections import Counter
import json, asyncio

async def analyze_and_export():
    client = TelegramGiftsClient(strict=False)
    
    if not await client.connect():
        print("❌ Failed to connect. Please check your .env file.")
        return
    
    try:
        result = await client.get_user_gifts('username')
        
        # Analyze gift types
        gift_types = Counter(gift.type for gift in result.gifts)
        print("📊 Gift Types Distribution:")
        for gift_type, count in gift_types.items():
            print(f"  🎁 {gift_type}: {count}")
        
        # Export to JSON
        export_data = {
            'total_gifts': result.count_gifts,
            'gift_types': dict(gift_types),
            'gifts': [{
                'name': gift.name,
                'type': gift.type,
                'message': gift.message,
                'received_date': gift.received_date
            } for gift in result.gifts]
        }
        
        with open('gifts_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"📤 Exported analysis to gifts_analysis.json")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()

asyncio.run(analyze_and_export())
```

## 🆕 What's New in v2.1.3

### 🛠️ Improved Error Handling

- **Fixed constructor exceptions**: No more `ValueError` thrown in constructor by default
- **New `strict` parameter**: Control when validation happens
- **Better error messages**: More helpful guidance for missing credentials
- **Graceful degradation**: Handle missing `.env` files elegantly

### 🔧 Migration from v2.1.2.x

**Old way (could throw exceptions):**
```python
client = TelegramGiftsClient()  # Could throw ValueError here
```

**New way (recommended):**
```python
client = TelegramGiftsClient(strict=False)  # No exceptions in constructor
if not await client.connect():  # Validation happens here
    # Handle missing credentials gracefully
    return
```

**Or with traditional try-catch:**
```python
try:
    client = TelegramGiftsClient()  # strict=True by default
except ValueError as e:
    # Handle missing credentials
    pass
```

## 📊 API Reference

### `TelegramGiftsClient`

#### Constructor Parameters
- `api_id` (int, optional): Telegram API ID
- `api_hash` (str, optional): Telegram API Hash  
- `session_name` (str, optional): Session file name (default: 'account')
- `strict` (bool, optional): Enable strict validation (default: True)
  - `True`: Validates credentials in constructor, may raise `ValueError`
  - `False`: Defers validation to `connect()` method

#### `get_user_gifts(username, limit=100)`

Fetches Telegram Star Gifts for a specified user with limit.

**Parameters:**
- `username` (str): Target username (without @)
- `limit` (int, optional): Maximum gifts to fetch (default: 100)

#### `get_all_gifts(username)`

Fetches ALL Telegram Star Gifts for a specified user without any limit.

**Parameters:**
- `username` (str): Target username (without @) or "me" for current user

**Returns:**
Both methods return a `GiftsResponse` object with:
```python
result.gifts         # List of gift objects
result.count_gifts   # Total gifts found

# Each gift object has:
gift.received_date   # Unix timestamp
gift.type           # Gift type classification
gift.message        # Gift message (optional)
gift.name_hidden    # Whether sender name is hidden
gift.can_upgrade    # Upgrade availability
gift.pinned_to_top  # Whether gift is pinned
gift.transfer_stars # Stars for transfer
gift.user_convert_stars # Stars for conversion
gift.name           # Gift name
gift.slug           # Gift slug
```

## 🎯 Gift Types Supported

| Type | Description |
|------|-------------|
| `star_gift` | Regular star gifts |
| `unique_gift` | Unique/limited gifts |
| `regular_gift` | Standard gifts |
| `unknown` | Future gift types |

## 🛡️ Error Handling

```python
from telegram_gifts_fetcher import TelegramGiftsClient
from telethon.errors import RPCError
import asyncio

async def safe_fetch():
    client = TelegramGiftsClient()
    try:
        if await client.connect():
            result = await client.get_user_gifts('username')
            print(f"✅ Fetched {result.count_gifts} gifts")
    except RPCError as e:
        print(f"❌ API error: {e}")
    finally:
        await client.disconnect()

asyncio.run(safe_fetch())
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with [Telethon](https://github.com/LonamiWebs/Telethon)
- Enhanced with modern Python async patterns
- Supports all current Telegram gift types