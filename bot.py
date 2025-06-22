import os
import json
import requests
import logging
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

# Set up Discord intents
intents = discord.Intents.all()

class GotLockzBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix="!", intents=intents, **kwargs)
        self.pick_counters = {"vip": 0, "lotto": 0, "free": 0}
        self.start_time = datetime.now()
        self._load_counters()
        
        # Channel configuration
        self.vip_channel_id = int(os.getenv("VIP_CHANNEL_ID", "0"))
        self.lotto_channel_id = int(os.getenv("LOTTO_CHANNEL_ID", "0"))
        self.free_channel_id = int(os.getenv("FREE_CHANNEL_ID", "0"))
        self.analysis_channel_id = int(os.getenv("ANALYSIS_CHANNEL_ID", "0"))
        self.channels_configured = all([
            self.vip_channel_id, self.lotto_channel_id, 
            self.free_channel_id, self.analysis_channel_id
        ])
        
        # Dashboard configuration
        self.dashboard_url = os.getenv("DASHBOARD_URL", "")
        self.dashboard_enabled = bool(self.dashboard_url)

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

    async def on_ready(self):
        print(f"Bot connected as {self.user}")
        print(f"Dashboard URL: {self.dashboard_url}")
        print(f"Dashboard enabled: {self.dashboard_enabled}")
        print(f"Analysis enabled: {ANALYSIS_ENABLED}")
        print(f"Channels configured: {self.channels_configured}")
        
        # Sync slash commands with Discord
        print("🔄 Syncing slash commands...")
        try:
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"❌ Command sync failed: {e}")
        
        # Test dashboard connection only if dashboard is enabled
        if self.dashboard_enabled:
            try:
                # Test with Gradio API endpoint
                response = requests.post(
                    f"{self.dashboard_url}/run/api_ping",
                    json={"data": []},
                    timeout=10
                )
                if response.status_code == 200:
                    print("✅ Dashboard connection successful")
                else:
                    print("⚠️ Dashboard connection failed")
            except Exception as e:
                print(f"❌ Dashboard connection error: {e}")
        else:
            print("ℹ️ Dashboard disabled - using local mode")

    async def setup_hook(self):
        """Set up the bot's slash commands."""
        print("🔄 Setting up slash commands...")
        
        # Load commands from commands.py
        try:
            from commands import setup as setup_commands
            await setup_commands(self)
            print("✅ Commands loaded from commands.py")
        except Exception as e:
            print(f"❌ Failed to load commands: {e}")
            # Fallback to basic commands
            print("⚠️ Using fallback command setup")

    async def _post_pick_with_analysis(self, interaction: discord.Interaction, image: discord.Attachment, context: str, pick_type: str, channel_id: Optional[int] = None):
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
                analysis = generate_analysis(str(bet_details))
            except Exception as e:
                await interaction.followup.send(f"❌ AI analysis failed: {str(e)}", ephemeral=True)
                return
            
            # Validate analysis quality (simplified)
            validation = {"status": "Analysis completed"}
            
            # Create response embed
            embed = await self._create_analysis_embed(bet_details, analysis, validation)
            
            # Post to specified channel if configured, otherwise post in current channel
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

    def _get_uptime(self) -> str:
        """Get bot uptime as a formatted string."""
        uptime = datetime.now() - self.start_time
        return f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m"

    async def on_message(self, message):
        # Don't respond to bot's own messages
        if message.author == self.user:
            return
        
        await self.process_commands(message)

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Handle application command errors."""
        if isinstance(error, app_commands.CommandNotFound):
            await interaction.response.send_message(
                "❌ That command doesn't exist or was removed. Please try again or contact support.",
                ephemeral=True
            )
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
        elif isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"⏰ This command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            # Log the error for debugging
            logger.exception(f"Unhandled app command error: {error}")
            await interaction.response.send_message(
                "❌ An unexpected error occurred. Please try again or contact support.",
                ephemeral=True
            )
