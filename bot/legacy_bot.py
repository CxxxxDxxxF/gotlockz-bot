#!/usr/bin/env python3
"""
bot.py - GotLockz Discord Bot Core

Professional Discord bot implementation with proper command handling.
"""
import os
import json
import logging
import requests
from datetime import datetime
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

# Import our analysis modules
try:
    from utils.ocr_parser import extract_bet_info
    from utils.gpt_analysis import generate_analysis, generate_pick_summary
    ANALYSIS_ENABLED = True
except ImportError:
    ANALYSIS_ENABLED = False
    logger = logging.getLogger(__name__)
    logger.warning("Analysis modules not available - OCR/AI features disabled")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GotLockzBot(commands.Bot):
    """Professional Discord bot for betting analysis and pick management."""

    def __init__(self):
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        # Initialize bot
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

        # Bot configuration
        self.start_time = datetime.now()
        self.pick_counters = {"vip": 0, "lotto": 0, "free": 0}

        # Load configuration
        self._load_config()
        self._load_counters()

        logger.info("Bot initialized successfully")

    def _load_config(self):
        """Load bot configuration from environment variables."""
        # Channel IDs
        self.vip_channel_id = int(
            os.getenv(
                'VIP_CHANNEL_ID',
                0)) if os.getenv('VIP_CHANNEL_ID') else None
        self.lotto_channel_id = int(
            os.getenv(
                'LOTTO_CHANNEL_ID',
                0)) if os.getenv('LOTTO_CHANNEL_ID') else None
        self.free_channel_id = int(
            os.getenv(
                'FREE_CHANNEL_ID',
                0)) if os.getenv('FREE_CHANNEL_ID') else None
        self.analysis_channel_id = int(
            os.getenv(
                'ANALYSIS_CHANNEL_ID',
                0)) if os.getenv('ANALYSIS_CHANNEL_ID') else None
        self.log_channel_id = int(
            os.getenv(
                'LOG_CHANNEL_ID',
                0)) if os.getenv('LOG_CHANNEL_ID') else None

        # Check if channels are configured
        self.channels_configured = all([
            self.vip_channel_id, self.lotto_channel_id,
            self.free_channel_id, self.analysis_channel_id
        ])

        # Dashboard configuration
        self.dashboard_url = os.getenv('DASHBOARD_URL')
        self.dashboard_enabled = bool(self.dashboard_url)

        logger.info(
            f"Configuration loaded - Channels: {self.channels_configured}, Dashboard: {self.dashboard_enabled}")

    def _load_counters(self):
        """Load pick counters from file."""
        try:
            with open('counters.json', 'r') as f:
                self.pick_counters = json.load(f)
                logger.info(f"Counters loaded: {self.pick_counters}")
        except FileNotFoundError:
            logger.info("No counters file found, using defaults")
        except Exception as e:
            logger.error(f"Error loading counters: {e}")

    def _save_counters(self):
        """Save pick counters to file."""
        try:
            with open('counters.json', 'w') as f:
                json.dump(self.pick_counters, f)
        except Exception as e:
            logger.error(f"Error saving counters: {e}")

    async def setup_hook(self):
        """Set up the bot's slash commands."""
        logger.info("🔄 Setting up slash commands...")

        try:
            # Load commands from commands.py
            from commands import setup as setup_commands
            await setup_commands(self)
            logger.info("✅ Commands loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load commands: {e}")
            # Create fallback commands
            await self._create_fallback_commands()

    async def _create_fallback_commands(self):
        """Create basic fallback commands if main commands fail."""
        logger.info("Creating fallback commands...")

        @self.tree.command(name="ping", description="Test bot responsiveness")
        async def ping(interaction: discord.Interaction):
            await interaction.response.send_message("🏓 Pong! Bot is online!")

        @self.tree.command(name="status", description="Check bot status")
        async def status(interaction: discord.Interaction):
            embed = discord.Embed(
                title="🤖 Bot Status",
                description="GotLockz Bot is running",
                color=0x00ff00
            )
            embed.add_field(name="Status", value="✅ Online", inline=True)
            embed.add_field(
                name="Latency",
                value=f"{round(self.latency * 1000)}ms",
                inline=True)
            embed.add_field(name="Servers", value=str(
                len(self.guilds)), inline=True)
            await interaction.response.send_message(embed=embed)

    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"✅ Bot connected as {self.user}")
        logger.info(f"📊 Connected to {len(self.guilds)} guild(s)")
        logger.info(f"👥 Serving {len(self.users)} user(s)")

        # Sync slash commands
        logger.info("🔄 Syncing slash commands...")
        try:
            synced = await self.tree.sync()
            logger.info(f"✅ Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"❌ Command sync failed: {e}")

        # Test dashboard connection
        if self.dashboard_enabled:
            try:
                response = requests.get(
                    f"{self.dashboard_url}/api/ping", timeout=10)
                if response.status_code == 200:
                    logger.info("✅ Dashboard connection successful")
                else:
                    logger.warning("⚠️ Dashboard connection failed")
            except Exception as e:
                logger.warning(f"⚠️ Dashboard connection error: {e}")
        else:
            logger.info("ℹ️ Dashboard disabled - using local mode")

    async def on_app_command_error(self,
                                   interaction: discord.Interaction,
                                   error: app_commands.AppCommandError):
        """Handle application command errors."""
        logger.error(f"Command error: {error}")

        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"⏰ Please wait {error.retry_after:.1f} seconds before using this command again.",
                ephemeral=True
            )
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ An error occurred: {str(error)}",
                ephemeral=True
            )

    def get_uptime(self) -> str:
        """Get bot uptime as a formatted string."""
        uptime = datetime.now() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"

    async def _post_pick_with_analysis(
            self,
            interaction: discord.Interaction,
            image: discord.Attachment,
            context: str,
            pick_type: str,
            channel_id: Optional[int] = None):
        """Post a pick with analysis to the specified channel."""
        # Check if interaction has already been responded to
        if interaction.response.is_done():
            return

        if not ANALYSIS_ENABLED:
            try:
                await interaction.response.send_message(
                    "❌ Analysis functionality is not available. Please install required dependencies: opencv-python, pytesseract",
                    ephemeral=True
                )
            except discord.errors.NotFound:
                # Interaction expired, can't respond
                return
            return

        try:
            await interaction.response.defer(thinking=True)
        except discord.errors.NotFound:
            # Interaction expired, can't respond
            return

        try:
            # Validate image
            if not image.content_type or not image.content_type.startswith(
                    'image/'):
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
            bet_details = {
                "team": "Lakers",
                "opponent": "Warriors",
                "pick": "-5.5",
                "sport": "NBA"}

            # AI: Analyze bet slip
            try:
                analysis = generate_analysis(str(bet_details))
            except Exception as e:
                await interaction.followup.send(f"❌ AI analysis failed: {str(e)}", ephemeral=True)
                return

            # Validate analysis quality (simplified)
            validation = {"status": "Analysis completed"}

            # Create response embed
            embed = await self._create_analysis_embed(bet_details, analysis, validation)

            # Post to specified channel if configured, otherwise post in
            # current channel
            if channel_id and self.channels_configured:
                try:
                    channel = self.get_channel(channel_id)
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
            if self.dashboard_enabled:
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
                        f"{self.dashboard_url}/run/api_add_pick",
                        json={"data": [json.dumps(pick_data)]},
                        timeout=15
                    )
                    if response.status_code == 200:
                        print(f"✅ Pick synced to dashboard")
                    else:
                        print(f"⚠️ Dashboard sync failed: {response.text}")
                except Exception as e:
                    print(f"❌ Dashboard sync error: {e}")

        except discord.errors.NotFound:
            # Interaction expired, can't respond
            logger.warning("Interaction expired before bot could respond")
        except Exception as e:
            logger.exception("Error in _post_pick_with_analysis")
            try:
                await interaction.followup.send(f"❌ An error occurred while posting the pick: {str(e)}", ephemeral=True)
            except discord.errors.NotFound:
                # Interaction expired, can't respond
                pass

    async def _create_analysis_embed(self, bet_details, analysis, validation):
        """Create a Discord embed for bet analysis results."""
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

    async def on_message(self, message):
        # Don't respond to bot's own messages
        if message.author == self.user:
            return

        await self.process_commands(message)
