"""
Configuration settings for GotLockz Bot V2.
"""

import logging
import logging.handlers
import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Bot Configuration
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# MLB API Configuration
MLB_BASE_URL = "https://statsapi.mlb.com/api/v1"
MLB_TIMEOUT = 15

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Performance Configuration
CACHE_TIMEOUT = 300  # 5 minutes
REQUEST_TIMEOUT = 15  # seconds

# Feature Flags
ENABLE_WEATHER_ANALYSIS = os.getenv("ENABLE_WEATHER_ANALYSIS", "true").lower() == "true"
ENABLE_PLAYER_ANALYTICS = os.getenv("ENABLE_PLAYER_ANALYTICS", "true").lower() == "true"
ENABLE_REAL_TIME_UPDATES = os.getenv("ENABLE_REAL_TIME_UPDATES", "true").lower() == "true"


def setup_logging():
    """Setup logging configuration for the bot (console only - free)"""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),  # Console output (free)
        ],
    )

    # Set specific loggers
    loggers = [
        "bot.services.mlb_scraper",
        "bot.services.player_analytics",
        "bot.services.weather_impact",
        "bot.commands.pick",
        "bot.main",
    ]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, LOG_LEVEL))

    # Log startup info
    logger = logging.getLogger(__name__)
    logger.info(f"Bot logging initialized at level: {LOG_LEVEL}")
    logger.info(
        f"Features enabled - Weather: {ENABLE_WEATHER_ANALYSIS}, Player Analytics: {ENABLE_PLAYER_ANALYTICS}, Real-time: {ENABLE_REAL_TIME_UPDATES}"
    )
    logger.info("Using free console logging - view logs in Render dashboard")


@dataclass
class BotConfig:
    """Bot configuration settings."""

    token: str
    guild_id: Optional[int] = None
    environment: str = "development"
    log_level: str = "INFO"


@dataclass
class APIConfig:
    """API configuration settings."""

    openai_api_key: str
    openai_model: str = "gpt-4"


@dataclass
class ChannelConfig:
    """Channel configuration settings."""

    vip_channel_id: Optional[int] = None
    free_channel_id: Optional[int] = None
    lotto_channel_id: Optional[int] = None


@dataclass
class TemplateConfig:
    """Template configuration for different pick types."""

    free_play_header: str = "**FREE PLAY**"
    vip_header: str = "**VIP PLAY**"
    lotto_header: str = "**LOTTO TICKET**"

    # VIP-specific styling
    vip_emoji: str = "👑"
    vip_diamond: str = "💎"
    vip_units_emoji: str = "💰"
    vip_matchup_emoji: str = "⚾"
    vip_selection_emoji: str = "🎯"
    vip_stats_emoji: str = "📊"
    vip_analysis_emoji: str = "🔍"

    # Template placeholders
    date_format: str = "%m/%d/%y"
    time_format: str = "%I:%M %p EST"


class Settings:
    """Main settings class."""

    def __init__(self):
        self.bot = BotConfig(
            token=os.getenv("DISCORD_TOKEN", ""),
            guild_id=int(os.getenv("GUILD_ID", "0")) if os.getenv("GUILD_ID") else None,
            environment=os.getenv("ENVIRONMENT", "development"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

        self.api = APIConfig(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""), openai_model=os.getenv("OPENAI_MODEL", "gpt-4")
        )

        self.channels = ChannelConfig(
            vip_channel_id=int(os.getenv("VIP_CHANNEL_ID", "0")) if os.getenv("VIP_CHANNEL_ID") else None,
            free_channel_id=int(os.getenv("FREE_CHANNEL_ID", "0")) if os.getenv("FREE_CHANNEL_ID") else None,
            lotto_channel_id=int(os.getenv("LOTTO_CHANNEL_ID", "0")) if os.getenv("LOTTO_CHANNEL_ID") else None,
        )

        self.templates = TemplateConfig()

    def validate(self) -> bool:
        """Validate required settings."""
        if not self.bot.token:
            raise ValueError("DISCORD_TOKEN is required")
        if not self.api.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        return True


# Global settings instance
settings = Settings()
