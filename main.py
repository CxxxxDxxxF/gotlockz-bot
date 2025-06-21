# main.py

#!/usr/bin/env python3
"""
main.py

Main entry point for the GotLockz Discord bot.
Handles startup, shutdown, and signal handling.
"""
import asyncio
import signal
import sys
import logging
from pathlib import Path

from bot import GotLockzBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)


async def main():
    """Main entry point."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        logger.error("❌ .env file not found!")
        logger.error("Please copy .env.example to .env and fill in your configuration.")
        sys.exit(1)
    
    # Create bot instance
    bot = GotLockzBot()
    
    try:
        logger.info("🚀 Starting GotLockz bot...")
        await bot.start(bot.token)
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.exception("Fatal error in main")
        sys.exit(1)
    finally:
        logger.info("Shutting down bot...")
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
