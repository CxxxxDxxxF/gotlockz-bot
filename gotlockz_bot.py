import os
import base64
import logging

# Inject credentials.json from environment variables
creds_raw = os.getenv("GOOGLE_SHEETS_CREDS")
creds_b64 = os.getenv("GOOGLE_SHEETS_CREDS_B64")
if creds_raw:
    with open("credentials.json", "w") as f:
        f.write(creds_raw)
elif creds_b64:
    with open("credentials.json", "wb") as f:
        f.write(base64.b64decode(creds_b64))

logger = logging.getLogger(__name__)

import discord
from discord.ext import commands
from utils.sheets import init_sheets, log_pick, get_play_number
from utils.ocr import extract_text

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")
    try:
        init_sheets()
    except Exception:
        logger.exception("Failed to initialize Google Sheets")

@bot.command(name="postpick")
async def postpick(ctx, units: float, channel_name: str):
    logger.info(f"Received postpick: units={units}, channel={channel_name}")
    try:
        play_type = "VIP" if channel_name.lower().startswith("vip") else "Free"
        entry_number = get_play_number(play_type)
        entry = {
            "type": play_type,
            "number": entry_number,
            "units": units,
        }
        log_pick(entry)
        await ctx.send(f"Logged {play_type} play #{entry_number}: {units} units")
    except Exception:
        logger.exception("Error handling postpick command")
        await ctx.send("Sorry, something went wrong logging your pick.")

@bot.command(name="health")
async def health(ctx):
    await ctx.send("Bot is running and connected!")
