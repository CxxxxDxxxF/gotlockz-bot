import os
import logging
from dotenv import load_dotenv

# Load local .env file
load_dotenv()

from config import settings
from gotlockz_bot import bot

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s:%(name)s: %(message)s')

if __name__ == "__main__":
    if not settings.discord_token:
        logging.error("DISCORD_TOKEN not set.")
        exit(1)
    bot.run(settings.discord_token)
