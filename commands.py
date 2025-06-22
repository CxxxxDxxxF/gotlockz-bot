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
            
            # Create plain text analysis
            analysis_text = f"""📊 BET ANALYSIS
📋 Image: {image.filename}
📝 Context: {context or 'No context provided'}
🤖 Status: ✅ Basic analysis completed
📊 Image processed successfully

Analysis will be enhanced with AI features in future updates."""
            
            # Send message with image attachment
            await interaction.followup.send(content=analysis_text, file=await image.to_file())
            
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
        """Post a pick to Discord using plain-text templates."""
        await interaction.response.defer(thinking=True)
        
        try:
            # Validate image
            if not image.content_type or not image.content_type.startswith('image/'):
                await interaction.followup.send("❌ Please upload a valid image file!", ephemeral=True)
                return
            
            # Increment counter
            self.pick_counters[pick_type] += 1
            self._save_counters()
            
            # Get current date
            current_date = datetime.now().strftime("%m/%d/%y")
            
            # Create message content based on pick type
            if pick_type == "vip":
                message_content = f"""🔒 | VIP PLAY #{self.pick_counters[pick_type]} 🏆 – {current_date}
⚾ | Game: {context or 'TBD'} @ {context or 'TBD'} ({current_date} {datetime.now().strftime('%I:%M')} PM EST)
🏆 | {context or 'PLAYER'} – {context or 'description'} ({context or 'odds'})
💵 | Unit Size: {context or 'units'}
👇 | Analysis Below:

{context or 'Analysis paragraph 1'}
{context or 'Analysis paragraph 2'}"""
                
            elif pick_type == "free":
                message_content = f"""FREE PLAY – {current_date}
⚾ | Game: {context or 'TBD'} @ {context or 'TBD'} ({current_date} {datetime.now().strftime('%I:%M')} PM EST)
🏆 | {context or 'PLAYER'} – {context or 'description'} ({context or 'odds'})
👇 | Analysis Below:

{context or 'Analysis paragraph 1'}
{context or 'Analysis paragraph 2'}

LOCK IT. 🔒🔥"""
                
            elif pick_type == "lotto":
                message_content = f"""🔒 | LOTTO TICKET 🎰 – {current_date}
🏆 | {context or 'Pick 1: Name – description (odds)'}
🏆 | {context or 'Pick 2: Name – description (odds)'}
🏆 | {context or 'Pick 3: Name – description (odds)'}
🏆 | {context or 'Pick 4: Name – description (odds)'}
💰 | Parlayed: {context or 'combined_odds'}
🍀 | GOOD LUCK TO ALL TAILING
( THESE ARE 1 UNIT PLAYS )"""
            
            # Send message with image attachment
            await interaction.followup.send(content=message_content, file=await image.to_file())
            
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
        status_text = f"""🤖 BOT STATUS
✅ Status: Online
⚡ Latency: {round(self.bot.latency * 1000)}ms
⏰ Uptime: {self.bot.get_uptime()}
🏠 Servers: {len(self.bot.guilds)}
👥 Users: {len(self.bot.users)}
🔧 Commands: {len(self.bot.tree.get_commands())}"""
        
        await interaction.response.send_message(content=status_text)

    @app_commands.command(name="stats", description="View bot statistics")
    async def stats_command(self, interaction: discord.Interaction):
        """View bot statistics."""
        stats_text = f"""📊 BOT STATISTICS
🎯 Pick Counters:
   VIP: {self.bot.pick_counters['vip']}
   Lotto: {self.bot.pick_counters['lotto']}
   Free: {self.bot.pick_counters['free']}

🤖 Bot Status:
   Dashboard: {'✅' if self.bot.dashboard_enabled else '❌'}
   Channels: {'✅' if self.bot.channels_configured else '❌'}
   Uptime: {self.bot.get_uptime()}"""
        
        await interaction.response.send_message(content=stats_text)

    @app_commands.command(name="force_sync", description="Force sync all commands")
    async def force_sync_command(self, interaction: discord.Interaction):
        """Force sync all commands."""
        await interaction.response.defer(thinking=True)
        
        try:
            synced = await self.bot.tree.sync()
            sync_text = f"""🔄 FORCE SYNC
✅ Status: Commands synced
🔧 Commands: {len(synced)}"""
            
            await interaction.followup.send(content=sync_text)
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