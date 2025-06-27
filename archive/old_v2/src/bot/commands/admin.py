"""
Admin Commands - Bot management and utilities
"""

import logging
import platform
from datetime import datetime

import discord
import psutil
from discord import app_commands

logger = logging.getLogger(__name__)


class AdminCommands(app_commands.Group):
    """Admin commands for bot management."""

    def __init__(self, bot):
        super().__init__(name="admin", description="Admin commands")
        self.bot = bot

    @app_commands.command(name="ping", description="Test bot responsiveness")
    async def ping(self, interaction: discord.Interaction):
        """Test bot responsiveness."""
        try:
            latency = round(self.bot.latency * 1000)
            await interaction.response.send_message(f"🏓 Pong! Latency: {latency}ms", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in ping command: {e}")
            await interaction.response.send_message("❌ Error testing bot responsiveness", ephemeral=True)

    @app_commands.command(name="status", description="Check bot status")
    async def status(self, interaction: discord.Interaction):
        """Check bot status and system information."""
        try:
            # Get system info
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Get bot info
            guild_count = len(self.bot.guilds)

            embed = discord.Embed(title="🤖 Bot Status", color=0x00FF00)

            embed.add_field(
                name="System",
                value=f"CPU: {cpu_percent}%\nMemory: {memory.percent}%\nDisk: {disk.percent}%",
                inline=True,
            )

            embed.add_field(
                name="Bot",
                value=f"Guilds: {guild_count}\nLatency: {round(self.bot.latency * 1000)}ms\nPython: {platform.python_version()}",
                inline=True,
            )

            embed.add_field(name="Discord.py", value=f"Version: {discord.__version__}", inline=True)

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await interaction.response.send_message("❌ Error retrieving bot status", ephemeral=True)

    @app_commands.command(name="sync", description="Sync slash commands")
    async def sync_commands(self, interaction: discord.Interaction):
        """Sync slash commands."""
        try:
            # Check if user has admin permissions
            if not interaction.guild:
                await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
                return

            member = interaction.guild.get_member(interaction.user.id)
            if not member or not member.guild_permissions.administrator:
                await interaction.response.send_message(
                    "❌ You need administrator permissions to use this command.", ephemeral=True
                )
                return

            # Sync commands
            synced = await self.bot.tree.sync()

            await interaction.response.send_message(f"✅ Successfully synced {len(synced)} command(s)!", ephemeral=True)

        except Exception as e:
            logger.error(f"Error in sync command: {e}")
            await interaction.response.send_message("❌ Error syncing commands", ephemeral=True)

    @app_commands.command(name="uptime", description="Get bot uptime")
    async def uptime(self, interaction: discord.Interaction):
        """Get bot uptime."""
        try:
            uptime = datetime.now() - self.bot.start_time
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            if days > 0:
                uptime_str = f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                uptime_str = f"{hours}h {minutes}m"
            else:
                uptime_str = f"{minutes}m {seconds}s"

            await interaction.response.send_message(f"⏱️ Bot uptime: {uptime_str}", ephemeral=True)

        except Exception as e:
            logger.error(f"Error in uptime command: {e}")
            await interaction.response.send_message("❌ Error getting uptime", ephemeral=True)
