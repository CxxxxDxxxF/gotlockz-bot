#!/usr/bin/env python3
"""
test_commands.py

Simple test script to verify Discord commands are working.
"""
import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

# Set up basic bot for testing
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.tree.command(name="test", description="Test command")
async def test_command(interaction: discord.Interaction):
    """Test command to verify slash commands work."""
    await interaction.response.send_message("✅ Test command working!")

@bot.tree.command(name="ping", description="Test bot responsiveness")
async def ping_command(interaction: discord.Interaction):
    """Test bot responsiveness."""
    await interaction.response.send_message("🏓 Pong! Bot is online!")

async def main():
    """Main test function."""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ DISCORD_TOKEN environment variable not set!")
        return
    
    print("🚀 Starting test bot...")
    
    try:
        await bot.start(token)
    except Exception as e:
        print(f"❌ Bot failed to start: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 