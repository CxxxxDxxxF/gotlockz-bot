from discord.ext import commands
from mlbstatsapi import MLBStatsAPI  # Use mlbstatsapi for primary data
from pybaseball import playerid_lookup  # pybaseball as additional source

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")