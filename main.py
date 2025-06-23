"""
GotLockz Bot V2 - Main Entry Point
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.settings import settings
from src.bot.main import GotLockzBot

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


async def main():
    """Main entry point."""
    try:
        # Validate settings
        settings.validate()
        logger.info("Settings validated successfully")
        
        # Create bot instance
        bot = GotLockzBot()
        
        # Start bot
        logger.info("Starting GotLockz Bot V2...")
        await bot.start(settings.bot.token)
        
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 