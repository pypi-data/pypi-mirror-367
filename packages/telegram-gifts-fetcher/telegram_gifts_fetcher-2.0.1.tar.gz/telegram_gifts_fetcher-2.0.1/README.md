# 🎁 Telegram Gifts Fetcher

[![PyPI version](https://badge.fury.io/py/telegram-gifts-fetcher.svg)](https://badge.fury.io/py/telegram-gifts-fetcher)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/badge/GitHub-Th3ryks-blue)](https://github.com/Th3ryks/TelegramGiftsFetcher)

**A powerful Python library to fetch and analyze Telegram Star Gifts! 🌟**

This library provides a comprehensive solution for programmatically fetching, analyzing, and managing Telegram Star Gifts from user profiles using the official Telegram API.

## ✨ Features

- 🎁 **Complete Gift Support** - Handles all Telegram gift types (StarGift, StarGiftUnique, StarGiftRegular)
- 📊 **Advanced Analytics** - Detailed gift statistics, trends, and sender analysis
- 🚀 **Async/Await Ready** - Built with modern Python async patterns
- 🛡️ **Robust Error Handling** - Comprehensive error management and type safety
- 📱 **Developer Friendly** - Simple, intuitive API design
- 💾 **Multiple Export Formats** - JSON, CSV, and custom data exports
- 🔍 **Smart Filtering** - Advanced gift filtering by date, type, value, and more
- 🧮 **Statistical Tools** - Comprehensive gift statistics

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

### 2. Environment Setup

Create a `.env` file in your project root:

```env
API_ID=your_api_id_here
API_HASH=your_api_hash_here
```

### 3. Basic Usage

```python
import asyncio
import os
from telethon import TelegramClient
from telegram_gifts_fetcher import TelegramGiftsFetcher
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def main():
    # Initialize client
    client = TelegramClient(
        'session_name',
        int(os.getenv('API_ID')),
        os.getenv('API_HASH')
    )
    
    async with client:
        # Create fetcher instance
        fetcher = TelegramGiftsFetcher(client)
        
        # Fetch gifts for a user
        result = await fetcher.get_user_gifts('username')
        
        print(f"📊 Found {result['count_gifts']} gifts!")
        print(f"⭐ Total value: {result['total_cost']['stars']} stars")
        
        # Display recent gifts
        for gift in result['gifts'][:5]:
            gift_type = gift.get('type', 'Unknown')
            stars = gift.get('stars', 0)
            print(f"🎁 {gift_type}: {stars} stars")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📖 API Reference

### `TelegramGiftsFetcher`

Main class for fetching and analyzing Telegram gifts.

```python
from telegram_gifts_fetcher import TelegramGiftsFetcher

fetcher = TelegramGiftsFetcher(client)
```

#### `get_user_gifts(username, offset="", limit=100)`

Fetches Telegram Star Gifts for a specified user.

**Parameters:**
- `username` (str): Target username (without @)
- `offset` (str, optional): Pagination offset for large datasets
- `limit` (int, optional): Maximum gifts to fetch (default: 100)

**Returns:**
```python
{
    "gifts": [  # List of gift objects
        {
            "received_date": 1234567890,  # Unix timestamp
            "type": "StarGift",  # Gift type classification
            "from_id": 123456789,  # Sender ID (None if anonymous)
            "message": "Happy Birthday!",  # Gift message
            "stars": 100,  # Gift cost in stars
            "convert_stars": 80,  # Conversion value
            "saved": True,  # Whether gift is saved
            "can_upgrade": False,  # Upgrade availability
            # ... additional metadata
        }
    ],
    "count_gifts": 5,  # Total gifts found
    "total_cost": {
        "stars": 500  # Total stars value
    }
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

### 📊 Advanced Features

#### Gift Statistics and Analysis

```python
import asyncio
from telegram_gifts_fetcher import TelegramGiftsFetcher, GiftAnalyzer

async def analyze_gifts():
    async with TelegramClient('session', api_id, api_hash) as client:
        fetcher = TelegramGiftsFetcher(client)
        analyzer = GiftAnalyzer()
        
        # Fetch gifts
        result = await fetcher.get_user_gifts('username')
        
        # Analyze the data
        stats = analyzer.get_statistics(result['gifts'])
        
        print(f"📊 Total gifts: {stats['total_gifts']}")
        print(f"⭐ Total stars: {stats['total_stars']}")
        print(f"👥 Unique senders: {stats['unique_senders']}")
        print(f"💾 Saved gifts: {stats['saved_gifts']}")
        print(f"🎭 Anonymous gifts: {stats['anonymous_gifts']}")
        
        # Gift types distribution
        for gift_type, count in stats['gift_types'].items():
            print(f"🎁 {gift_type}: {count}")

asyncio.run(analyze_gifts())
```

#### Gift Filtering and Export

```python
from telegram_gifts_fetcher import TelegramGiftsFetcher, GiftFilter, GiftExporter
from datetime import datetime, timedelta

async def filter_and_export():
    async with TelegramClient('session', api_id, api_hash) as client:
        fetcher = TelegramGiftsFetcher(client)
        filter_tool = GiftFilter()
        exporter = GiftExporter()
        
        # Fetch gifts
        result = await fetcher.get_user_gifts('username')
        gifts = result['gifts']
        
        # Filter high-value gifts from last month
        high_value_recent = filter_tool.filter_by_criteria(
            gifts,
            min_stars=100,
            date_from=datetime.now() - timedelta(days=30)
        )
        
        # Filter by gift type
        star_gifts = filter_tool.filter_by_type(gifts, 'StarGift')
        
        # Filter saved gifts only
        saved_gifts = filter_tool.filter_saved_only(gifts)
        
        # Export to different formats
        exporter.to_json(high_value_recent, 'high_value_gifts.json')
        exporter.to_csv(star_gifts, 'star_gifts.csv')
        
        print(f"📤 Exported {len(high_value_recent)} high-value gifts")
        print(f"📤 Exported {len(star_gifts)} star gifts")

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

### 🛡️ Error Handling

```python
from telegram_gifts_fetcher import TelegramGiftsFetcher, TelegramGiftsError

async def safe_fetch():
    try:
        async with TelegramClient('session', api_id, api_hash) as client:
            fetcher = TelegramGiftsFetcher(client)
            result = await fetcher.get_user_gifts('username')
            print(f"✅ Successfully fetched {result['count_gifts']} gifts")
    except TelegramGiftsError as e:
        print(f"❌ Gift fetching error: {e}")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")

asyncio.run(safe_fetch())
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