# bot.py
import os
import json
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
import pytesseract
from PIL import Image
import openai
import statsapi as mlb

# Load .env in local/dev
load_dotenv()

# Environment variables
DISCORD_TOKEN        = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY       = os.getenv("OPENAI_API_KEY")
FREE_PLAY_CHANNEL_ID = int(os.getenv("FREE_PLAY_CHANNEL_ID", 0))
VIP_PLAY_CHANNEL_ID  = int(os.getenv("VIP_PLAY_CHANNEL_ID", 0))

openai.api_key = OPENAI_API_KEY

# Simple JSON storage
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

# Set up Discord bot
bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command(name="postpick")
async def postpick(ctx, units: float, channel: str):
    # Assumes the user attaches an image; grab the first one
    attachment = ctx.message.attachments[0]
    img_data = await attachment.read()
    img = Image.open(io.BytesIO(img_data))

    # OCR it
    text = pytesseract.image_to_string(img)

    # (Your parsing logic here)
    # e.g. pick = parse_team(text)
    # formatted = build_message_text(pick, units, etc.)

    # Log in JSON
    entry_id = len(storage.get("plays", [])) + 1
    storage.setdefault("plays", []).append({
        "id": entry_id,
        "text": text,
        "units": units,
        "channel": channel,
        "timestamp": ctx.message.created_at.isoformat()
    })
    save_storage(storage)

    # Send back to Discord
    await ctx.send(f"Processed pick #{entry_id}: ```{text}```")

if __name__ == "__main__":
    # When running as a Background Worker:
    bot.run(DISCORD_TOKEN)

    # If you must deploy as a Web Service, uncomment the block below
    # and change your Docker CMD to: ["python", "bot.py"]
    #
    # from aiohttp import web
    #
    # async def health(request):
    #     return web.Response(text="OK")
    #
    # app = web.Application()
    # app.add_routes([web.get("/", health)])
    #
    # async def main():
    #     discord_task = asyncio.create_task(bot.start(DISCORD_TOKEN))
    #     web_task     = asyncio.create_task(web._run_app(app, port=int(os.getenv("PORT", 5000))))
    #     await asyncio.gather(discord_task, web_task)
    #
    # asyncio.run(main())
    bot.run(config.discord_token)

