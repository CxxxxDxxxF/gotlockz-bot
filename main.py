import os
import discord
from dotenv import load_dotenv
from gotlockz_bot import bot

load_dotenv()

@bot.event
async def on_ready():
    print(f"✅ Bot is live as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

bot.run(os.getenv("DISCORD_TOKEN"))
