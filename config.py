"""
Configuration file for the Discord Stock Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Discord Bot Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Chart-img.com API Configuration (optional - for embedded chart images)
CHARTIMG_API_KEY = os.getenv('CHARTIMG_API_KEY', '')
USE_EMBEDDED_CHARTS = os.getenv('USE_EMBEDDED_CHARTS', 'true').lower() == 'true'

# Bot Settings
COMMAND_PREFIX = '!'
BOT_DESCRIPTION = 'Stock ticker bot - automatically responds to $TICKER symbols'

# Ticker Detection Settings
TICKER_PATTERN = r'\$([A-Z]{1,5})\b'  # Matches $AAPL, $TSLA, etc.
# Advanced pattern: $AAPL 1h EMA,RSI
ADVANCED_TICKER_PATTERN = r'\$([A-Z]{1,5})(?:\s+(\d+[smhdwMy]))?(?:\s+([A-Za-z,\s]+))?'

# Cache Settings (to avoid rate limiting)
CACHE_EXPIRY_SECONDS = 300  # 5 minutes

# Color for Discord embeds
EMBED_COLOR_GREEN = 0x00ff00  # Green for positive/neutral
EMBED_COLOR_RED = 0xff0000     # Red for negative

# TradingView Chart Intervals
CHART_INTERVALS = {
    '1h': '60',
    '4h': '240',
    '1d': 'D'
}

# Timeframe mapping (user input -> TradingView format)
TIMEFRAME_MAPPING = {
    # Seconds/Minutes
    '1s': '1S', '5s': '5S', '10s': '10S', '15s': '15S', '30s': '30S',
    '1m': '1', '3m': '3', '5m': '5', '15m': '15', '30m': '30', '45m': '45',
    # Hours
    '1h': '60', '2h': '120', '3h': '180', '4h': '240', '6h': '360', '8h': '480', '12h': '720',
    # Days/Weeks/Months
    '1d': 'D', '1day': 'D', 'd': 'D',
    '1w': 'W', '1week': 'W', 'w': 'W',
    '1M': 'M', '1month': 'M', 'M': 'M',
    # Default
    'default': 'D'
}

# Technical Indicators mapping
TECHNICAL_INDICATORS = {
    # Moving Averages
    'ema': 'Exponential Moving Average',
    'sma': 'Simple Moving Average',
    'wma': 'Weighted Moving Average',
    # Oscillators
    'rsi': 'Relative Strength Index',
    'macd': 'MACD',
    'stoch': 'Stochastic',
    'cci': 'Commodity Channel Index',
    # Bands
    'bb': 'Bollinger Bands',
    'bollinger': 'Bollinger Bands',
    # Volume
    'volume': 'Volume',
    'vol': 'Volume',
    # Trend
    'adx': 'Average Directional Index',
    'ichimoku': 'Ichimoku Cloud',
    # Other
    'atr': 'Average True Range',
    'obv': 'On Balance Volume',
}
