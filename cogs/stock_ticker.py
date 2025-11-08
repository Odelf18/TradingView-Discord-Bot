"""
Stock Ticker Cog
Detects stock ticker symbols in messages and provides stock information
"""
import discord
from discord.ext import commands
import re
import yfinance as yf
from datetime import datetime
import time
from functools import lru_cache
from config import (TICKER_PATTERN, ADVANCED_TICKER_PATTERN, EMBED_COLOR_GREEN, EMBED_COLOR_RED,
                    CACHE_EXPIRY_SECONDS, USE_EMBEDDED_CHARTS, CHARTIMG_API_KEY,
                    TIMEFRAME_MAPPING, TECHNICAL_INDICATORS)
from utils.tradingview import format_chart_links_markdown, generate_chart_image_bytes
import io


class StockTicker(commands.Cog):
    """Cog for detecting and responding to stock ticker symbols"""

    def __init__(self, bot):
        self.bot = bot
        self.ticker_pattern = re.compile(TICKER_PATTERN)
        self.advanced_ticker_pattern = re.compile(ADVANCED_TICKER_PATTERN)
        # Track recently processed messages to avoid duplicates
        self.processed_messages = set()

    @lru_cache(maxsize=100)
    def get_stock_data_cached(self, symbol, timestamp_bucket):
        """
        Get stock data with caching to avoid rate limits
        timestamp_bucket groups requests into time buckets for caching
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Check if we got valid data
            if not info or 'regularMarketPrice' not in info:
                return None

            return info
        except Exception as e:
            print(f"Erreur lors de la récupération des données pour {symbol}: {e}")
            return None

    def get_stock_data(self, symbol):
        """Get stock data with cache buckets based on CACHE_EXPIRY_SECONDS"""
        # Create time buckets for caching (e.g., 5-minute buckets)
        timestamp_bucket = int(time.time() / CACHE_EXPIRY_SECONDS)
        return self.get_stock_data_cached(symbol, timestamp_bucket)

    def parse_ticker_request(self, text):
        """
        Parse ticker request with optional timeframe and indicators

        Examples:
            $AAPL -> ('AAPL', 'D', [])
            $TSLA 1h -> ('TSLA', '60', [])
            $MSFT 4h EMA -> ('MSFT', '240', ['Exponential Moving Average'])
            $GOOGL 1d RSI,MACD -> ('GOOGL', 'D', ['Relative Strength Index', 'MACD'])

        Returns:
            tuple: (symbol, interval, indicators_list)
        """
        match = self.advanced_ticker_pattern.search(text)
        if not match:
            return None

        symbol = match.group(1).upper()
        timeframe = match.group(2)  # e.g., "1h", "4h", "1d"
        indicators_str = match.group(3)  # e.g., "EMA,RSI" or "Bollinger"

        # Convert timeframe to TradingView format
        if timeframe:
            interval = TIMEFRAME_MAPPING.get(timeframe.lower(), TIMEFRAME_MAPPING['default'])
        else:
            interval = TIMEFRAME_MAPPING['default']  # Default to 1 day

        # Parse indicators
        indicators = []
        if indicators_str:
            # Split by comma or space
            indicator_names = re.split(r'[,\s]+', indicators_str.strip())
            for ind in indicator_names:
                ind_lower = ind.lower()
                if ind_lower in TECHNICAL_INDICATORS:
                    indicators.append(TECHNICAL_INDICATORS[ind_lower])

        return (symbol, interval, indicators)

    def format_number(self, num):
        """Format large numbers with appropriate suffixes (K, M, B, T)"""
        if num is None:
            return 'N/A'

        try:
            num = float(num)
            if num >= 1_000_000_000_000:  # Trillion
                return f"${num / 1_000_000_000_000:.2f}T"
            elif num >= 1_000_000_000:  # Billion
                return f"${num / 1_000_000_000:.2f}B"
            elif num >= 1_000_000:  # Million
                return f"${num / 1_000_000:.2f}M"
            elif num >= 1_000:  # Thousand
                return f"${num / 1_000:.2f}K"
            else:
                return f"${num:.2f}"
        except (ValueError, TypeError):
            return 'N/A'

    def format_volume(self, volume):
        """Format volume numbers"""
        if volume is None:
            return 'N/A'

        try:
            volume = float(volume)
            if volume >= 1_000_000_000:
                return f"{volume / 1_000_000_000:.2f}B"
            elif volume >= 1_000_000:
                return f"{volume / 1_000_000:.2f}M"
            elif volume >= 1_000:
                return f"{volume / 1_000:.2f}K"
            else:
                return f"{volume:,.0f}"
        except (ValueError, TypeError):
            return 'N/A'

    async def create_stock_embed(self, symbol, info):
        """Create a rich Discord embed with stock information"""

        # Get basic info
        company_name = info.get('longName', info.get('shortName', symbol))
        current_price = info.get('regularMarketPrice', info.get('currentPrice'))
        previous_close = info.get('regularMarketPreviousClose', info.get('previousClose'))
        volume = info.get('volume', info.get('regularMarketVolume'))
        market_cap = info.get('marketCap')
        pe_ratio = info.get('trailingPE', info.get('forwardPE'))

        # Calculate price change
        price_change = None
        price_change_percent = None
        embed_color = EMBED_COLOR_GREEN

        if current_price and previous_close:
            price_change = current_price - previous_close
            price_change_percent = (price_change / previous_close) * 100
            embed_color = EMBED_COLOR_GREEN if price_change >= 0 else EMBED_COLOR_RED

        # Create embed
        embed = discord.Embed(
            title=f"${symbol.upper()} - {company_name}",
            color=embed_color,
            timestamp=datetime.utcnow()
        )

        # Price field
        if current_price:
            price_text = f"**${current_price:,.2f}**"
            if price_change is not None and price_change_percent is not None:
                change_emoji = "📈" if price_change >= 0 else "📉"
                sign = "+" if price_change >= 0 else ""
                price_text += f"\n{change_emoji} {sign}${price_change:.2f} ({sign}{price_change_percent:.2f}%)"
            embed.add_field(name="Prix", value=price_text, inline=True)
        else:
            embed.add_field(name="Prix", value="N/A", inline=True)

        # Volume field
        if volume:
            embed.add_field(name="Volume", value=self.format_volume(volume), inline=True)

        # Market cap field
        if market_cap:
            embed.add_field(name="Capitalisation", value=self.format_number(market_cap), inline=True)

        # P/E Ratio
        if pe_ratio:
            embed.add_field(name="P/E Ratio", value=f"{pe_ratio:.2f}", inline=True)

        # Day's range
        day_low = info.get('regularMarketDayLow', info.get('dayLow'))
        day_high = info.get('regularMarketDayHigh', info.get('dayHigh'))
        if day_low and day_high:
            embed.add_field(
                name="Range du jour",
                value=f"${day_low:,.2f} - ${day_high:,.2f}",
                inline=True
            )

        # 52-week range
        week_52_low = info.get('fiftyTwoWeekLow')
        week_52_high = info.get('fiftyTwoWeekHigh')
        if week_52_low and week_52_high:
            embed.add_field(
                name="Range 52 semaines",
                value=f"${week_52_low:,.2f} - ${week_52_high:,.2f}",
                inline=True
            )

        # Add chart links (always show as fallback or additional option)
        chart_links = format_chart_links_markdown(symbol)
        embed.add_field(name="\u200b", value=chart_links, inline=False)

        # Footer
        embed.set_footer(text="Données fournies par Yahoo Finance via yfinance")

        return embed

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for messages containing stock ticker symbols"""

        # Ignore bot messages
        if message.author.bot:
            return

        # Ignore if message was already processed (avoid duplicates)
        if message.id in self.processed_messages:
            return

        # Parse ticker requests with advanced syntax
        # Look for patterns like: $AAPL, $TSLA 1h, $MSFT 4h EMA,RSI
        ticker_requests = []
        for match in self.advanced_ticker_pattern.finditer(message.content):
            parsed = self.parse_ticker_request(match.group(0))
            if parsed:
                ticker_requests.append(parsed)

        # Remove duplicates
        seen = set()
        unique_requests = []
        for symbol, interval, indicators in ticker_requests:
            key = (symbol, interval, tuple(indicators))
            if key not in seen:
                seen.add(key)
                unique_requests.append((symbol, interval, indicators))

        # Process each unique ticker request
        for symbol, interval, indicators in unique_requests:
            # Ignore common false positives (currencies, etc.)
            if symbol in ['USD', 'EUR', 'GBP', 'CAD', 'JPY', 'CHF', 'AUD']:
                continue

            try:
                # Get stock data
                info = self.get_stock_data(symbol)

                if info is None:
                    # Stock not found or error
                    await message.channel.send(
                        f"❌ Impossible de trouver les données pour `${symbol}`. "
                        f"Vérifiez que le symbole est correct.",
                        delete_after=10
                    )
                    continue

                # Create embed
                embed = await self.create_stock_embed(symbol, info)

                # Add timeframe and indicators info to embed if specified
                if interval != 'D' or indicators:
                    extra_info = []
                    # Convert interval back to readable format
                    readable_interval = {v: k for k, v in TIMEFRAME_MAPPING.items()}.get(interval, interval)
                    extra_info.append(f"📊 Intervalle: **{readable_interval}**")
                    if indicators:
                        extra_info.append(f"📈 Indicateurs: **{', '.join(ind for ind in indicators)}**")
                    embed.add_field(name="\u200b", value="\n".join(extra_info), inline=False)

                # Generate and attach chart image if enabled
                chart_file = None
                if USE_EMBEDDED_CHARTS and CHARTIMG_API_KEY:
                    # Free tier limit: 800x600 max
                    image_bytes = await generate_chart_image_bytes(
                        symbol,
                        interval=interval,
                        width=800,
                        height=500,
                        indicators=indicators if indicators else None
                    )
                    if image_bytes:
                        # Create Discord file from image bytes
                        chart_file = discord.File(io.BytesIO(image_bytes), filename=f"{symbol}_chart.png")
                        # Set the image in the embed
                        embed.set_image(url=f"attachment://{symbol}_chart.png")

                # Send embed with optional chart attachment
                if chart_file:
                    await message.channel.send(embed=embed, file=chart_file)
                else:
                    await message.channel.send(embed=embed)

                # Mark message as processed
                self.processed_messages.add(message.id)

                # Limit cache size (keep last 1000 messages)
                if len(self.processed_messages) > 1000:
                    # Remove oldest half
                    self.processed_messages = set(list(self.processed_messages)[500:])

            except Exception as e:
                print(f"Erreur lors du traitement de ${ticker}: {e}")
                import traceback
                traceback.print_exc()

                await message.channel.send(
                    f"❌ Erreur lors de la récupération des données pour `${ticker}`.",
                    delete_after=10
                )

    @commands.command(name='stock', aliases=['ticker', 's'])
    async def stock_command(self, ctx, symbol: str):
        """
        Commande manuelle pour obtenir des informations sur une action
        Usage: !stock AAPL
        """
        symbol = symbol.upper().replace('$', '')

        try:
            info = self.get_stock_data(symbol)

            if info is None:
                await ctx.send(
                    f"❌ Impossible de trouver les données pour `${symbol}`. "
                    f"Vérifiez que le symbole est correct."
                )
                return

            # Create embed
            embed = await self.create_stock_embed(symbol, info)

            # Generate and attach chart image if enabled
            chart_file = None
            if USE_EMBEDDED_CHARTS and CHARTIMG_API_KEY:
                # Use 1-day interval for main chart
                # Free tier limit: 800x600 max
                image_bytes = await generate_chart_image_bytes(symbol, interval='D', width=800, height=500)
                if image_bytes:
                    # Create Discord file from image bytes
                    chart_file = discord.File(io.BytesIO(image_bytes), filename=f"{symbol}_chart.png")
                    # Set the image in the embed
                    embed.set_image(url=f"attachment://{symbol}_chart.png")

            # Send embed with optional chart attachment
            if chart_file:
                await ctx.send(embed=embed, file=chart_file)
            else:
                await ctx.send(embed=embed)

        except Exception as e:
            print(f"Erreur lors du traitement de la commande !stock {symbol}: {e}")
            import traceback
            traceback.print_exc()

            await ctx.send(f"❌ Erreur lors de la récupération des données pour `${symbol}`.")


async def setup(bot):
    """Required function to load the cog"""
    await bot.add_cog(StockTicker(bot))
