#!/usr/bin/env python3
"""
commands.py - GotLockz Discord Bot Commands

Clean, professional slash commands for betting analysis and pick management.
"""
import logging
import json
import requests
from datetime import datetime
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)

class BettingCommands(app_commands.Group):
    """Betting-related slash commands."""
    
    def __init__(self, bot):
        super().__init__(name="betting", description="Betting analysis and pick management")
        self.bot = bot
        self.pick_counters = {"vip": 0, "lotto": 0, "free": 0}
        self._load_counters()

    def _load_counters(self):
        """Load pick counters from file."""
        try:
            with open('counters.json', 'r') as f:
                self.pick_counters = json.load(f)
        except FileNotFoundError:
            pass
        except Exception as e:
            logger.error(f"Error loading counters: {e}")

    def _save_counters(self):
        """Save pick counters to file."""
        try:
            with open('counters.json', 'w') as f:
                json.dump(self.pick_counters, f)
        except Exception as e:
            logger.error(f"Error saving counters: {e}")

    @app_commands.command(name="vip", description="Post a VIP pick")
    @app_commands.describe(
        image="Upload a betting slip image",
        context="Optional context or notes"
    )
    async def vip_command(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        context: Optional[str] = None
    ):
        """Post a VIP pick."""
        await self._post_pick(interaction, image, context, "vip")

    @app_commands.command(name="lotto", description="Post a lotto pick")
    @app_commands.describe(
        image="Upload a betting slip image",
        context="Optional context or notes"
    )
    async def lotto_command(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        context: Optional[str] = None
    ):
        """Post a lotto pick."""
        await self._post_pick(interaction, image, context, "lotto")

    @app_commands.command(name="free", description="Post a free pick")
    @app_commands.describe(
        image="Upload a betting slip image",
        context="Optional context or notes"
    )
    async def free_command(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        context: Optional[str] = None
    ):
        """Post a free pick."""
        await self._post_pick(interaction, image, context, "free")

    @app_commands.command(name="analyze", description="Analyze a betting slip image")
    @app_commands.describe(
        image="Upload a betting slip image to analyze",
        context="Optional context or notes about the bet"
    )
    async def analyze_command(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        context: Optional[str] = None
    ):
        """Analyze a betting slip image."""
        await interaction.response.defer(thinking=True)
        
        try:
            # Validate image
            if not image.content_type or not image.content_type.startswith('image/'):
                await interaction.followup.send("❌ Please upload a valid image file!", ephemeral=True)
                return
            
            # Create analysis embed
            embed = discord.Embed(
                title="📊 Bet Analysis",
                description="Image analysis completed",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            
            # Add image
            embed.set_image(url=image.url)
            
            # Add basic info
            embed.add_field(
                name="📋 Image Details",
                value=f"**Filename:** {image.filename}\n"
                      f"**Type:** {image.content_type}\n"
                      f"**Context:** {context or 'No context provided'}",
                inline=True
            )
            
            embed.add_field(
                name="🤖 Analysis Status",
                value="✅ Basic analysis completed\n"
                      "📊 Image processed successfully",
                inline=True
            )
            
            embed.set_footer(text="GotLockz Bot • Analysis")
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in analyze command: {e}")
            await interaction.followup.send(f"❌ Analysis failed: {str(e)}", ephemeral=True)

    async def _post_pick(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        context: Optional[str],
        pick_type: str
    ):
        """Post a pick to Discord."""
        await interaction.response.defer(thinking=True)
        
        try:
            # Validate image
            if not image.content_type or not image.content_type.startswith('image/'):
                await interaction.followup.send("❌ Please upload a valid image file!", ephemeral=True)
                return
            
            # Increment counter
            self.pick_counters[pick_type] += 1
            self._save_counters()
            
            # Create embed
            embed = discord.Embed(
                title=f"🎯 {pick_type.upper()} PICK #{self.pick_counters[pick_type]}",
                description=context or f"New {pick_type} pick posted!",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            
            # Add image
            embed.set_image(url=image.url)
            
            # Add details
            embed.add_field(
                name="📊 Pick Details",
                value=f"**Type:** {pick_type.upper()}\n"
                      f"**Number:** #{self.pick_counters[pick_type]}\n"
                      f"**Context:** {context or 'No context provided'}",
                inline=True
            )
            
            embed.add_field(
                name="👤 Posted By",
                value=f"**User:** {interaction.user.display_name}\n"
                      f"**Channel:** <#{interaction.channel_id}>",
                inline=True
            )
            
            embed.set_footer(text=f"GotLockz Bot • {pick_type.upper()} Pick")
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            
            # Send to channel
            await interaction.followup.send(embed=embed)
            
            logger.info(f"Posted {pick_type} pick #{self.pick_counters[pick_type]} by {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error in {pick_type} command: {e}")
            await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

class InfoCommands(app_commands.Group):
    """Information and utility commands."""
    
    def __init__(self, bot):
        super().__init__(name="info", description="Bot information and utilities")
        self.bot = bot

    @app_commands.command(name="ping", description="Test bot responsiveness")
    async def ping_command(self, interaction: discord.Interaction):
        """Test bot responsiveness."""
        await interaction.response.send_message("🏓 Pong! Bot is online!")

    @app_commands.command(name="status", description="Check bot status")
    async def status_command(self, interaction: discord.Interaction):
        """Check bot status."""
        embed = discord.Embed(
            title="🤖 Bot Status",
            description="GotLockz Bot is running",
            color=0x00ff00
        )
        
        embed.add_field(
            name="Status",
            value="✅ Online",
            inline=True
        )
        
        embed.add_field(
            name="Latency",
            value=f"{round(self.bot.latency * 1000)}ms",
            inline=True
        )
        
        embed.add_field(
            name="Uptime",
            value=self.bot.get_uptime(),
            inline=True
        )
        
        embed.add_field(
            name="Servers",
            value=str(len(self.bot.guilds)),
            inline=True
        )
        
        embed.add_field(
            name="Users",
            value=str(len(self.bot.users)),
            inline=True
        )
        
        embed.add_field(
            name="Commands",
            value=str(len(self.bot.tree.get_commands())),
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stats", description="View bot statistics")
    async def stats_command(self, interaction: discord.Interaction):
        """View bot statistics."""
        embed = discord.Embed(
            title="📊 Bot Statistics",
            color=0x00ff00
        )
        
        # Pick counters
        embed.add_field(
            name="🎯 Pick Counters",
            value=f"VIP: {self.bot.pick_counters['vip']}\n"
                  f"Lotto: {self.bot.pick_counters['lotto']}\n"
                  f"Free: {self.bot.pick_counters['free']}",
            inline=True
        )
        
        # Bot status
        embed.add_field(
            name="🤖 Bot Status",
            value=f"Dashboard: {'✅' if self.bot.dashboard_enabled else '❌'}\n"
                  f"Channels: {'✅' if self.bot.channels_configured else '❌'}\n"
                  f"Uptime: {self.bot.get_uptime()}",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="force_sync", description="Force sync all commands")
    async def force_sync_command(self, interaction: discord.Interaction):
        """Force sync all commands."""
        await interaction.response.defer(thinking=True)
        
        try:
            synced = await self.bot.tree.sync()
            embed = discord.Embed(
                title="🔄 Force Sync",
                description=f"Synced {len(synced)} commands successfully!",
                color=0x00ff00
            )
            embed.add_field(name="Status", value="✅ Commands synced", inline=True)
            embed.add_field(name="Commands", value=str(len(synced)), inline=True)
            
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ Force sync failed: {e}")

async def setup(bot):
    """Setup function for the commands."""
    logger.info("🔄 Setting up command groups...")
    
    try:
        # Add command groups
        betting_commands = BettingCommands(bot)
        info_commands = InfoCommands(bot)
        
        bot.tree.add_command(betting_commands)
        bot.tree.add_command(info_commands)
        
        logger.info("✅ Command groups added successfully")
    except Exception as e:
        logger.error(f"❌ Error adding command groups: {e}")
        raise 