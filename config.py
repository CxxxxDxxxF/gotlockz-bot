# config.py

"""
Centralized configuration management.
Loads environment variables from a .env file and sets them as constants.
"""
import os
import logging
from dotenv import load_dotenv

# Load .env file
load_dotenv()
logger = logging.getLogger(__name__)

def get_env_var(name: str, default: str = "", required: bool = False) -> str:
    """Gets an environment variable or returns a default."""
    var = os.getenv(name)
    if var is None or var == "":
        if required:
            logger.error(f"{name} environment variable not set.")
            raise ValueError(f"Missing required environment variable: {name}")
        return default
    return var

# --- Bot Credentials & IDs ---
try:
    DISCORD_TOKEN = get_env_var("DISCORD_TOKEN", required=True)
except ValueError:
    DISCORD_TOKEN = ""

try:
    GUILD_ID = int(get_env_var("GUILD_ID", default="0"))
except ValueError:
    GUILD_ID = 0

try:
    OWNER_ID = int(get_env_var("OWNER_ID", default="0"))
except ValueError:
    OWNER_ID = 0

# --- Channel IDs ---
try:
    ANALYSIS_CHANNEL_ID = int(get_env_var("ANALYSIS_CHANNEL_ID", default="0"))
except ValueError:
    ANALYSIS_CHANNEL_ID = 0

try:
    VIP_CHANNEL_ID = int(get_env_var("VIP_CHANNEL_ID", default="0"))
except ValueError:
    VIP_CHANNEL_ID = 0

try:
    LOTTO_CHANNEL_ID = int(get_env_var("LOTTO_CHANNEL_ID", default="0"))
except ValueError:
    LOTTO_CHANNEL_ID = 0

try:
    FREE_CHANNEL_ID = int(get_env_var("FREE_CHANNEL_ID", default="0"))
except ValueError:
    FREE_CHANNEL_ID = 0

# --- API Keys ---
OPENAI_API_KEY = get_env_var("OPENAI_API_KEY", default="")

# --- AI Analysis Tuning ---
OPENAI_MODEL = get_env_var("OPENAI_MODEL", default="gpt-4")
ANALYSIS_TEMPERATURE = float(get_env_var("ANALYSIS_TEMPERATURE", default="0.7"))

# --- File Paths ---
COUNTER_FILE = get_env_var("COUNTER_FILE", default="counters.json")
LOG_FILE = get_env_var("LOG_FILE", default="gotlockz-bot.log")

# --- Google Sheets (for /history command) ---
GOOGLE_CREDENTIALS_PATH = get_env_var("GOOGLE_CREDENTIALS_PATH", default="gcreds.json")
GOOGLE_SHEET_NAME = get_env_var("GOOGLE_SHEET_NAME", default="GotLockz Picks")
