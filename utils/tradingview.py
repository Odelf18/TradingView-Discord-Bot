"""
TradingView URL Generator
Generates direct links to TradingView charts with specific intervals
Also supports embedded chart images via chart-img.com API
"""
from config import CHART_INTERVALS, CHARTIMG_API_KEY, USE_EMBEDDED_CHARTS
import aiohttp
import urllib.parse


def get_exchange_for_symbol(symbol):
    """
    Determine the exchange for a given stock symbol
    This is a simplified version - in production, you'd want to use an API
    to get the correct exchange.
    """
    # Common NASDAQ stocks
    nasdaq_stocks = {
        'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA',
        'AMD', 'NFLX', 'INTC', 'CSCO', 'ADBE', 'PYPL', 'CMCSA', 'AVGO',
        'TXN', 'QCOM', 'COST', 'SBUX', 'CHTR', 'INTU', 'AMGN', 'TMUS',
        'GILD', 'MDLZ', 'VRTX', 'ADP', 'ISRG', 'FISV', 'BKNG', 'REGN',
        'ATVI', 'CSX', 'ILMN', 'BIIB', 'MU', 'LRCX', 'ADSK', 'MNST'
    }

    # Default to NASDAQ for tech stocks, NYSE for others
    if symbol.upper() in nasdaq_stocks:
        return 'NASDAQ'
    else:
        return 'NYSE'


def generate_tradingview_url(symbol, interval='60'):
    """
    Generate a TradingView chart URL for a given symbol and interval

    Args:
        symbol (str): Stock ticker symbol (e.g., 'AAPL')
        interval (str): Chart interval - '60' (1h), '240' (4h), 'D' (1 day)

    Returns:
        str: TradingView chart URL
    """
    exchange = get_exchange_for_symbol(symbol)
    base_url = "https://www.tradingview.com/chart/"
    params = f"?symbol={exchange}:{symbol}&interval={interval}"
    return base_url + params


def generate_all_chart_links(symbol):
    """
    Generate all chart links (1h, 4h, 1d) for a symbol

    Args:
        symbol (str): Stock ticker symbol

    Returns:
        dict: Dictionary with interval names as keys and URLs as values
    """
    return {
        interval_name: generate_tradingview_url(symbol, interval_code)
        for interval_name, interval_code in CHART_INTERVALS.items()
    }


def format_chart_links_markdown(symbol):
    """
    Format chart links as Discord markdown with clickable links

    Args:
        symbol (str): Stock ticker symbol

    Returns:
        str: Formatted markdown string with chart links
    """
    links = generate_all_chart_links(symbol)
    formatted = " | ".join([
        f"[{interval.upper()}]({url})"
        for interval, url in links.items()
    ])
    return f"📊 **Graphiques TradingView:** {formatted}"


async def generate_chart_image_bytes(symbol, interval='D', width=800, height=500, indicators=None):
    """
    Generate a chart image using chart-img.com API v2 and return image bytes

    Args:
        symbol (str): Stock ticker symbol
        interval (str): Chart interval - '1h', '4h', '1D', etc.
        width (int): Image width in pixels (max 800 for free tier)
        height (int): Image height in pixels (max 600 for free tier)
        indicators (list): List of technical indicator names to display

    Returns:
        bytes: Image data as bytes, or None if API key not configured or error

    Note:
        Free tier limit is 800x600 pixels maximum
    """
    if not CHARTIMG_API_KEY:
        return None

    exchange = get_exchange_for_symbol(symbol)
    ticker = f"{exchange}:{symbol}"

    # Convert interval format if needed (60 -> 1h, 240 -> 4h)
    interval_mapping = {
        '60': '1h',
        '240': '4h',
        'D': '1D',
        '1': '1m',
        '3': '3m',
        '5': '5m',
        '15': '15m',
        '30': '30m',
        '45': '45m',
        '120': '2h',
        '180': '3h',
        '360': '6h',
        '480': '8h',
        '720': '12h',
        'W': '1W',
        'M': '1M'
    }
    chart_interval = interval_mapping.get(interval, interval)

    # chart-img.com API v2 endpoint
    api_url = "https://api.chart-img.com/v2/tradingview/advanced-chart"

    headers = {
        'x-api-key': CHARTIMG_API_KEY,
        'content-type': 'application/json'
    }

    # Build studies list (indicators)
    studies = []

    # Always add Volume by default if no indicators specified
    if not indicators:
        studies.append({
            'name': 'Volume',
            'forceOverlay': False
        })
    else:
        # Add Volume + requested indicators
        studies.append({
            'name': 'Volume',
            'forceOverlay': False
        })
        for indicator in indicators:
            studies.append({
                'name': indicator,
                'forceOverlay': False
            })

    payload = {
        'symbol': ticker,
        'interval': chart_interval,
        'width': width,
        'height': height,
        'theme': 'dark',
        'studies': studies
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    # API v2 returns the image data directly
                    image_bytes = await response.read()
                    return image_bytes
                else:
                    error_text = await response.text()
                    print(f"Erreur API chart-img.com (status {response.status}): {error_text}")
                    return None
    except Exception as e:
        print(f"Erreur lors de la génération du graphique: {e}")
        import traceback
        traceback.print_exc()
        return None


async def generate_multiple_chart_images(symbol, intervals=['60', '240', 'D']):
    """
    Generate multiple chart image URLs for different intervals

    Args:
        symbol (str): Stock ticker symbol
        intervals (list): List of intervals to generate

    Returns:
        dict: Dictionary mapping interval names to image URLs
    """
    if not CHARTIMG_API_KEY:
        return {}

    interval_map = {
        '60': '1h',
        '240': '4h',
        'D': '1d'
    }

    charts = {}
    for interval in intervals:
        url = await generate_chart_image_url(symbol, interval)
        if url:
            interval_name = interval_map.get(interval, interval)
            charts[interval_name] = url

    return charts
