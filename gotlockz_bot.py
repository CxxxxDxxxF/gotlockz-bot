import discord
from discord.ext import commands
from mlb_statsapi import MLBStatsAPI

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
