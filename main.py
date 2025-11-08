"""
Discord Stock Ticker Bot
Automatically detects stock ticker symbols (e.g., $AAPL) and provides stock information
"""
import discord
from discord.ext import commands
import sys
import asyncio
from config import DISCORD_TOKEN, COMMAND_PREFIX, BOT_DESCRIPTION

# Check if token is configured
if not DISCORD_TOKEN:
    print("ERROR: DISCORD_TOKEN not found!")
    print("Please create a .env file with your Discord bot token.")
    print("See .env.example for reference.")
    sys.exit(1)

# Configure bot intents
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content

# Initialize bot
bot = commands.Bot(
    command_prefix=COMMAND_PREFIX,
    description=BOT_DESCRIPTION,
    intents=intents
)


@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord"""
    print(f'Bot connecté en tant que {bot.user.name} (ID: {bot.user.id})')
    print(f'Discord.py version: {discord.__version__}')
    print('------')
    print('Le bot est prêt à détecter les tickers boursiers!')
    print('Tapez $AAPL dans un channel pour tester.')
    print('------')


@bot.event
async def on_error(event, *args, **kwargs):
    """Handle errors"""
    print(f'Erreur dans {event}:')
    import traceback
    traceback.print_exc()


async def load_cogs():
    """Load all bot extensions (cogs)"""
    try:
        await bot.load_extension('cogs.stock_ticker')
        print('Cog stock_ticker chargé avec succès')
    except Exception as e:
        print(f'Erreur lors du chargement du cog stock_ticker: {e}')
        import traceback
        traceback.print_exc()


async def main():
    """Main entry point"""
    async with bot:
        await load_cogs()
        await bot.start(DISCORD_TOKEN)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\nBot arrêté par l\'utilisateur')
    except Exception as e:
        print(f'Erreur fatale: {e}')
        import traceback
        traceback.print_exc()
