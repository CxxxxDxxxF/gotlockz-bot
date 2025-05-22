import os
import json
import asyncio
import io
import discord
from discord.ext import commands
from dotenv import load_dotenv
import pytesseract
from PIL import Image
import openai
import statsapi as mlb

load_dotenv()

DISCORD_TOKEN        = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY       = os.getenv("OPENAI_API_KEY")
FREE_PLAY_CHANNEL_ID = int(os.getenv("FREE_PLAY_CHANNEL_ID", 0))
VIP_PLAY_CHANNEL_ID  = int(os.getenv("VIP_PLAY_CHANNEL_ID", 0))

openai.api_key = OPENAI_API_KEY

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

# Set up Discord bot with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command(name="postpick")
async def postpick(ctx, units: float, channel: str):
    attachment = ctx.message.attachments[0]
    img_data = await attachment.read()
    img = Image.open(io.BytesIO(img_data))
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

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)

