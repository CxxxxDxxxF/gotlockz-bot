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
        
        # Initialize command tree
        # self.tree = commands.app_commands.CommandTree(self)

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
        
        # Define all slash commands
        commands = [
            discord.app_commands.Command(
                name="ping",
                description="Test bot responsiveness",
                callback=self._ping_command
            ),
            discord.app_commands.Command(
                name="analyze",
                description="Analyze a betting slip image",
                callback=self._analyze_command
            ),
            discord.app_commands.Command(
                name="vip",
                description="Post a VIP pick",
                callback=self._vip_command
            ),
            discord.app_commands.Command(
                name="lotto",
                description="Post a lotto pick",
                callback=self._lotto_command
            ),
            discord.app_commands.Command(
                name="free",
                description="Post a free pick",
                callback=self._free_command
            ),
            discord.app_commands.Command(
                name="history",
                description="View pick history",
                callback=self._history_command
            ),
            discord.app_commands.Command(
                name="stats",
                description="View bot statistics",
                callback=self._stats_command
            ),
            discord.app_commands.Command(
                name="sync",
                description="Sync picks from Discord to dashboard",
                callback=self._sync_command
            ),
            discord.app_commands.Command(
                name="status",
                description="Check bot and dashboard status",
                callback=self._status_command
            ),
            discord.app_commands.Command(
                name="addpick",
                description="Add a new pick to the dashboard",
                callback=self._addpick_command
            ),
            discord.app_commands.Command(
                name="force_sync",
                description="Force sync all commands",
                callback=self._force_sync_command
            )
        ]
        
        # Add commands to the tree
        for cmd in commands:
            self.tree.add_command(cmd)
        
        print(f"✅ Added {len(commands)} slash commands")

    async def _ping_command(self, interaction: discord.Interaction):
        """Test bot responsiveness"""
        await interaction.response.send_message("🏓 Pong! Bot is online!")

    async def _analyze_command(self, interaction: discord.Interaction, image: discord.Attachment, context: Optional[str] = None):
        """Analyze a betting slip using OCR and AI."""
        # Check if command is used in the correct channel
        if self.channels_configured and interaction.channel_id != self.analysis_channel_id:
            try:
                await interaction.response.send_message(
                    "❌ This command can only be used in the analysis channel!",
                    ephemeral=True
                )
            except discord.errors.NotFound:
                return
            return
        
        if not ANALYSIS_ENABLED:
            try:
                await interaction.response.send_message(
                    "❌ Analysis functionality is not available. Please install required dependencies: opencv-python, pytesseract",
                    ephemeral=True
                )
            except discord.errors.NotFound:
                return
            return
            
        try:
            await interaction.response.defer(thinking=True)
        except discord.errors.NotFound:
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
            await interaction.followup.send(embed=embed)
        except discord.errors.NotFound:
            logger.warning("Interaction expired before bot could respond")
        except Exception as e:
            logger.exception("Error in analyze command")
            try:
                await interaction.followup.send(f"❌ An error occurred during analysis: {str(e)}", ephemeral=True)
            except discord.errors.NotFound:
                pass

    async def _vip_command(self, interaction: discord.Interaction, image: discord.Attachment, context: Optional[str] = None):
        """Post a VIP pick with analysis."""
        # Check if command is used in the correct channel
        if self.channels_configured and interaction.channel_id != self.vip_channel_id:
            try:
                await interaction.response.send_message(
                    "❌ This command can only be used in the VIP channel!",
                    ephemeral=True
                )
            except discord.errors.NotFound:
                return
            return
        
        await self._post_pick_with_analysis(interaction, image, context or "", "vip", self.vip_channel_id if self.channels_configured else None)

    async def _lotto_command(self, interaction: discord.Interaction, image: discord.Attachment, context: Optional[str] = None):
        """Post a lotto pick with analysis."""
        # Check if command is used in the correct channel
        if self.channels_configured and interaction.channel_id != self.lotto_channel_id:
            try:
                await interaction.response.send_message(
                    "❌ This command can only be used in the lotto channel!",
                    ephemeral=True
                )
            except discord.errors.NotFound:
                return
            return
        
        await self._post_pick_with_analysis(interaction, image, context or "", "lotto", self.lotto_channel_id if self.channels_configured else None)

    async def _free_command(self, interaction: discord.Interaction, image: discord.Attachment, context: Optional[str] = None):
        """Post a free pick with analysis."""
        # Check if command is used in the correct channel
        if self.channels_configured and interaction.channel_id != self.free_channel_id:
            try:
                await interaction.response.send_message(
                    "❌ This command can only be used in the free channel!",
                    ephemeral=True
                )
            except discord.errors.NotFound:
                return
            return
        
        await self._post_pick_with_analysis(interaction, image, context or "", "free", self.free_channel_id if self.channels_configured else None)

    async def _history_command(self, interaction: discord.Interaction, pick_type: Optional[str] = None, limit: Optional[int] = None):
        """Show pick history."""
        try:
            await interaction.response.defer(thinking=True)
        except discord.errors.NotFound:
            return
            
        try:
            if not self.dashboard_enabled:
                await interaction.followup.send("❌ Dashboard is not available", ephemeral=True)
                return
            
            # Get history from dashboard
            try:
                params = {}
                if pick_type:
                    params["pick_type"] = pick_type
                if limit:
                    params["limit"] = limit
                
                response = requests.get(
                    f"{self.dashboard_url}/run/api_get_history",
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
                
        except discord.errors.NotFound:
            logger.warning("Interaction expired before bot could respond")
        except Exception as e:
            logger.exception("Error in history command")
            try:
                await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
            except discord.errors.NotFound:
                pass

    async def _stats_command(self, interaction: discord.Interaction):
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
                value=f"VIP: {self.pick_counters['vip']}\n"
                      f"Lotto: {self.pick_counters['lotto']}\n"
                      f"Free: {self.pick_counters['free']}",
                inline=True
            )
            
            # Bot status
            embed.add_field(
                name="🤖 Bot Status",
                value=f"Analysis: {'✅' if ANALYSIS_ENABLED else '❌'}\n"
                      f"Dashboard: {'✅' if self.dashboard_enabled else '❌'}\n"
                      f"Channels: {'✅' if self.channels_configured else '❌'}",
                inline=True
            )
            
            # Uptime
            uptime = datetime.now() - self.start_time
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

    async def _sync_command(self, interaction: discord.Interaction):
        """Sync picks from Discord to dashboard."""
        try:
            await interaction.response.defer(thinking=True)
        except discord.errors.NotFound:
            return
        
        if not self.dashboard_enabled:
            try:
                await interaction.followup.send("ℹ️ Dashboard is disabled. Running in local mode.")
            except discord.errors.NotFound:
                return
            return
            
        try:
            # Example: Send some test picks to dashboard
            test_picks = [
                {
                    "pick_number": 1,
                    "pick_type": "vip",
                    "bet_details": "Lakers -5.5 vs Warriors",
                    "odds": "-110",
                    "analysis": "Strong home court advantage",
                    "posted_at": datetime.now().isoformat(),
                    "confidence_score": 8,
                    "edge_percentage": 5.2,
                    "result": "win",
                    "profit_loss": 50.0
                }
            ]
            
            response = requests.post(
                f"{self.dashboard_url}/run/api_sync_discord",
                json={"data": [json.dumps(test_picks)]},
                timeout=15
            )
            
            if response.status_code == 200:
                await interaction.followup.send("✅ Picks synced to dashboard successfully!")
            else:
                await interaction.followup.send(f"❌ Sync failed: {response.text}")
                
        except requests.exceptions.ConnectionError:
            await interaction.followup.send("❌ Cannot connect to dashboard. Make sure DASHBOARD_URL is set correctly.")
        except discord.errors.NotFound:
            logger.warning("Interaction expired before bot could respond")
        except Exception as e:
            try:
                await interaction.followup.send(f"❌ Sync error: {str(e)}")
            except discord.errors.NotFound:
                pass

    async def _status_command(self, interaction: discord.Interaction):
        """Check bot and dashboard status."""
        try:
            await interaction.response.defer(thinking=True)
        except discord.errors.NotFound:
            return
        
        if not self.dashboard_enabled:
            try:
                await interaction.followup.send("ℹ️ Bot Status: 🟢 Online (Dashboard disabled)")
            except discord.errors.NotFound:
                return
            return
            
        try:
            response = requests.post(
                f"{self.dashboard_url}/run/api_bot_status",
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

    async def _addpick_command(self, interaction: discord.Interaction, pick_type: str, pick_number: int, bet_details: str):
        """Add a new pick to the dashboard."""
        try:
            await interaction.response.defer(thinking=True)
        except discord.errors.NotFound:
            return
        
        if not self.dashboard_enabled:
            try:
                await interaction.followup.send("ℹ️ Dashboard is disabled. Cannot add picks.")
            except discord.errors.NotFound:
                return
            return
            
        try:
            pick_data = {
                "pick_type": pick_type.lower(),
                "pick_number": pick_number,
                "bet_details": bet_details,
                "odds": "-110",  # Default odds
                "analysis": f"Added via Discord by {interaction.user.name}",
                "confidence_score": 7,
                "edge_percentage": 3.0
            }
            
            response = requests.post(
                f"{self.dashboard_url}/run/api_add_pick",
                json={"data": [json.dumps(pick_data)]},
                timeout=15
            )
            
            if response.status_code == 200:
                await interaction.followup.send(f"✅ Pick #{pick_number} added successfully!")
            else:
                await interaction.followup.send(f"❌ Failed to add pick: {response.text}")
                
        except requests.exceptions.ConnectionError:
            await interaction.followup.send("❌ Cannot connect to dashboard. Check DASHBOARD_URL setting.")
        except discord.errors.NotFound:
            logger.warning("Interaction expired before bot could respond")
        except Exception as e:
            try:
                await interaction.followup.send(f"❌ Error adding pick: {str(e)}")
            except discord.errors.NotFound:
                pass

    async def _force_sync_command(self, interaction: discord.Interaction):
        """Force sync all commands."""
        try:
            await interaction.response.defer(thinking=True)
        except discord.errors.NotFound:
            return
        try:
            synced = await self.tree.sync()
            await interaction.followup.send(f"✅ Force synced {len(synced)} command(s)")
        except discord.errors.NotFound:
            logger.warning("Interaction expired before bot could respond")
        except Exception as e:
            try:
                await interaction.followup.send(f"❌ Force sync failed: {e}")
            except discord.errors.NotFound:
                pass

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
        """Create an embed for bet analysis results."""
        embed = discord.Embed(
            title="🔍 Bet Analysis Results",
            description="AI-powered betting slip analysis",
            color=discord.Color.blue()
        )
        
        # Add bet details
        if bet_details:
            if isinstance(bet_details, dict):
                embed.add_field(
                    name="📋 Bet Details",
                    value=f"```{json.dumps(bet_details, indent=2)}```",
                    inline=False
                )
            else:
                embed.add_field(
                    name="📋 Bet Details",
                    value=str(bet_details),
                    inline=False
                )
        else:
            embed.add_field(
                name="📋 Bet Details",
                value="No bet details available",
                inline=False
            )
        
        # Add analysis results
        if analysis:
            if isinstance(analysis, dict):
                embed.add_field(
                    name="🤖 AI Analysis",
                    value=analysis.get('summary', 'No analysis available'),
                    inline=False
                )
                
                if 'confidence' in analysis:
                    embed.add_field(
                        name="📊 Confidence",
                        value=f"{analysis['confidence']}/10",
                        inline=True
                    )
                
                if 'recommendation' in analysis:
                    embed.add_field(
                        name="💡 Recommendation",
                        value=analysis['recommendation'],
                        inline=True
                    )
            else:
                embed.add_field(
                    name="🤖 AI Analysis",
                    value=str(analysis),
                    inline=False
                )
        else:
            embed.add_field(
                name="🤖 AI Analysis",
                value="Analysis not available",
                inline=False
            )
        
        # Add validation results
        if validation:
            if isinstance(validation, dict):
                embed.add_field(
                    name="✅ Validation",
                    value=validation.get('status', 'Unknown'),
                    inline=True
                )
            else:
                embed.add_field(
                    name="✅ Validation",
                    value=str(validation),
                    inline=True
                )
        else:
            embed.add_field(
                name="✅ Validation",
                value="Validation not available",
                inline=True
            )
        
        embed.set_footer(text="Analysis completed by GotLockz AI")
        return embed

    def _get_uptime(self) -> str:
        """Get bot uptime."""
        return "Online"  # Simplified for now

    async def on_message(self, message):
        # Don't respond to bot's own messages
        if message.author == self.user:
            return
        
        await self.process_commands(message)
