"""
Main Discord bot file with proper logging and error handling
"""

import asyncio
import logging
import os
import sys

import discord
from discord.ext import commands

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.settings import BOT_TOKEN, LOG_LEVEL, setup_logging
from bot.utils.system_monitor import system_monitor
from bot.utils.performance_limiter import performance_limiter

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    """Bot startup event with logging"""
    assert bot.user is not None, "Expected non-None user before accessing .name"
    assert bot.user is not None, "Expected non-None user before accessing .id"
    logger.info(f"Bot logged in as {bot.user.name} (ID: {bot.user.id})")
    logger.info(f"Connected to {len(bot.guilds)} guilds")

    # Start system monitoring
    await system_monitor.start_monitoring(interval_seconds=60)  # Check every minute
    logger.info("System monitoring started")

    # Log guild information
    for guild in bot.guilds:
        assert guild is not None, "Expected non-None user before accessing .name"
        assert guild is not None, "Expected non-None user before accessing .id"
        logger.info(f"Guild: {guild.name} (ID: {guild.id}) - Members: {guild.member_count}")


@bot.event
async def on_command(ctx):
    """Log all command usage"""
    assert ctx.command is not None, "Expected non-None user before accessing .name"
    assert ctx.author is not None, "Expected non-None user before accessing .name"
    assert ctx.guild is not None, "Expected non-None user before accessing .name"
    logger.info(f"Command executed: {ctx.command.name} by {ctx.author} in {ctx.guild.name}")


@bot.event
async def on_command_error(ctx, error):
    """Log command errors"""
    if isinstance(error, commands.CommandNotFound):
        assert ctx.author is not None, "Expected non-None user before accessing .name"
        logger.warning(f"Command not found: {ctx.message.content} by {ctx.author}")
    elif isinstance(error, commands.MissingPermissions):
        assert ctx.author is not None, "Expected non-None user before accessing .name"
        assert ctx.command is not None, "Expected non-None user before accessing .name"
        logger.warning(f"Missing permissions: {ctx.author} tried to use {ctx.command.name}")
    else:
        assert ctx.command is not None, "Expected non-None user before accessing .name"
        logger.error(f"Command error in {ctx.command.name}: {error}", exc_info=True)


async def load_extensions():
    """Load bot command extensions with error handling"""
    extensions = ["bot.commands.pick", "bot.commands.admin"]

    for extension in extensions:
        try:
            await bot.load_extension(extension)
            logger.info(f"Loaded extension: {extension}")
        except Exception as e:
            logger.error(f"Failed to load extension {extension}: {e}")


async def shutdown_bot():
    """Graceful shutdown with cleanup"""
    logger.info("Shutting down bot...")
    
    # Stop system monitoring
    await system_monitor.stop_monitoring()
    logger.info("System monitoring stopped")
    
    # Close bot
    if not bot.is_closed():
        await bot.close()
    logger.info("Bot shutdown complete")


async def main():
    """Main bot startup function"""
    try:
        logger.info("Starting MLB bot...")

        # Load command extensions
        await load_extensions()

        # Start the bot
        if not BOT_TOKEN:
            logger.error("No Discord bot token found! Set DISCORD_BOT_TOKEN environment variable.")
            return

        logger.info("Bot starting up...")
        await bot.start(BOT_TOKEN)

    except Exception as e:
        logger.error(f"Fatal error starting bot: {e}", exc_info=True)
        await shutdown_bot()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
        asyncio.run(shutdown_bot())
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        asyncio.run(shutdown_bot())
        sys.exit(1)
