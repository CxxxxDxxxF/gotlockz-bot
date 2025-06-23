"""
GotLockz Bot V2 - Main Entry Point
"""
import asyncio
import logging
import sys
from pathlib import Path

import discord
from discord.ext import commands

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import settings
from bot.commands.pick import PickCommands
from bot.commands.admin import AdminCommands

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.bot.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GotLockzBot(commands.Bot):
    """Main bot class for GotLockz V2."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        
        self.settings = settings
        self.start_time = None
        logger.info("Bot initialized")
    
    async def setup_hook(self):
        """Set up bot commands and extensions."""
        try:
            # Add command groups
            self.tree.add_command(PickCommands(self))
            self.tree.add_command(AdminCommands(self))
            
            logger.info("Commands loaded successfully")
            
        except Exception as e:
            logger.error(f"Error setting up bot: {e}")
            raise
    
    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f"Bot is ready! Logged in as {self.user}")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        
        # Set start time
        self.start_time = asyncio.get_event_loop().time()
        
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
        
        error_msg = "❌ An error occurred while processing your command. Please try again."
        if isinstance(error, commands.MissingPermissions):
            error_msg = "❌ You don't have permission to use this command."
        elif isinstance(error, commands.BotMissingPermissions):
            error_msg = "❌ I don't have the required permissions to execute this command."
        
        try:
            await ctx.send(error_msg, ephemeral=True)
        except Exception:
            pass


async def main():
    """Main entry point."""
    try:
        # Validate settings
        settings.validate()
        
        # Create and start bot
        bot = GotLockzBot()
        logger.info("Starting GotLockz Bot V2...")
        
        await bot.start(settings.bot.token)
        
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 