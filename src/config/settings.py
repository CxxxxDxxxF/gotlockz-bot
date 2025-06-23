"""
Configuration settings for GotLockz Bot V2.
"""
import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


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
    
    def validate(self) -> bool:
        """Validate required settings."""
        if not self.bot.token:
            raise ValueError("DISCORD_TOKEN is required")
        if not self.api.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        return True


# Global settings instance
settings = Settings() 