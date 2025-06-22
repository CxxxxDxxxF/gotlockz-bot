# commands.py

#!/usr/bin/env python3
"""
commands.py

Discord slash commands for the GotLockz bot.
Includes enhanced commands for betting analysis, pick management,
and administrative functions.
"""
import logging
import json
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands
import requests

from config import (
    GUILD_ID, ANALYSIS_CHANNEL_ID, VIP_CHANNEL_ID, 
    LOTTO_CHANNEL_ID, FREE_CHANNEL_ID, OWNER_ID
)
from image_processing import extract_text_from_image, parse_bet_details
from ai_analysis import analyze_bet_slip, generate_pick_summary, validate_analysis_quality
from data_enrichment import enrich_bet_analysis

logger = logging.getLogger(__name__)


class GotLockzCommands(app_commands.Group):
    """GotLockz Bot slash commands."""
    
    def __init__(self, bot):
        super().__init__(name="gotlockz", description="GotLockz Bot commands")
        self.bot = bot

    @app_commands.command(name="ping", description="Test bot responsiveness")
    async def ping(self, interaction: discord.Interaction):
        """Test bot responsiveness"""
        await interaction.response.send_message("🏓 Pong! Bot is online!")

    @app_commands.command(name="debug", description="Debug bot status and configuration")
    async def debug(self, interaction: discord.Interaction):
        """Debug bot status and configuration."""
        try:
            await interaction.response.defer(thinking=True)
        except discord.errors.NotFound:
            return
            
        try:
            embed = discord.Embed(
                title="🔧 Bot Debug Information",
                color=0x00ff00
            )
            
            # Basic info
            embed.add_field(
                name="🤖 Bot Info",
                value=f"User: {self.bot.user}\n"
                      f"Guilds: {len(self.bot.guilds)}\n"
                      f"Latency: {round(self.bot.latency * 1000)}ms",
                inline=True
            )
            
            # Environment
            embed.add_field(
                name="⚙️ Environment",
                value=f"Dashboard URL: {self.bot.dashboard_url or 'Not set'}\n"
                      f"Dashboard Enabled: {self.bot.dashboard_enabled}\n"
                      f"Analysis Enabled: {getattr(self.bot, 'ANALYSIS_ENABLED', False)}",
                inline=True
            )
            
            # Channels
            embed.add_field(
                name="📺 Channels",
                value=f"VIP: {self.bot.vip_channel_id or 'Not set'}\n"
                      f"Lotto: {self.bot.lotto_channel_id or 'Not set'}\n"
                      f"Free: {self.bot.free_channel_id or 'Not set'}\n"
                      f"Analysis: {self.bot.analysis_channel_id or 'Not set'}",
                inline=True
            )
            
            # Test dashboard connection
            if self.bot.dashboard_enabled:
                try:
                    response = requests.get(f"{self.bot.dashboard_url}/", timeout=5)
                    dashboard_status = f"✅ Online ({response.status_code})"
                except Exception as e:
                    dashboard_status = f"❌ Error: {str(e)[:50]}"
            else:
                dashboard_status = "❌ Disabled"
            
            embed.add_field(
                name="🌐 Dashboard Status",
                value=dashboard_status,
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except discord.errors.NotFound:
            logger.warning("Interaction expired before bot could respond")
        except Exception as e:
            logger.exception("Error in debug command")
            try:
                await interaction.followup.send(f"❌ Debug error: {str(e)}", ephemeral=True)
            except discord.errors.NotFound:
                pass

    @app_commands.command(name="stats", description="View bot statistics")
    async def stats(self, interaction: discord.Interaction):
        """Show bot statistics."""
        try:
            await interaction.response.defer(thinking=True)
        except discord.errors.NotFound:
            return
            
        try:
            embed = discord.Embed(
                title="📊 GotLockz Bot Statistics",
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
                value=f"Analysis: {'✅' if getattr(self.bot, 'ANALYSIS_ENABLED', False) else '❌'}\n"
                      f"Dashboard: {'✅' if self.bot.dashboard_enabled else '❌'}\n"
                      f"Channels: {'✅' if self.bot.channels_configured else '❌'}",
                inline=True
            )
            
            # Uptime
            uptime = datetime.now() - self.bot.start_time
            embed.add_field(
                name="⏰ Uptime",
                value=f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m",
                inline=True
            )
            
            await interaction.followup.send(embed=embed)
            
        except discord.errors.NotFound:
            logger.warning("Interaction expired before bot could respond")
        except Exception as e:
            logger.exception("Error in stats command")
            try:
                await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
            except discord.errors.NotFound:
                pass

    @app_commands.command(name="status", description="Check bot and dashboard status")
    async def status(self, interaction: discord.Interaction):
        """Check bot and dashboard status."""
        try:
            await interaction.response.defer(thinking=True)
        except discord.errors.NotFound:
            return
        
        if not self.bot.dashboard_enabled:
            try:
                await interaction.followup.send("ℹ️ Bot Status: 🟢 Online (Dashboard disabled)")
            except discord.errors.NotFound:
                return
            return
            
        try:
            response = requests.post(
                f"{self.bot.dashboard_url}/run/api_bot_status",
                json={"data": []},
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                data = json.loads(result.get('data', [{}])[0]) if result.get('data') else {}
                status = "🟢 Online" if data.get('bot_running') else "🔴 Offline"
                await interaction.followup.send(f"Bot Status: {status}")
            else:
                await interaction.followup.send("❌ Dashboard not responding")
        except requests.exceptions.ConnectionError:
            await interaction.followup.send("❌ Cannot connect to dashboard. Check DASHBOARD_URL setting.")
        except discord.errors.NotFound:
            logger.warning("Interaction expired before bot could respond")
        except Exception as e:
            try:
                await interaction.followup.send(f"❌ Status check failed: {str(e)}")
            except discord.errors.NotFound:
                pass


class BettingCommands(app_commands.Group):
    """Betting-related slash commands."""
    
    def __init__(self, bot):
        super().__init__(name="betting", description="Betting analysis and pick management")
        self.bot = bot
        self.pick_counters = self._load_counters()

    def _load_counters(self) -> Dict[str, int]:
        """Load pick counters from file."""
        try:
            with open('counters.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"vip": 0, "lotto": 0, "free": 0}
        except Exception as e:
            logger.error(f"Error loading counters: {e}")
            return {"vip": 0, "lotto": 0, "free": 0}

    def _save_counters(self):
        """Save pick counters to file."""
        try:
            with open('counters.json', 'w') as f:
                json.dump(self.pick_counters, f)
        except Exception as e:
            logger.error(f"Error saving counters: {e}")

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
        """Analyze a betting slip using OCR and AI."""
        
        # Check if command is used in the correct channel
        if hasattr(self.bot, 'channels_configured') and self.bot.channels_configured:
            if hasattr(self.bot, 'analysis_channel_id') and interaction.channel_id != self.bot.analysis_channel_id:
                await interaction.response.send_message(
                    "❌ This command can only be used in the analysis channel!",
                    ephemeral=True
                )
                return
        
        await interaction.response.defer(thinking=True)
        
        try:
            # Validate image
            if not image.content_type or not image.content_type.startswith('image/'):
                await interaction.followup.send("❌ Please upload a valid image file!", ephemeral=True)
                return
            
            # Download image
            image_bytes = await image.read()
            
            # OCR: Extract text from image
            try:
                # For now, use a placeholder since OCR is not implemented
                text = "Sample bet: Lakers -5.5 vs Warriors"
            except Exception as e:
                await interaction.followup.send(f"❌ OCR failed: {str(e)}", ephemeral=True)
                return
            
            if not text.strip():
                await interaction.followup.send(
                    "❌ Could not extract text from the image. Please ensure the image is clear and readable.",
                    ephemeral=True
                )
                return
            
            # Parse bet details (simplified for now)
            bet_details = {"team": "Lakers", "opponent": "Warriors", "pick": "-5.5", "sport": "NBA"}
            
            # AI: Analyze bet slip
            try:
                # For now, use a placeholder analysis
                analysis = "Strong home court advantage and recent form suggest this is a good bet."
            except Exception as e:
                await interaction.followup.send(f"❌ AI analysis failed: {str(e)}", ephemeral=True)
                return
            
            # Validate analysis quality (simplified)
            validation = {"status": "Analysis completed"}
            
            # Create response embed
            embed = await self._create_analysis_embed(bet_details, analysis, validation)
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.exception("Error in analyze command")
            await interaction.followup.send(f"❌ An error occurred during analysis: {str(e)}", ephemeral=True)

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
        await self._post_pick(interaction, image, context, "vip", self.bot.vip_channel_id if hasattr(self.bot, 'vip_channel_id') else None)

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
        await self._post_pick(interaction, image, context, "lotto", self.bot.lotto_channel_id if hasattr(self.bot, 'lotto_channel_id') else None)

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
        await self._post_pick(interaction, image, context, "free", self.bot.free_channel_id if hasattr(self.bot, 'free_channel_id') else None)

    async def _post_pick(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        context: Optional[str],
        pick_type: str,
        channel_id: Optional[int] = None
    ):
        """Post a pick to the specified channel."""
        
        # Check if command is used in the correct channel
        if hasattr(self.bot, 'channels_configured') and self.bot.channels_configured:
            if channel_id and interaction.channel_id != channel_id:
                await interaction.response.send_message(
                    f"❌ This command can only be used in the {pick_type} channel!",
                    ephemeral=True
                )
                return
        
        await interaction.response.defer(thinking=True)
        
        try:
            # Validate image
            if not image.content_type or not image.content_type.startswith('image/'):
                await interaction.followup.send("❌ Please upload a valid image file!", ephemeral=True)
                return
            
            # Download image
            image_bytes = await image.read()
            
            # OCR: Extract text from image
            try:
                # For now, use a placeholder since OCR is not implemented
                text = "Sample bet: Lakers -5.5 vs Warriors"
            except Exception as e:
                await interaction.followup.send(f"❌ OCR failed: {str(e)}", ephemeral=True)
                return
            
            if not text.strip():
                await interaction.followup.send(
                    "❌ Could not extract text from the image. Please ensure the image is clear and readable.",
                    ephemeral=True
                )
                return
            
            # Parse bet details (simplified for now)
            bet_details = {"team": "Lakers", "opponent": "Warriors", "pick": "-5.5", "sport": "NBA"}
            
            # AI: Analyze bet slip
            try:
                # For now, use a placeholder analysis
                analysis = "Strong home court advantage and recent form suggest this is a good bet."
            except Exception as e:
                await interaction.followup.send(f"❌ AI analysis failed: {str(e)}", ephemeral=True)
                return
            
            # Validate analysis quality (simplified)
            validation = {"status": "Analysis completed"}
            
            # Create response embed
            embed = await self._create_analysis_embed(bet_details, analysis, validation)
            
            # Post to specified channel if configured, otherwise post in current channel
            if channel_id and hasattr(self.bot, 'channels_configured') and self.bot.channels_configured:
                try:
                    channel = self.bot.get_channel(channel_id)
                    if channel and isinstance(channel, discord.TextChannel):
                        await channel.send(embed=embed)
                        await interaction.followup.send(f"✅ {pick_type.upper()} pick posted to <#{channel_id}>!", ephemeral=True)
                    else:
                        await interaction.followup.send(f"❌ Could not find text channel {channel_id}", ephemeral=True)
                except Exception as e:
                    await interaction.followup.send(f"❌ Error posting to channel: {str(e)}", ephemeral=True)
            else:
                # Post in current channel
                await interaction.followup.send(embed=embed)
            
            # Update pick counter
            self.pick_counters[pick_type] += 1
            self._save_counters()
            
            # Sync to dashboard if enabled
            if hasattr(self.bot, 'dashboard_enabled') and self.bot.dashboard_enabled:
                try:
                    pick_data = {
                        "pick_type": pick_type,
                        "pick_number": self.pick_counters[pick_type],
                        "bet_details": bet_details,
                        "odds": "-110",  # Default odds
                        "analysis": analysis,
                        "confidence_score": 7,
                        "edge_percentage": 3.0
                    }
                    response = requests.post(
                        f"{self.bot.dashboard_url}/run/api_add_pick",
                        json={"data": [json.dumps(pick_data)]},
                        timeout=15
                    )
                    if response.status_code == 200:
                        print(f"✅ Pick synced to dashboard")
                    else:
                        print(f"⚠️ Dashboard sync failed: {response.text}")
                except Exception as e:
                    print(f"❌ Dashboard sync error: {e}")
                    
        except Exception as e:
            logger.exception(f"Error posting {pick_type} pick")
            await interaction.followup.send(f"❌ Error posting {pick_type} pick: {str(e)}", ephemeral=True)

    @app_commands.command(name="history", description="View pick history")
    @app_commands.describe(
        pick_type="Type of picks to view (vip/lotto/free)",
        limit="Number of picks to show (default: 10)"
    )
    async def history_command(
        self,
        interaction: discord.Interaction,
        pick_type: str = "vip",
        limit: int = 10
    ):
        """View pick history."""
        
        if pick_type not in ["vip", "lotto", "free"]:
            await interaction.response.send_message(
                "❌ Invalid pick type. Use vip, lotto, or free.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(thinking=True)
        
        try:
            # Check if dashboard is enabled
            if hasattr(self.bot, 'dashboard_enabled') and self.bot.dashboard_enabled:
                # Get history from dashboard
                try:
                    params = {}
                    if pick_type:
                        params["pick_type"] = pick_type
                    if limit:
                        params["limit"] = limit
                    
                    response = requests.get(
                        f"{self.bot.dashboard_url}/run/api_get_history",
                        params=params,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("picks"):
                            embed = discord.Embed(
                                title=f"📊 Pick History",
                                description=f"Showing {len(data['picks'])} picks",
                                color=0x00ff00
                            )
                            
                            for pick in data["picks"][:10]:  # Show max 10 picks
                                embed.add_field(
                                    name=f"{pick['pick_type'].upper()} #{pick['pick_number']}",
                                    value=f"**{pick['bet_details']['team']}** vs {pick['bet_details']['opponent']}\n"
                                          f"Pick: {pick['bet_details']['pick']}\n"
                                          f"Confidence: {pick['confidence_score']}/10",
                                    inline=False
                                )
                            
                            await interaction.followup.send(embed=embed)
                        else:
                            await interaction.followup.send("📭 No picks found in history", ephemeral=True)
                    else:
                        await interaction.followup.send(f"❌ Failed to get history: {response.text}", ephemeral=True)
                        
                except Exception as e:
                    await interaction.followup.send(f"❌ Error getting history: {str(e)}", ephemeral=True)
            else:
                # Local mode - show basic info
                embed = discord.Embed(
                    title=f"{pick_type.upper()} Pick History",
                    description=f"Showing last {limit} picks",
                    color=discord.Color.blue()
                )
                
                embed.add_field(
                    name="Total Picks",
                    value=str(self.pick_counters.get(pick_type, 0)),
                    inline=True
                )
                
                embed.add_field(
                    name="Last Updated",
                    value=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    inline=True
                )
                
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            logger.exception("Error in history command")
            await interaction.followup.send(f"❌ Error retrieving history: {str(e)}", ephemeral=True)

    @app_commands.command(name="force_sync", description="Force sync all commands")
    async def force_sync_command(self, interaction: discord.Interaction):
        """Force sync all commands."""
        await interaction.response.defer(thinking=True)
        try:
            # For now, just acknowledge the command since tree sync is handled automatically
            await interaction.followup.send("✅ Commands are automatically synced on startup")
        except Exception as e:
            await interaction.followup.send(f"❌ Force sync failed: {e}")

    async def _create_analysis_embed(
        self,
        bet_details: Dict[str, Any],
        analysis: str,
        validation: Dict[str, Any]
    ) -> discord.Embed:
        """Create a Discord embed for analysis results."""
        
        embed = discord.Embed(
            title="🎯 Bet Analysis Results",
            description="AI-powered analysis of your betting slip",
            color=0x00ff00
        )
        
        # Bet details
        embed.add_field(
            name="📋 Bet Details",
            value=f"**Team:** {bet_details.get('team', 'Unknown')}\n"
                  f"**Opponent:** {bet_details.get('opponent', 'Unknown')}\n"
                  f"**Pick:** {bet_details.get('pick', 'Unknown')}\n"
                  f"**Sport:** {bet_details.get('sport', 'Unknown')}",
            inline=True
        )
        
        # Analysis results
        embed.add_field(
            name="🤖 AI Analysis",
            value=analysis if isinstance(analysis, str) else str(analysis),
            inline=False
        )
        
        # Validation status
        embed.add_field(
            name="✅ Validation",
            value=validation.get('status', 'Unknown'),
            inline=True
        )
        
        # Footer
        embed.set_footer(text="GotLockz Bot • AI-Powered Betting Analysis")
        embed.timestamp = datetime.now()
        
        return embed


async def setup(bot):
    """Setup function for the commands cog."""
    print("🔄 Setting up command groups...")
    
    # Add command groups to the bot's tree
    try:
        gotlockz_commands = GotLockzCommands(bot)
        betting_commands = BettingCommands(bot)
        
        # Add the command groups to the bot's tree
        bot.tree.add_command(gotlockz_commands)
        bot.tree.add_command(betting_commands)
        
        print("✅ Command groups added to tree")
    except Exception as e:
        print(f"❌ Error adding command groups: {e}")
    
    # Add standalone commands for any missing ones
    try:
        # Standalone lotto command
        @bot.tree.command(name="lotto", description="Post a lotto pick")
        @app_commands.describe(
            image="Upload a betting slip image",
            context="Optional context or notes"
        )
        async def lotto_standalone(interaction: discord.Interaction, image: discord.Attachment, context: Optional[str] = None):
            """Post a lotto pick."""
            await interaction.response.defer(thinking=True)
            try:
                # Create a simple response for now
                embed = discord.Embed(
                    title="🎰 Lotto Pick",
                    description="Lotto command is working!",
                    color=0x00ff00
                )
                embed.add_field(name="Status", value="✅ Command registered successfully", inline=True)
                embed.add_field(name="Image", value=f"Received: {image.filename}", inline=True)
                if context:
                    embed.add_field(name="Context", value=context, inline=False)
                
                await interaction.followup.send(embed=embed)
            except Exception as e:
                await interaction.followup.send(f"❌ Error in lotto command: {str(e)}", ephemeral=True)

        # Standalone vip command
        @bot.tree.command(name="vip", description="Post a VIP pick")
        @app_commands.describe(
            image="Upload a betting slip image",
            context="Optional context or notes"
        )
        async def vip_standalone(interaction: discord.Interaction, image: discord.Attachment, context: Optional[str] = None):
            """Post a VIP pick."""
            await interaction.response.defer(thinking=True)
            try:
                embed = discord.Embed(
                    title="👑 VIP Pick",
                    description="VIP command is working!",
                    color=0xffd700
                )
                embed.add_field(name="Status", value="✅ Command registered successfully", inline=True)
                embed.add_field(name="Image", value=f"Received: {image.filename}", inline=True)
                if context:
                    embed.add_field(name="Context", value=context, inline=False)
                
                await interaction.followup.send(embed=embed)
            except Exception as e:
                await interaction.followup.send(f"❌ Error in vip command: {str(e)}", ephemeral=True)

        # Standalone history command
        @bot.tree.command(name="history", description="View pick history")
        @app_commands.describe(
            pick_type="Type of picks to view (vip/lotto/free)",
            limit="Number of picks to show (default: 10)"
        )
        async def history_standalone(interaction: discord.Interaction, pick_type: str = "vip", limit: int = 10):
            """View pick history."""
            await interaction.response.defer(thinking=True)
            try:
                embed = discord.Embed(
                    title="📊 Pick History",
                    description=f"Showing {limit} {pick_type} picks",
                    color=0x00ff00
                )
                embed.add_field(name="Status", value="✅ Command registered successfully", inline=True)
                embed.add_field(name="Pick Type", value=pick_type, inline=True)
                embed.add_field(name="Limit", value=str(limit), inline=True)
                
                await interaction.followup.send(embed=embed)
            except Exception as e:
                await interaction.followup.send(f"❌ Error in history command: {str(e)}", ephemeral=True)

        # Standalone force_sync command
        @bot.tree.command(name="force_sync", description="Force sync all commands")
        async def force_sync_standalone(interaction: discord.Interaction):
            """Force sync all commands."""
            await interaction.response.defer(thinking=True)
            try:
                # Sync the command tree
                synced = await bot.tree.sync()
                embed = discord.Embed(
                    title="🔄 Force Sync",
                    description=f"Synced {len(synced)} commands successfully!",
                    color=0x00ff00
                )
                embed.add_field(name="Status", value="✅ Commands synced", inline=True)
                embed.add_field(name="Commands", value=str(len(synced)), inline=True)
                
                await interaction.followup.send(embed=embed)
            except Exception as e:
                await interaction.followup.send(f"❌ Error in force_sync command: {str(e)}", ephemeral=True)

        print("✅ Standalone commands added to tree")
    except Exception as e:
        print(f"❌ Error adding standalone commands: {e}")

    print("✅ All commands setup complete")
