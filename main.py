# main.py

#!/usr/bin/env python3
"""
main.py

Main entry point for the GotLockz Discord bot.
Handles startup, shutdown, and signal handling.
"""
import os
import asyncio
from bot import GotLockzBot

def main():
    # Get bot token from environment
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ DISCORD_TOKEN environment variable not set!")
        return
    
    # Create and run bot
    bot = GotLockzBot()
    
    try:
        print("🚀 Starting GotLockz Bot...")
        bot.run(token)
    except Exception as e:
        print(f"❌ Bot failed to start: {e}")

if __name__ == "__main__":
    main()
