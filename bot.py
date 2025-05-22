import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
from utils.ocr_parser import extract_bet_info
from utils.mlb_stats import get_game_stats
from utils.gpt_analysis import generate_analysis
from utils.utils import format_message

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)
tree = app_commands.CommandTree(bot)

@tree.command(name="postpick")
@app_commands.describe(units="Unit size", channel="Target channel")
async def postpick(interaction: discord.Interaction, units: float, channel: discord.TextChannel):
    await interaction.response.defer()

    if not interaction.attachments:
        await interaction.followup.send("Please attach a bet slip image.")
        return

    image = interaction.attachments[0]
    image_path = f"temp_{interaction.id}.jpg"
    await image.save(image_path)

    try:
        bet_info = extract_bet_info(image_path)
        game_stats = get_game_stats(bet_info)
        analysis = generate_analysis(bet_info, game_stats)
        message = format_message(bet_info, analysis, units)

        await channel.send(message)
        await channel.send(file=discord.File(image_path))
        await interaction.followup.send("Pick posted!")
    except Exception as e:
        await interaction.followup.send(f"Error processing pick: {str(e)}")
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Bot connected as {bot.user}")

bot.run(TOKEN)
