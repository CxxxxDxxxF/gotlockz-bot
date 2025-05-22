# bot.py (Version 7)

import os
import json
import asyncio
from io import BytesIO

import discord
from discord import app_commands, TextChannel
from discord.ext import commands
from dotenv import load_dotenv
import pytesseract
from PIL import Image
import openai
import statsapi as mlb  # pip install mlb-statsapi>=1.9.0

# Load configuration from environment
load_dotenv()
DISCORD_TOKEN        = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY       = os.getenv("OPENAI_API_KEY")
FREE_PLAY_CHANNEL_ID = int(os.getenv("FREE_PLAY_CHANNEL_ID", 0))
VIP_PLAY_CHANNEL_ID  = int(os.getenv("VIP_PLAY_CHANNEL_ID", 0))
openai.api_key       = OPENAI_API_KEY

# Persistent JSON storage
STORAGE_PATH = "storage.json"

def load_storage() -> dict:
    if not os.path.exists(STORAGE_PATH):
        return {}
    with open(STORAGE_PATH, "r") as f:
        return json.load(f)

def save_storage(data: dict) -> None:
    with open(STORAGE_PATH, "w") as f:
        json.dump(data, f, indent=2)

storage = load_storage()

# Bot subclass to handle slash command sync
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Sync slash commands with Discord
        await self.tree.sync()

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (Ready)")

# == PREFIX COMMAND ==
@bot.command(name="postpick")
async def postpick_prefix(ctx: commands.Context, units: float, channel: TextChannel):
    """
    !postpick <units> #channel [attached image]
    - OCRs the attached bet slip image
    - Logs the pick to storage.json
    - Posts the OCR result into the specified channel
    """
    if not ctx.message.attachments:
        return await ctx.send("❌ Please attach an image of your bet slip.")
    attachment = ctx.message.attachments[0]
    img_data = await attachment.read()
    img = Image.open(BytesIO(img_data))
    text = pytesseract.image_to_string(img)

    entry_id = len(storage.get("plays", [])) + 1
    storage.setdefault("plays", []).append({
        "id": entry_id,
        "text": text.strip(),
        "units": units,
        "channel_id": channel.id,
        "timestamp": ctx.message.created_at.isoformat()
    })
    save_storage(storage)

    await channel.send(f"✅ Processed pick #{entry_id}: ```{text.strip()}```")
    await ctx.send(f"Your pick #{entry_id} has been posted to {channel.mention}.")

# == SLASH COMMAND ==
@bot.tree.command(
    name="postpick",
    description="OCR a bet slip image and log your pick"
)
@app_commands.describe(
    units="Units to stake",
    channel="Channel to post the result in",
    file="Upload your bet slip image here"
)
async def postpick_slash(
    interaction: discord.Interaction,
    units: float,
    channel: TextChannel,
    file: discord.Attachment
):
    """
    /postpick units:<float> channel:<#channel> file:<attachment>
    - OCRs the uploaded bet slip
    - Logs the pick
    - Posts the result into the chosen channel
    """
    await interaction.response.defer()

    img_data = await file.read()
    img = Image.open(BytesIO(img_data))
    text = pytesseract.image_to_string(img)

    entry_id = len(storage.get("plays", [])) + 1
    storage.setdefault("plays", []).append({
        "id": entry_id,
        "text": text.strip(),
        "units": units,
        "channel_id": channel.id,
        "timestamp": interaction.created_at.isoformat()
    })
    save_storage(storage)

    await channel.send(f"✅ Processed pick #{entry_id}: ```{text.strip()}```")
    await interaction.followup.send(f"Your pick #{entry_id} has been posted to {channel.mention}.")

# == ENTRYPOINT ==
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
