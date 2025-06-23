"""
GotLockz Bot V2 - Main Entry Point with Health API
"""
import asyncio
import logging
import sys
import threading
from pathlib import Path

import uvicorn
from fastapi import FastAPI

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.settings import settings
from src.bot.main import GotLockzBot
from src.api.health import app as health_app, set_bot_instance

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


def run_health_api():
    """Run the health check API server."""
    uvicorn.run(
        health_app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


async def main():
    """Main entry point."""
    try:
        # Validate settings
        settings.validate()
        logger.info("Settings validated successfully")
        
        # Create bot instance
        bot = GotLockzBot()
        bot.start_time = asyncio.get_event_loop().time()
        
        # Set bot instance for health checks
        set_bot_instance(bot)
        logger.info("Bot instance set for health checks")
        
        # Start health API in separate thread
        health_thread = threading.Thread(target=run_health_api, daemon=True)
        health_thread.start()
        logger.info("Health API server started")
        
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