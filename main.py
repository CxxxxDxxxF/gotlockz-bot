# main.py

#!/usr/bin/env python3
"""
main.py

Main entry point for the GotLockz Discord bot.
Handles startup, shutdown, and signal handling.
"""
import os
import logging
from bot import GotLockzBot

def main():
    logging.basicConfig(level=logging.INFO)
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN environment variable not set!")
        print("Please set your Discord bot token as an environment variable.")
        return
    
    bot = GotLockzBot()
    print("🚀 Starting GotLockz bot...")
    bot.run(token)

if __name__ == "__main__":
    main()
