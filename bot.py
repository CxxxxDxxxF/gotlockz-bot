import discord
from discord.ext import commands
import os
import requests
import json
from datetime import datetime
import logging
from typing import Optional

# Import our analysis modules
try:
    from image_processing import extract_text_from_image, parse_bet_details
    from ai_analysis import analyze_bet_slip, generate_pick_summary, validate_analysis_quality
    from data_enrichment import enrich_bet_analysis
    ANALYSIS_ENABLED = True
except ImportError as e:
    logging.warning(f"Analysis modules not available: {e}")
    ANALYSIS_ENABLED = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GotLockzBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix="!", intents=discord.Intents.all(), **kwargs)
        # Use environment variable or default to localhost for development
        self.dashboard_url = os.getenv("DASHBOARD_URL", "http://localhost:8080")
        self.dashboard_enabled = bool(os.getenv("DASHBOARD_URL"))
        self.pick_counters = self._load_counters()
        
        # Load channel IDs from config if available
        try:
            from config import ANALYSIS_CHANNEL_ID, VIP_CHANNEL_ID, LOTTO_CHANNEL_ID, FREE_CHANNEL_ID
            self.analysis_channel_id = ANALYSIS_CHANNEL_ID
            self.vip_channel_id = VIP_CHANNEL_ID
            self.lotto_channel_id = LOTTO_CHANNEL_ID
            self.free_channel_id = FREE_CHANNEL_ID
            self.channels_configured = True
        except (ImportError, ValueError):
            self.channels_configured = False
            logger.warning("Channel IDs not configured - all channels allowed")

    def _load_counters(self):
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
                text = extract_text_from_image(image_bytes)
            except Exception as e:
                await interaction.followup.send(f"❌ OCR failed: {str(e)}", ephemeral=True)
                return
            if not text.strip():
                await interaction.followup.send(
                    "❌ Could not extract text from the image. Please ensure the image is clear and readable.",
                    ephemeral=True
                )
                return
            # Parse bet details
            bet_details = parse_bet_details(text)
            if not bet_details:
                await interaction.followup.send(
                    "❌ Could not parse betting details from the image. Please ensure it's a valid betting slip.",
                    ephemeral=True
                )
                return
            # AI: Analyze bet slip
            try:
                analysis = await analyze_bet_slip(bet_details, context)
            except Exception as e:
                await interaction.followup.send(f"❌ AI analysis failed: {str(e)}", ephemeral=True)
                return
            # Validate analysis quality
            try:
                validation = await validate_analysis_quality(analysis)
            except Exception as e:
                validation = {"status": f"Validation error: {str(e)}"}
            # Create response embed
            embed = await self._create_analysis_embed(bet_details, analysis, validation)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.exception("Error in analyze command")
            await interaction.followup.send(f"❌ An error occurred during analysis: {str(e)}", ephemeral=True)

    async def _vip_command(self, interaction: discord.Interaction, image: discord.Attachment, context: Optional[str] = None):
        """Post a VIP pick."""
        await self._post_pick_with_analysis(interaction, image, context or "", "vip", self.vip_channel_id if self.channels_configured else None)

    async def _lotto_command(self, interaction: discord.Interaction, image: discord.Attachment, context: Optional[str] = None):
        """Post a lotto pick."""
        await self._post_pick_with_analysis(interaction, image, context or "", "lotto", self.lotto_channel_id if self.channels_configured else None)

    async def _free_command(self, interaction: discord.Interaction, image: discord.Attachment, context: Optional[str] = None):
        """Post a free pick."""
        await self._post_pick_with_analysis(interaction, image, context or "", "free", self.free_channel_id if self.channels_configured else None)

    async def _history_command(self, interaction: discord.Interaction, pick_type: str = "vip", limit: int = 10):
        """View pick history."""
        await interaction.response.defer()
        
        try:
            # Get pick history from dashboard if enabled
            if self.dashboard_enabled:
                response = requests.post(
                    f"{self.dashboard_url}/run/api_picks",
                    json={"data": []},
                    timeout=15
                )
                if response.status_code == 200:
                    result = response.json()
                    picks = json.loads(result.get('data', [{}])[0]) if result.get('data') else []
                    filtered_picks = [p for p in picks if p.get('pick_type') == pick_type.lower()][-limit:]
                    
                    if filtered_picks:
                        embed = discord.Embed(
                            title=f"📊 {pick_type.upper()} Pick History",
                            color=discord.Color.green()
                        )
                        
                        for pick in filtered_picks:
                            result = pick.get('result', 'Pending')
                            result_emoji = "✅" if result == "win" else "❌" if result == "loss" else "⏳"
                            embed.add_field(
                                name=f"{result_emoji} Pick #{pick['pick_number']}",
                                value=f"**Bet:** {pick['bet_details']}\n**Result:** {result.title()}\n**Posted:** {pick.get('posted_at', 'N/A')}",
                                inline=False
                            )
                    else:
                        embed = discord.Embed(
                            title=f"📊 {pick_type.upper()} Pick History",
                            description="No picks found",
                            color=discord.Color.orange()
                        )
                    
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("❌ Could not fetch pick history from dashboard")
            else:
                # Local mode - show mock data
                embed = discord.Embed(
                    title=f"📊 {pick_type.upper()} Pick History",
                    description="Dashboard disabled - showing mock data",
                    color=discord.Color.blue()
                )
                embed.add_field(
                    name="Sample Pick #1",
                    value="**Bet:** Lakers -5.5 vs Warriors\n**Result:** Win\n**Posted:** 2024-01-15 14:30:00",
                    inline=False
                )
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            await interaction.followup.send(f"❌ Error fetching history: {str(e)}")

    async def _stats_command(self, interaction: discord.Interaction):
        """View bot statistics."""
        await interaction.response.defer()
        
        try:
            if self.dashboard_enabled:
                response = requests.post(
                    f"{self.dashboard_url}/run/api_stats",
                    json={"data": []},
                    timeout=15
                )
                if response.status_code == 200:
                    result = response.json()
                    stats = json.loads(result.get('data', [{}])[0]) if result.get('data') else {}
                    
                    embed = discord.Embed(
                        title="📈 Bot Statistics",
                        color=discord.Color.blue()
                    )
                    embed.add_field(name="Total Picks", value=stats.get('total_picks', 0), inline=True)
                    embed.add_field(name="Wins", value=stats.get('wins', 0), inline=True)
                    embed.add_field(name="Losses", value=stats.get('losses', 0), inline=True)
                    embed.add_field(name="Win Rate", value=f"{stats.get('win_rate', 0):.1f}%", inline=True)
                    embed.add_field(name="Total P/L", value=f"${stats.get('total_pl', 0):.2f}", inline=True)
                    embed.add_field(name="Uptime", value=self._get_uptime(), inline=True)
                    
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("❌ Could not fetch stats from dashboard")
            else:
                # Local mode - show mock stats
                embed = discord.Embed(
                    title="📈 Bot Statistics",
                    description="Dashboard disabled - showing mock data",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Total Picks", value="25", inline=True)
                embed.add_field(name="Wins", value="18", inline=True)
                embed.add_field(name="Losses", value="7", inline=True)
                embed.add_field(name="Win Rate", value="72.0%", inline=True)
                embed.add_field(name="Total P/L", value="$450.00", inline=True)
                embed.add_field(name="Uptime", value=self._get_uptime(), inline=True)
                
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            await interaction.followup.send(f"❌ Error fetching stats: {str(e)}")

    async def _sync_command(self, interaction: discord.Interaction):
        """Sync picks from Discord to dashboard."""
        await interaction.response.defer()
        
        if not self.dashboard_enabled:
            await interaction.followup.send("ℹ️ Dashboard is disabled. Running in local mode.")
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
        except Exception as e:
            await interaction.followup.send(f"❌ Sync error: {str(e)}")

    async def _status_command(self, interaction: discord.Interaction):
        """Check bot and dashboard status."""
        await interaction.response.defer()
        
        if not self.dashboard_enabled:
            await interaction.followup.send("ℹ️ Bot Status: 🟢 Online (Dashboard disabled)")
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
        except Exception as e:
            await interaction.followup.send(f"❌ Status check failed: {str(e)}")

    async def _addpick_command(self, interaction: discord.Interaction, pick_type: str, pick_number: int, bet_details: str):
        """Add a new pick to the dashboard."""
        await interaction.response.defer()
        
        if not self.dashboard_enabled:
            await interaction.followup.send("ℹ️ Dashboard is disabled. Cannot add picks.")
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
        except Exception as e:
            await interaction.followup.send(f"❌ Error adding pick: {str(e)}")

    async def _force_sync_command(self, interaction: discord.Interaction):
        """Force sync all commands."""
        await interaction.response.defer()
        try:
            synced = await self.tree.sync()
            await interaction.followup.send(f"✅ Force synced {len(synced)} command(s)")
        except Exception as e:
            await interaction.followup.send(f"❌ Force sync failed: {e}")

    async def _post_pick_with_analysis(self, interaction: discord.Interaction, image: discord.Attachment, context: str, pick_type: str, channel_id: Optional[int] = None):
        """Post a pick with analysis to the specified channel."""
        # Check if interaction has already been responded to
        if interaction.response.is_done():
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
                text = extract_text_from_image(image_bytes)
            except Exception as e:
                await interaction.followup.send(f"❌ OCR failed: {str(e)}", ephemeral=True)
                return
            
            if not text.strip():
                await interaction.followup.send(
                    "❌ Could not extract text from the image. Please ensure the image is clear and readable.",
                    ephemeral=True
                )
                return
            
            # Parse bet details
            bet_details = parse_bet_details(text)
            if not bet_details:
                await interaction.followup.send(
                    "❌ Could not parse betting details from the image. Please ensure it's a valid betting slip.",
                    ephemeral=True
                )
                return
            
            # AI: Analyze bet slip
            try:
                analysis = await analyze_bet_slip(bet_details, context)
            except Exception as e:
                await interaction.followup.send(f"❌ AI analysis failed: {str(e)}", ephemeral=True)
                return
            
            # Validate analysis quality
            try:
                validation = await validate_analysis_quality(analysis)
            except Exception as e:
                validation = {"status": f"Validation error: {str(e)}"}
            
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
                    
        except Exception as e:
            logger.exception("Error in _post_pick_with_analysis")
            await interaction.followup.send(f"❌ An error occurred while posting the pick: {str(e)}", ephemeral=True)

    async def _create_analysis_embed(self, bet_details, analysis, validation):
        """Create an embed for bet analysis results."""
        embed = discord.Embed(
            title="🔍 Bet Analysis Results",
            description="AI-powered betting slip analysis",
            color=discord.Color.blue()
        )
        
        # Add bet details
        if bet_details:
            embed.add_field(
                name="📋 Bet Details",
                value=f"```{json.dumps(bet_details, indent=2)}```",
                inline=False
            )
        
        # Add analysis results
        if analysis:
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
        
        # Add validation results
        if validation:
            embed.add_field(
                name="✅ Validation",
                value=validation.get('status', 'Unknown'),
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
