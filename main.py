# main.py

#!/usr/bin/env python3
"""
main.py - GotLockz Discord Bot

Professional Discord bot for betting analysis and pick management.
"""
import os
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the bot."""
    # Get bot token from environment
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("❌ DISCORD_TOKEN environment variable not set!")
        logger.error("Please set your Discord bot token in the environment variables.")
        return
    
    # Import bot class
    try:
        from bot import GotLockzBot
    except ImportError as e:
        logger.error(f"❌ Failed to import bot: {e}")
        return
    
    # Create and run bot
    try:
        logger.info("🚀 Starting GotLockz Bot...")
        bot = GotLockzBot()
        bot.run(token, log_handler=None)
    except Exception as e:
        logger.error(f"❌ Bot failed to start: {e}")
        raise

if __name__ == "__main__":
    main()
