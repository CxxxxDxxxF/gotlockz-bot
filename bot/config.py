#!/usr/bin/env python3
"""
config.py - Configuration Management

Load and manage environment variables and bot configuration.
"""

import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    # Load .env file if it exists
    load_dotenv()

    config = {
        'DISCORD_TOKEN': os.getenv('DISCORD_TOKEN'),
        'VIP_CHANNEL_ID': int(
            os.getenv(
                'VIP_CHANNEL_ID',
                0)) if os.getenv('VIP_CHANNEL_ID') else None,
        'FREE_CHANNEL_ID': int(
            os.getenv(
                'FREE_CHANNEL_ID',
                0)) if os.getenv('FREE_CHANNEL_ID') else None,
        'LOTTO_CHANNEL_ID': int(
            os.getenv(
                'LOTTO_CHANNEL_ID',
                0)) if os.getenv('LOTTO_CHANNEL_ID') else None,
        'LOG_LEVEL': os.getenv(
            'LOG_LEVEL',
            'INFO'),
        'ENVIRONMENT': os.getenv(
            'ENVIRONMENT',
            'development')}

    # Validate required config
    if not config['DISCORD_TOKEN']:
        logger.error("DISCORD_TOKEN is required but not set")
        raise ValueError("DISCORD_TOKEN environment variable is required")

    logger.info(
        f"Configuration loaded for environment: {config['ENVIRONMENT']}")
    return config


def get_channel_id(channel_name: str) -> Optional[int]:
    """Get channel ID by name."""
    config = load_config()
    return config.get(f'{channel_name.upper()}_CHANNEL_ID')


def is_production() -> bool:
    """Check if running in production environment."""
    return os.getenv('ENVIRONMENT', 'development').lower() == 'production'


# --- Bot Credentials & IDs ---
try:
    DISCORD_TOKEN = load_config()['DISCORD_TOKEN']
except ValueError:
    DISCORD_TOKEN = ""

try:
    GUILD_ID = int(load_config().get('GUILD_ID', '0'))
except ValueError:
    GUILD_ID = 0

try:
    OWNER_ID = int(load_config().get('OWNER_ID', '0'))
except ValueError:
    OWNER_ID = 0

# --- Channel IDs ---
try:
    ANALYSIS_CHANNEL_ID = int(load_config().get('ANALYSIS_CHANNEL_ID', '0'))
except ValueError:
    ANALYSIS_CHANNEL_ID = 0

try:
    VIP_CHANNEL_ID = load_config().get('VIP_CHANNEL_ID')
except ValueError:
    VIP_CHANNEL_ID = 0

try:
    LOTTO_CHANNEL_ID = load_config().get('LOTTO_CHANNEL_ID')
except ValueError:
    LOTTO_CHANNEL_ID = 0

try:
    FREE_CHANNEL_ID = load_config().get('FREE_CHANNEL_ID')
except ValueError:
    FREE_CHANNEL_ID = 0

# --- API Keys ---
OPENAI_API_KEY = load_config().get('OPENAI_API_KEY', '')

# --- AI Analysis Tuning ---
OPENAI_MODEL = load_config().get('OPENAI_MODEL', 'gpt-4')
ANALYSIS_TEMPERATURE = float(load_config().get('ANALYSIS_TEMPERATURE', '0.7'))

# --- File Paths ---
COUNTER_FILE = load_config().get('COUNTER_FILE', 'counters.json')
LOG_FILE = load_config().get('LOG_FILE', 'gotlockz-bot.log')

# --- Google Sheets (for /history command) ---
GOOGLE_CREDENTIALS_PATH = load_config().get(
    'GOOGLE_CREDENTIALS_PATH', 'gcreds.json')
GOOGLE_SHEET_NAME = load_config().get('GOOGLE_SHEET_NAME', 'GotLockz Picks')
