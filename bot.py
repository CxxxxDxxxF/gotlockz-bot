# bot.py

import os
import json
import asyncio
from io import BytesIO

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import pytesseract
from PIL import Image
import openai
import statsapi as mlb  # use statsapi.rename mlb-statsapi install

# Load environment variables
load_dotenv()
DISCORD_TOKEN        = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY       = os.getenv("OPENAI_API_KEY")
FREE_PLAY_CHANNEL_ID = int(os.getenv("FREE_PLAY_CHANNEL_ID", 0))
VIP_PLAY_CHANNEL_ID  = int(os.getenv("VIP_PLAY_CHANNEL_ID", 0))
openai.api_key       = OPENAI_API_KEY

# JSON storage helpers
STORAGE_PATH = "storage.json"
def load_storage():
    if not os.path.exists(STORAGE_PATH):
        return {}
    with open(STORAGE_PATH, "r") as f:
        return json.load(f)

def save_storage(data):
    with open(STORAGE_PATH, "w") as f:
        json.dump(data, f, indent=2)

storage = load_storage()

# Bot subclass with proper command tree setup
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # sync all slash commands
        await self.tree.sync()

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Legacy prefix command
@bot.command(name="postpick")
async def postpick_prefix(ctx, units: float, channel: str):
    attachment = ctx.message.attachments[0]
    img_data = await attachment.read()
    img = Image.open(BytesIO(img_data))
    text = pytesseract.image_to_string(img)

    entry_id = len(storage.get("plays", [])) + 1
    storage.setdefault("plays", []).append({
        "id": entry_id,
        "text": text,
        "units": units,
        "channel": channel,
        "timestamp": ctx.message.created_at.isoformat()
    })
    save_storage(storage)

    await ctx.send(f"Processed pick #{entry_id}: ```{text}```")

# Slash command version
@bot.tree.command(
    name="postpick",
    description="OCR a bet slip image and log your pick"
)
@app_commands.describe(
    units="Units to stake",
    channel="Destination channel name",
    file="Your bet slip image file"
)
async def postpick_slash(
    interaction: discord.Interaction,
    units: float,
    channel: str,
    file: discord.Attachment
):
    await interaction.response.defer()
    img_data = await file.read()
    img = Image.open(BytesIO(img_data))
    text = pytesseract.image_to_string(img)

    entry_id = len(storage.get("plays", [])) + 1
    storage.setdefault("plays", []).append({
        "id": entry_id,
        "text": text,
        "units": units,
        "channel": channel,
        "timestamp": interaction.created_at.isoformat()
    })
    save_storage(storage)

    await interaction.followup.send(f"✅ Processed pick #{entry_id}: ```{text}```")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
