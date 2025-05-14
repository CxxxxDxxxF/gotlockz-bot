
# main.py
import os
from gotlockz_bot import bot

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if token is None:
        raise ValueError("DISCORD_TOKEN environment variable is not set. Please set it in the Secrets tab.")
    bot.run(token)
