# main.py

#!/usr/bin/env python3
"""
main.py - GotLockz Discord Bot Entry Point

Production-ready Discord bot with enhanced betting commands,
OCR integration, and MLB data analysis.
"""

from bot.commands.info import InfoCommands
from bot.commands.betting import BettingCommands
from bot.config import load_config
from dotenv import load_dotenv
from discord.ext import commands
import discord
import asyncio
import logging
import os
from pathlib import Path
from datetime import datetime
import sys

# Add the bot directory to Python path
bot_dir = Path(__file__).parent


# Import bot modules

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(bot_dir, 'data', 'bot.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GotLockzBot(commands.Bot):
    """Enhanced Discord bot with betting commands and AI integration."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

        # Load configuration
        self.config = load_config()

        # Set channel IDs from config
        self.vip_channel_id = self.config.get('VIP_CHANNEL_ID')
        self.free_channel_id = self.config.get('FREE_CHANNEL_ID')
        self.lotto_channel_id = self.config.get('LOTTO_CHANNEL_ID')

        # Track start time
        self.start_time = datetime.now()

        logger.info("Bot initialized with configuration loaded")

    async def setup_hook(self):
        """Set up bot commands and extensions."""
        try:
            # Add command groups
            self.tree.add_command(BettingCommands(self))
            self.tree.add_command(InfoCommands(self))

            logger.info("Command groups loaded successfully")

        except Exception as e:
            logger.error(f"Error setting up bot: {e}")
            raise

    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f"Bot is ready! Logged in as {self.user}")
        logger.info(f"Connected to {len(self.guilds)} guilds")

        # Sync commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Error syncing commands: {e}")

    async def on_command_error(self, ctx, error):
        """Global error handler."""
        if isinstance(error, commands.CommandNotFound):
            return

        logger.error(f"Command error: {error}")

        # Send user-friendly error message
        error_msg = "❌ An error occurred while processing your command. Please try again."
        if isinstance(error, commands.MissingPermissions):
            error_msg = "❌ You don't have permission to use this command."
        elif isinstance(error, commands.BotMissingPermissions):
            error_msg = "❌ I don't have the required permissions to execute this command."

        try:
            await ctx.send(error_msg, ephemeral=True)
        except BaseException:
            pass


async def main():
    """Main entry point."""
    try:
        # Create bot instance
        bot = GotLockzBot()

        # Get token from environment
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            logger.error("DISCORD_TOKEN not found in environment variables")
            sys.exit(1)
        token = str(token)

        # Run bot
        logger.info("Starting GotLockz Discord Bot...")
        await bot.start(token)

    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
