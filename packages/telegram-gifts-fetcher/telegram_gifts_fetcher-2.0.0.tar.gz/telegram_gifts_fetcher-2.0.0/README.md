# 🎁 Telegram Gifts Fetcher

[![PyPI version](https://badge.fury.io/py/telegram-gifts-fetcher.svg)](https://badge.fury.io/py/telegram-gifts-fetcher)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**The first and only library to fetch Telegram Star Gifts from user profiles! 🌟**

This library allows you to programmatically fetch and analyze Telegram Star Gifts from any user profile using the official Telegram API.

## ✨ Features

- 🎯 **First on PyPI** - The pioneering library for Telegram Star Gifts
- 🔄 **All Gift Types** - Supports StarGift, StarGiftUnique, StarGiftRegular, and unknown types
- 📊 **Detailed Analysis** - Complete gift information with timestamps, costs, and metadata
- 🚀 **Async Support** - Built with modern async/await patterns
- 🛡️ **Type Safety** - Comprehensive error handling and type checking
- 📱 **Easy Integration** - Simple API for quick integration into your projects
- 📈 **NEW**: Advanced gift analysis and statistics
- 🔍 **NEW**: Powerful gift filtering capabilities
- 💾 **NEW**: Data export to JSON and CSV formats
- 📊 **NEW**: Trend analysis over time periods
- 👥 **NEW**: Sender pattern analysis
- 🧮 **NEW**: Comprehensive statistical insights

## 📦 Installation

```bash
pip install telegram-gifts-fetcher
```

## 🚀 Quick Start

### 1. Get Telegram API Credentials

1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Go to "API Development Tools"
4. Create a new application
5. Copy your `API_ID` and `API_HASH`

### 2. Basic Usage

```python
import asyncio
from telethon import TelegramClient
from telegram_gifts_fetcher import get_user_gifts_extended

async def main():
    # Initialize Telegram client
    client = TelegramClient('session', API_ID, API_HASH)
    await client.start()
    
    try:
        # Fetch gifts for a user
        gifts_data = await get_user_gifts_extended(client, 'username')
        
        print(f"Found {gifts_data['count_gifts']} gifts!")
        
        for gift in gifts_data['gifts']:
            print(f"Gift: {gift['type']} - Received: {gift['received_date']}")
            
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Environment Setup

Create a `.env` file:

```env
API_ID=your_api_id
API_HASH=your_api_hash
```

## 📖 API Reference

### `get_user_gifts_extended(client, username, offset="", limit=100)`

Fetches Telegram Star Gifts for a specified user.

**Parameters:**
- `client` (TelegramClient): Authenticated Telethon client
- `username` (str): Target username (without @)
- `offset` (str, optional): Pagination offset
- `limit` (int, optional): Maximum gifts to fetch (default: 100)

**Returns:**
```python
{
    "gifts": [  # List of gift objects
        {
            "received_date": 1234567890,  # Unix timestamp
            "type": "StarGift",  # Gift type
            "from_id": 123456789,  # Sender ID (None if anonymous)
            "message": "Happy Birthday!",  # Gift message
            "stars": 100,  # Gift cost in stars
            "convert_stars": 80,  # Conversion value
            # ... more fields
        }
    ],
    "count_gifts": 5  # Total gifts found
}
```

## 🎯 Gift Types Supported

| Type | Constructor ID | Description |
|------|----------------|-------------|
| `StarGift` | `0x2cc73c8` | Regular star gifts |
| `StarGiftUnique` | `0x5c62d151` | Unique/limited gifts |
| `StarGiftRegular` | `0x736b72c7` | Standard gifts |
| `Unknown` | Various | Future gift types |

## 🔧 Advanced Usage

### Custom Gift Processing

```python
async def process_gifts(client, username):
    gifts_data = await get_user_gifts_extended(client, username)
    
    # Filter by gift type
    unique_gifts = [g for g in gifts_data['gifts'] if g['type'] == 'StarGiftUnique']
    
    # Find most expensive gift
    most_expensive = max(gifts_data['gifts'], key=lambda x: x.get('stars', 0))
    
    return {
        'unique_count': len(unique_gifts),
        'most_expensive': most_expensive
    }
```

### 📊 Advanced Analysis Features (v1.1.0+)

#### Comprehensive Gift Analysis

```python
import asyncio
from telethon import TelegramClient
from telegram_gifts_fetcher import get_user_gifts_with_analysis

async def main():
    async with TelegramClient('session', api_id, api_hash) as client:
        # Get gifts with full analysis
        analysis = await get_user_gifts_with_analysis(client, 'username')
        
        # Basic statistics
        stats = analysis['statistics']
        print(f"📊 Total gifts: {stats['total_gifts']}")
        print(f"⭐ Total stars: {stats['total_stars_received']}")
        print(f"👥 Unique senders: {stats['unique_senders']}")
        print(f"💾 Saved gifts: {stats['saved_gifts']}")
        print(f"🎭 Anonymous gifts: {stats['anonymous_gifts']}")
        
        # Gift types distribution
        for gift_type, count in stats['gift_types'].items():
            print(f"🎁 {gift_type}: {count}")

asyncio.run(main())
```

#### Gift Filtering and Export

```python
from telegram_gifts_fetcher import (
    get_user_gifts_extended,
    filter_gifts,
    export_gifts_to_json,
    export_gifts_to_csv
)
from datetime import datetime, timedelta

async def filter_and_export():
    async with TelegramClient('session', api_id, api_hash) as client:
        data = await get_user_gifts_extended(client, 'username')
        gifts = data['gifts']
        
        # Filter high-value gifts from last month
        high_value_recent = filter_gifts(
            gifts,
            min_stars=100,
            date_from=datetime.now() - timedelta(days=30)
        )
        
        # Filter by gift type
        star_gifts = filter_gifts(gifts, gift_type='star')
        
        # Filter saved gifts only
        saved_gifts = filter_gifts(gifts, saved_only=True)
        
        # Export to different formats
        export_gifts_to_json(high_value_recent, 'high_value_gifts.json')
        export_gifts_to_csv(star_gifts, 'star_gifts.csv')
        
        print(f"Exported {len(high_value_recent)} high-value gifts")
        print(f"Exported {len(star_gifts)} star gifts")

asyncio.run(filter_and_export())
```

#### Trend and Sender Analysis

```python
from telegram_gifts_fetcher import (
    get_gift_trends,
    get_sender_analysis,
    analyze_gifts_statistics
)

async def analyze_patterns():
    async with TelegramClient('session', api_id, api_hash) as client:
        data = await get_user_gifts_extended(client, 'username')
        gifts = data['gifts']
        
        # Analyze weekly trends
        weekly_trends = get_gift_trends(gifts, period_days=7)
        print("📈 Weekly Trends:")
        for period, data in weekly_trends.items():
            print(f"  Week {period}: {data['gift_count']} gifts, {data['total_stars']} stars")
        
        # Analyze senders
        sender_data = get_sender_analysis(gifts)
        print("\n👥 Top Senders:")
        for sender_id, data in list(sender_data.items())[:3]:
            print(f"  Sender {sender_id}:")
            print(f"    Gifts: {data['gift_count']}")
            print(f"    Total stars: {data['total_stars']}")
            print(f"    Average: {data['average_stars_per_gift']:.1f} stars/gift")

asyncio.run(analyze_patterns())
```

### Dependency Error Handler 🛠️

The library includes an automatic dependency error handler that detects and fixes circular dependencies:

```python
from telegram_gifts_fetcher import (
    handle_dependency_errors,
    check_circular_dependencies,
    fix_circular_dependencies,
    DependencyError
)

# Automatic error handling
try:
    handle_dependency_errors()
except DependencyError as e:
    print(f"Dependency error: {e}")

# Manual checking
if check_circular_dependencies("telegram-gifts-fetcher"):
    print("Circular dependencies detected!")
    fix_circular_dependencies("telegram-gifts-fetcher")
```

**Features of the dependency handler:**
- 🔍 **Automatic Detection** - Scans setup.py, pyproject.toml, and requirements.txt
- 🔧 **Auto-Fix** - Removes circular dependencies automatically
- 📝 **Detailed Logging** - Comprehensive logging with loguru
- ⚡ **Fast Processing** - Efficient file parsing and modification

### Error Handling

```python
try:
    gifts_data = await get_user_gifts_extended(client, 'username')
except Exception as e:
    print(f"Error fetching gifts: {e}")
```

## 📊 Gift Data Structure

The `get_user_gifts_extended` function returns a dictionary with the following structure:

```python
{
    'gifts': [
        {
            'received_date': int,           # Unix timestamp
            'constructor_id': str,          # Telegram constructor ID
            'from_id': int,                 # Sender user ID (if available)
            'message': str,                 # Gift message (if any)
            'msg_id': int,                  # Message ID
            'saved_id': str,                # Saved gift ID (if any)
            'name_hidden': bool,            # Whether sender name is hidden
            'unsaved': bool,                # Whether gift is unsaved
            'refunded': bool,               # Whether gift was refunded
            'can_upgrade': bool,            # Whether gift can be upgraded
            'pinned_to_top': bool,          # Whether gift is pinned
            'type': str,                    # Gift type classification
            'raw_data': str,                # Raw Telegram object data
            'transfer_stars': int,          # Stars value for transfer (if applicable)
            'user_convert_stars': int,      # Stars value for conversion (if applicable)
        }
    ],
    'count_gifts': int,                     # Total number of gifts
    'total_cost': {
        'stars': int                        # Total stars cost
    }
}
```

## 🔍 Supported Gift Types

- **StarGift**: Regular star gifts
- **StarGiftUnique**: Unique star gifts
- **StarGiftRegular**: Regular gifts (newly supported)
- **Unknown**: Unrecognized gift types (logged for debugging)

## 🐛 Debugging

The library includes comprehensive logging. To enable debug output:

```python
from loguru import logger
logger.add("debug.log", level="DEBUG")
```

## 📝 Files

- `main.py` - Main demo application
- `gift_fetcher_extended.py` - Extended gift fetcher library
- `d.py` - Debug and testing script
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Based on the original `telegram_gift_fetcher` library
- Enhanced to support additional gift types and provide better debugging