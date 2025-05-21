import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from utils import storage, analysis
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

class Settings(BaseSettings):
    discord_token: str
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

load_dotenv()
config = Settings()

import openai
openai.api_key = config.openai_api_key

intents = discord.Intents.default()
bot = commands.Bot(intents=intents, command_prefix="!", help_command=None)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands. Ready as {bot.user}.")
    except Exception as e:
        print(f"Sync error: {e}")

@bot.tree.command(name="postpick", description="Analyze a betting pick from image")
@app_commands.describe(units="Units to wager", channel="Channel to post", image="Bet slip image")
async def postpick(interaction: discord.Interaction, units: float, channel: discord.TextChannel, image: discord.Attachment):
    await interaction.response.defer(thinking=True, ephemeral=True)
    if not image.content_type or not image.content_type.startswith("image"):
        await interaction.followup.send("Attach a valid image.", ephemeral=True)
        return
    img_bytes = await image.read()
    try:
        ocr = analysis.extract_text_from_image(img_bytes)
    except Exception:
        await interaction.followup.send("OCR failed.", ephemeral=True)
        return
    if not ocr.strip():
        await interaction.followup.send("No text found.", ephemeral=True)
        return
    desc, teams = analysis.parse_pick_text(ocr)
    try:
        analysis_msg = await analysis.generate_analysis_message(desc, teams, config.openai_model)
    except Exception as e:
        await interaction.followup.send(f"Analysis error: {e}", ephemeral=True)
        return
    try:
        await channel.send(f"**Pick Analysis:** {analysis_msg}")
    except Exception:
        await interaction.followup.send(f"Cannot post in {channel.mention}", ephemeral=True)
        return
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    record = {"pick_text": desc, "units": units, "channel": channel.id, "timestamp": ts}
    await storage.add_pick(record)
    await interaction.followup.send(f"✅ Posted to {channel.mention}", ephemeral=True)

@bot.tree.command(name="history", description="Show pick history")
async def history(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)
    data = await storage.get_all_picks()
    if not data:
        await interaction.followup.send("No picks logged.", ephemeral=True)
        return
    lines = []
    for e in data:
        ts = e["timestamp"]
        if ts.endswith("+00:00"):
            ts = ts[:-6] + "Z"
        lines.append(f"- {ts} | {e['units']}u | {e['pick_text']} <#{e['channel']}>")
    msg = "**History:**
" + "
".join(lines[-50:])
    await interaction.followup.send(msg, ephemeral=True)

if __name__ == "__main__":
    bot.run(config.discord_token)
