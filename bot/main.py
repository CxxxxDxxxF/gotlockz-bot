# main.py

#!/usr/bin/env python3
"""
main.py - GotLockz Discord Bot Entry Point

Simplified, reliable Discord bot with betting commands and OCR integration.
"""

from commands.info import InfoCommands
from commands.betting import BettingCommands
from config import load_config
from dotenv import load_dotenv
from discord.ext import commands
import discord
import asyncio
import logging
import os
from pathlib import Path
from datetime import datetime
import sys
from flask import Flask, jsonify
import threading

# Add the bot directory to Python path
bot_dir = Path(__file__).parent

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

# Create Flask app for health checks
app = Flask(__name__)

# Global bot reference for health checks
bot_instance = None

@app.route('/health')
def health_check():
    """Health check endpoint for Render deployment."""
    global bot_instance
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'bot_ready': bot_instance.is_ready() if bot_instance else False,
        'guild_count': len(bot_instance.guilds) if bot_instance else 0
    })

@app.route('/')
def root():
    """Root endpoint."""
    return jsonify({
        'message': 'GotLockz Bot is running',
        'status': 'online',
        'timestamp': datetime.now().isoformat()
    })

def run_flask():
    """Run Flask app in a separate thread."""
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

class GotLockzBot(commands.Bot):
    """Simplified Discord bot with betting commands."""

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
    global bot_instance
    
    try:
        # Create bot instance
        bot = GotLockzBot()
        bot_instance = bot  # Set global reference for health checks

        # Start Flask health check server in separate thread
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logger.info("Flask health check server started")

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
