#!/usr/bin/env python3
"""
info.py - Information and Utility Commands

Bot status, statistics, and utility commands.
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
from datetime import datetime
import os
import platform
import psutil
import json

logger = logging.getLogger(__name__)


class InfoCommands(app_commands.Group):
    """Information and utility commands."""

    def __init__(self, bot):
        super().__init__(name="info", description="Bot information and utilities")
        self.bot = bot

    @app_commands.command(name="ping", description="Test bot responsiveness")
    async def ping_command(self, interaction: discord.Interaction):
        """Test bot responsiveness."""
        try:
            latency = round(self.bot.latency * 1000)
            await interaction.response.send_message(
                f"🏓 Pong! Latency: {latency}ms",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in ping command: {e}")
            await interaction.response.send_message(
                "❌ Error testing bot responsiveness",
                ephemeral=True
            )

    @app_commands.command(name="status", description="Check bot status")
    async def status_command(self, interaction: discord.Interaction):
        """Check bot status and system information."""
        try:
            # Get system info
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Get bot info
            uptime = datetime.now() - self.bot.start_time if hasattr(self.bot,
                                                                     'start_time') else 'Unknown'
            guild_count = len(self.bot.guilds)

            status_msg = f"""🤖 **Bot Status**

**System:**
• CPU Usage: {cpu_percent}%
• Memory: {memory.percent}% used
• Disk: {disk.percent}% used

**Bot:**
• Guilds: {guild_count}
• Latency: {round(self.bot.latency * 1000)}ms
• Python: {platform.python_version()}
• Discord.py: {discord.__version__}"""

            await interaction.response.send_message(status_msg, ephemeral=True)

        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await interaction.response.send_message(
                "❌ Error retrieving bot status",
                ephemeral=True
            )

    @app_commands.command(name="stats", description="View bot statistics")
    async def stats_command(self, interaction: discord.Interaction):
        """View bot usage statistics."""
        try:
            # Load pick counters
            counter_file = os.path.join(
                os.path.dirname(__file__), '..', 'data', 'pick_counters.json')
            if os.path.exists(counter_file):
                with open(counter_file, 'r') as f:
                    counters = json.load(f)
            else:
                counters = {"vip": 0, "free": 0, "lotto": 0}

            stats_msg = f"""📊 **Bot Statistics**

**Pick Counters:**
• VIP Picks: {counters.get('vip', 0)}
• Free Picks: {counters.get('free', 0)}
• Lotto Picks: {counters.get('lotto', 0)}
• **Total:** {sum(counters.values())}

**Commands Available:**
• `/betting postpick` - Post a pick with custom units and channel
• `/info ping` - Test responsiveness
• `/info status` - Check bot status
• `/info stats` - View statistics"""

            await interaction.response.send_message(stats_msg, ephemeral=True)

        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            await interaction.response.send_message(
                "❌ Error retrieving bot statistics",
                ephemeral=True
            )

    @app_commands.command(name="force_sync",
                          description="Force sync all commands")
    async def force_sync_command(self, interaction: discord.Interaction):
        """Force sync all slash commands."""
        try:
            # Check if user has admin permissions
            if not interaction.guild:
                await interaction.response.send_message(
                    "❌ This command can only be used in a server.",
                    ephemeral=True
                )
                return
                
            member = interaction.guild.get_member(interaction.user.id)
            if not member or not member.guild_permissions.administrator:
                await interaction.response.send_message(
                    "❌ You need administrator permissions to use this command.",
                    ephemeral=True
                )
                return

            # Sync commands
            synced = await self.bot.tree.sync()

            await interaction.response.send_message(
                f"✅ Successfully synced {len(synced)} command(s)!",
                ephemeral=True
            )

        except Exception as e:
            logger.error(f"Error in force_sync command: {e}")
            await interaction.response.send_message(
                "❌ Error syncing commands",
                ephemeral=True
            )


async def setup(bot):
    """Set up the info commands cog."""
    await bot.add_cog(InfoCommands(bot))
