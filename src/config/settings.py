"""
Configuration settings for GotLockz Bot V2.
"""
import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


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
    vip_header: str = "**VIP PICK**"
    lotto_header: str = "**LOTTO TICKET**"
    
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
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )
        
        self.api = APIConfig(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4")
        )
        
        self.channels = ChannelConfig(
            vip_channel_id=int(os.getenv("VIP_CHANNEL_ID", "0")) if os.getenv("VIP_CHANNEL_ID") else None,
            free_channel_id=int(os.getenv("FREE_CHANNEL_ID", "0")) if os.getenv("FREE_CHANNEL_ID") else None,
            lotto_channel_id=int(os.getenv("LOTTO_CHANNEL_ID", "0")) if os.getenv("LOTTO_CHANNEL_ID") else None
        )
        
        self.templates = TemplateConfig()
    
    def validate(self) -> bool:
        """Validate required settings."""
        if not self.bot.token:
            raise ValueError("DISCORD_TOKEN is required")
        # OpenAI API key is optional - bot can work without AI analysis
        if not self.api.openai_api_key:
            logger.warning("OPENAI_API_KEY not configured - AI analysis will be disabled")
        return True


# Global settings instance
settings = Settings() 