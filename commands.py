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


class BotLogger:
    """Handles logging bot events to Discord channels."""
    
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = getattr(bot, 'log_channel_id', None)
        self.log_level = getattr(bot, 'log_level', 'INFO')
    
    async def log_event(self, level: str, title: str, description: str, fields: Optional[Dict[str, str]] = None, color: int = 0x00ff00):
        """Log an event to the designated logging channel."""
        if not self.log_channel_id or level not in ['INFO', 'WARNING', 'ERROR', 'SUCCESS']:
            return
        
        try:
            channel = self.bot.get_channel(self.log_channel_id)
            if not channel:
                logger.warning(f"Log channel {self.log_channel_id} not found")
                return
            
            # Color mapping
            colors = {
                'INFO': 0x0099ff,
                'WARNING': 0xffaa00,
                'ERROR': 0xff0000,
                'SUCCESS': 0x00ff00
            }
            
            embed = discord.Embed(
                title=f"📝 {title}",
                description=description,
                color=colors.get(level, color),
                timestamp=datetime.now()
            )
            
            if fields:
                for name, value in fields.items():
                    embed.add_field(name=name, value=value, inline=True)
            
            embed.set_footer(text=f"GotLockz Bot • {level}")
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Failed to log to Discord channel: {e}")
    
    async def log_command(self, interaction: discord.Interaction, command_name: str, success: bool = True, error: Optional[str] = None):
        """Log command usage."""
        if not success:
            await self.log_event(
                'ERROR',
                f"Command Error: /{command_name}",
                f"Command failed for {interaction.user}",
                {
                    'User': f"{interaction.user} ({interaction.user.id})",
                    'Channel': f"{interaction.channel} ({interaction.channel_id})",
                    'Error': error or 'Unknown error'
                }
            )
        else:
            await self.log_event(
                'SUCCESS',
                f"Command Used: /{command_name}",
                f"Command executed successfully by {interaction.user}",
                {
                    'User': f"{interaction.user} ({interaction.user.id})",
                    'Channel': f"{interaction.channel} ({interaction.channel_id})",
                    'Guild': f"{interaction.guild} ({interaction.guild_id})"
                }
            )
    
    async def log_pick_posted(self, interaction: discord.Interaction, pick_type: str, analysis_enabled: bool = False):
        """Log when a pick is posted."""
        await self.log_event(
            'SUCCESS',
            f"Pick Posted: {pick_type.upper()}",
            f"New {pick_type} pick posted by {interaction.user}",
            {
                'User': f"{interaction.user} ({interaction.user.id})",
                'Channel': f"{interaction.channel} ({interaction.channel_id})",
                'Analysis': '✅ Enabled' if analysis_enabled else '❌ Disabled',
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        )
    
    async def log_bot_status(self, status: str, details: Optional[str] = None):
        """Log bot status changes."""
        await self.log_event(
            'INFO',
            f"Bot Status: {status}",
            details or f"Bot status changed to {status}",
            {
                'Status': status,
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Guilds': str(len(self.bot.guilds)),
                'Users': str(len(self.bot.users))
            }
        )


class GotLockzCommands(app_commands.Group):
    """GotLockz Bot slash commands."""
    
    def __init__(self, bot):
        super().__init__(name="gotlockz", description="GotLockz Bot commands")
        self.bot = bot
        self.logger = BotLogger(bot)

    @app_commands.command(name="ping", description="Test bot responsiveness")
    async def ping(self, interaction: discord.Interaction):
        """Test bot responsiveness"""
        try:
            await interaction.response.send_message("🏓 Pong! Bot is online!")
            await self.logger.log_command(interaction, "ping", success=True)
        except Exception as e:
            await self.logger.log_command(interaction, "ping", success=False, error=str(e))
            raise

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
                      f"Analysis: {self.bot.analysis_channel_id or 'Not set'}\n"
                      f"Log: {self.bot.log_channel_id or 'Not set'}",
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
            await self.logger.log_command(interaction, "debug", success=True)
            
        except discord.errors.NotFound:
            logger.warning("Interaction expired before bot could respond")
        except Exception as e:
            logger.exception("Error in debug command")
            await self.logger.log_command(interaction, "debug", success=False, error=str(e))
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
                      f"Channels: {'✅' if self.bot.channels_configured else '❌'}\n"
                      f"Logging: {'✅' if self.bot.log_channel_id else '❌'}",
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
            await self.logger.log_command(interaction, "stats", success=True)
            
        except discord.errors.NotFound:
            logger.warning("Interaction expired before bot could respond")
        except Exception as e:
            logger.exception("Error in stats command")
            await self.logger.log_command(interaction, "stats", success=False, error=str(e))
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
                await self.logger.log_command(interaction, "status", success=True)
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
                await self.logger.log_command(interaction, "status", success=True)
            else:
                await interaction.followup.send("❌ Dashboard not responding")
                await self.logger.log_command(interaction, "status", success=False, error="Dashboard not responding")
        except requests.exceptions.ConnectionError:
            await interaction.followup.send("❌ Cannot connect to dashboard. Check DASHBOARD_URL setting.")
            await self.logger.log_command(interaction, "status", success=False, error="Dashboard connection failed")
        except discord.errors.NotFound:
            logger.warning("Interaction expired before bot could respond")
        except Exception as e:
            await self.logger.log_command(interaction, "status", success=False, error=str(e))
            try:
                await interaction.followup.send(f"❌ Status check failed: {str(e)}")
            except discord.errors.NotFound:
                pass

    @app_commands.command(name="help", description="Show all available commands and their usage")
    @app_commands.describe(
        category="Category of commands to show (betting, admin, info, or all)",
        command="Specific command to get detailed help for"
    )
    async def help_command(self, interaction: discord.Interaction, category: Optional[str] = None, command: Optional[str] = None):
        """Show help information for bot commands."""
        await interaction.response.defer(thinking=True)
        
        try:
            # Define command categories
            command_categories = {
                "betting": {
                    "name": "🎯 Betting Commands",
                    "description": "Commands for posting and analyzing betting picks",
                    "commands": {
                        "vip": {"description": "Post a VIP pick with analysis", "usage": "/vip [image] [context]"},
                        "lotto": {"description": "Post a lotto pick with analysis", "usage": "/lotto [image] [context]"},
                        "free": {"description": "Post a free pick with analysis", "usage": "/free [image] [context]"},
                        "analyze": {"description": "Analyze a betting slip image", "usage": "/analyze [image] [context]"},
                        "history": {"description": "View pick history", "usage": "/history [pick_type] [limit]"}
                    }
                },
                "admin": {
                    "name": "⚙️ Admin Commands",
                    "description": "Administrative and management commands",
                    "commands": {
                        "force_sync": {"description": "Force sync all commands", "usage": "/force_sync"},
                        "debug": {"description": "Debug bot status and configuration", "usage": "/debug"},
                        "status": {"description": "Check bot and dashboard status", "usage": "/status"}
                    }
                },
                "info": {
                    "name": "ℹ️ Info Commands",
                    "description": "Information and utility commands",
                    "commands": {
                        "ping": {"description": "Test bot responsiveness", "usage": "/ping"},
                        "stats": {"description": "View bot statistics", "usage": "/stats"},
                        "help": {"description": "Show this help message", "usage": "/help [category] [command]"}
                    }
                }
            }
            
            # If specific command requested
            if command:
                for cat_name, cat_data in command_categories.items():
                    if command in cat_data["commands"]:
                        cmd_info = cat_data["commands"][command]
                        embed = discord.Embed(
                            title=f"📖 Help: /{command}",
                            description=cmd_info["description"],
                            color=0x00ff00
                        )
                        embed.add_field(name="Usage", value=f"`{cmd_info['usage']}`", inline=False)
                        embed.add_field(name="Category", value=cat_data["name"], inline=True)
                        embed.set_footer(text="GotLockz Bot • Use /help to see all commands")
                        await interaction.followup.send(embed=embed)
                        await self.logger.log_command(interaction, "help", success=True)
                        return
                
                # Command not found
                await interaction.followup.send(f"❌ Command `/{command}` not found. Use `/help` to see all available commands.", ephemeral=True)
                await self.logger.log_command(interaction, "help", success=False, error=f"Command {command} not found")
                return
            
            # If specific category requested
            if category and category.lower() in command_categories:
                cat_data = command_categories[category.lower()]
                embed = discord.Embed(
                    title=cat_data["name"],
                    description=cat_data["description"],
                    color=0x00ff00
                )
                
                for cmd_name, cmd_info in cat_data["commands"].items():
                    embed.add_field(
                        name=f"/{cmd_name}",
                        value=f"{cmd_info['description']}\n`{cmd_info['usage']}`",
                        inline=False
                    )
                
                embed.set_footer(text="GotLockz Bot • Use /help [command] for detailed help")
                await interaction.followup.send(embed=embed)
                await self.logger.log_command(interaction, "help", success=True)
                return
            
            # Show all categories
            embed = discord.Embed(
                title="🤖 GotLockz Bot Help",
                description="Welcome to GotLockz Bot! Here are all available commands organized by category.",
                color=0x00ff00
            )
            
            for cat_name, cat_data in command_categories.items():
                commands_list = []
                for cmd_name, cmd_info in cat_data["commands"].items():
                    commands_list.append(f"`/{cmd_name}` - {cmd_info['description']}")
                
                embed.add_field(
                    name=cat_data["name"],
                    value="\n".join(commands_list[:3]) + ("\n..." if len(commands_list) > 3 else ""),
                    inline=False
                )
            
            embed.add_field(
                name="📚 Usage",
                value="• `/help` - Show this overview\n• `/help [category]` - Show commands in a category\n• `/help [command]` - Get detailed help for a command",
                inline=False
            )
            
            embed.set_footer(text="GotLockz Bot • AI-Powered Betting Analysis")
            await interaction.followup.send(embed=embed)
            await self.logger.log_command(interaction, "help", success=True)
            
        except Exception as e:
            logger.exception("Error in help command")
            await self.logger.log_command(interaction, "help", success=False, error=str(e))
            await interaction.followup.send(f"❌ Error showing help: {str(e)}", ephemeral=True)

    @app_commands.command(name="about", description="Show information about the bot")
    async def about_command(self, interaction: discord.Interaction):
        """Show information about the bot."""
        await interaction.response.defer(thinking=True)
        
        try:
            embed = discord.Embed(
                title="🤖 About GotLockz Bot",
                description="AI-powered betting analysis and pick management bot",
                color=0x00ff00
            )
            
            # Bot info
            embed.add_field(
                name="📊 Bot Statistics",
                value=f"**Servers:** {len(self.bot.guilds)}\n"
                      f"**Users:** {len(self.bot.users)}\n"
                      f"**Latency:** {round(self.bot.latency * 1000)}ms\n"
                      f"**Uptime:** {self._get_uptime()}",
                inline=True
            )
            
            # Features
            embed.add_field(
                name="🚀 Features",
                value="• **OCR Analysis** - Extract text from betting slips\n"
                      "• **AI Analysis** - AI-powered betting recommendations\n"
                      "• **Pick Management** - Organize VIP, Lotto, and Free picks\n"
                      "• **Dashboard Integration** - Real-time analytics\n"
                      "• **Channel Management** - Dedicated channels for different pick types\n"
                      "• **Logging System** - Comprehensive event logging",
                inline=False
            )
            
            # Technical info
            embed.add_field(
                name="⚙️ Technical",
                value=f"**Python:** 3.9+\n"
                      f"**Discord.py:** {discord.__version__}\n"
                      f"**Analysis:** {'✅ Enabled' if getattr(self.bot, 'ANALYSIS_ENABLED', False) else '❌ Disabled'}\n"
                      f"**Dashboard:** {'✅ Connected' if self.bot.dashboard_enabled else '❌ Disabled'}\n"
                      f"**Logging:** {'✅ Enabled' if self.bot.log_channel_id else '❌ Disabled'}",
                inline=True
            )
            
            embed.set_footer(text="GotLockz Bot • Built with AI and ❤️")
            embed.timestamp = datetime.now()
            
            await interaction.followup.send(embed=embed)
            await self.logger.log_command(interaction, "about", success=True)
            
        except Exception as e:
            logger.exception("Error in about command")
            await self.logger.log_command(interaction, "about", success=False, error=str(e))
            await interaction.followup.send(f"❌ Error showing about info: {str(e)}", ephemeral=True)
    
    def _get_uptime(self) -> str:
        """Get bot uptime as a formatted string."""
        uptime = datetime.now() - self.bot.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"

    @app_commands.command(name="setup_logging", description="Set up logging channel for bot events")
    @app_commands.describe(
        channel="The channel where bot events should be logged"
    )
    async def setup_logging_command(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Set up logging channel for bot events."""
        # Check if user has admin permissions
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return
            
        member = interaction.guild.get_member(interaction.user.id)
        if not member or not member.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need administrator permissions to set up logging.", ephemeral=True)
            return
        
        await interaction.response.defer(thinking=True)
        
        try:
            # Update bot's log channel
            self.bot.log_channel_id = channel.id
            
            # Send test log message
            logger_instance = BotLogger(self.bot)
            await logger_instance.log_event(
                'INFO',
                'Logging Setup',
                f'Logging channel configured by {interaction.user}',
                {
                    'Channel': f"{channel.name} ({channel.id})",
                    'Guild': f"{interaction.guild.name} ({interaction.guild.id})",
                    'Configured By': f"{interaction.user} ({interaction.user.id})"
                }
            )
            
            embed = discord.Embed(
                title="✅ Logging Setup Complete",
                description=f"Bot events will now be logged to {channel.mention}",
                color=0x00ff00
            )
            embed.add_field(name="Channel", value=f"{channel.name} ({channel.id})", inline=True)
            embed.add_field(name="Configured By", value=interaction.user.mention, inline=True)
            embed.add_field(name="Test Message", value="✅ A test log message has been sent to the channel", inline=False)
            
            await interaction.followup.send(embed=embed)
            await self.logger.log_command(interaction, "setup_logging", success=True)
            
        except Exception as e:
            logger.exception("Error setting up logging")
            await self.logger.log_command(interaction, "setup_logging", success=False, error=str(e))
            await interaction.followup.send(f"❌ Error setting up logging: {str(e)}", ephemeral=True)


class BettingCommands(app_commands.Group):
    """Betting-related slash commands."""
    
    def __init__(self, bot):
        super().__init__(name="betting", description="Betting analysis and pick management")
        self.bot = bot
        self.pick_counters = self._load_counters()
        self.logger = BotLogger(bot)

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
                await self.logger.log_command(interaction, "analyze", success=False, error="Wrong channel")
                return
        
        await interaction.response.defer(thinking=True)
        
        try:
            # Validate image
            if not image.content_type or not image.content_type.startswith('image/'):
                await interaction.followup.send("❌ Please upload a valid image file!", ephemeral=True)
                await self.logger.log_command(interaction, "analyze", success=False, error="Invalid image file")
                return
            
            # Download image
            image_bytes = await image.read()
            
            # OCR: Extract text from image
            try:
                if getattr(self.bot, 'ANALYSIS_ENABLED', False):
                    extracted_text = extract_text_from_image(image_bytes)
                    if not extracted_text:
                        await interaction.followup.send("❌ Could not extract text from the image. Please ensure the image is clear and contains readable text.", ephemeral=True)
                        await self.logger.log_command(interaction, "analyze", success=False, error="OCR failed - no text extracted")
                        return
                    
                    # Parse bet details
                    bet_details = parse_bet_details(extracted_text)
                    
                    # AI Analysis
                    analysis_result = await analyze_bet_slip(bet_details or {}, context)
                    
                    # Validate analysis quality
                    validation = await validate_analysis_quality(analysis_result)
                    
                    # Create embed
                    embed = await self._create_analysis_embed(bet_details or {}, analysis_result, validation)
                    
                    await interaction.followup.send(embed=embed)
                    await self.logger.log_command(interaction, "analyze", success=True)
                    
                else:
                    # Fallback without analysis
                    embed = discord.Embed(
                        title="📊 Bet Analysis (Basic)",
                        description="AI analysis is currently disabled. Here's the basic image info:",
                        color=0x00ff00
                    )
                    embed.add_field(name="Image Info", value=f"Size: {len(image_bytes)} bytes\nType: {image.content_type}", inline=True)
                    embed.add_field(name="Context", value=context or "No context provided", inline=True)
                    embed.set_footer(text="Enable AI analysis for detailed betting insights")
                    
                    await interaction.followup.send(embed=embed)
                    await self.logger.log_command(interaction, "analyze", success=True)
                    
            except Exception as e:
                logger.exception("Error in analysis")
                await interaction.followup.send(f"❌ Analysis failed: {str(e)}", ephemeral=True)
                await self.logger.log_command(interaction, "analyze", success=False, error=str(e))
                
        except Exception as e:
            logger.exception("Error in analyze command")
            await self.logger.log_command(interaction, "analyze", success=False, error=str(e))
            await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

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
        await self._post_pick(interaction, image, context, "vip", self.bot.vip_channel_id)

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
        await self._post_pick(interaction, image, context, "lotto", self.bot.lotto_channel_id)

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
        await self._post_pick(interaction, image, context, "free", self.bot.free_channel_id)

    async def _post_pick(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        context: Optional[str],
        pick_type: str,
        channel_id: Optional[int] = None
    ):
        """Post a pick to the appropriate channel."""
        
        # Check if command is used in the correct channel
        if hasattr(self.bot, 'channels_configured') and self.bot.channels_configured:
            if channel_id and interaction.channel_id != channel_id:
                channel_name = "VIP" if pick_type == "vip" else "Lotto" if pick_type == "lotto" else "Free"
                await interaction.response.send_message(
                    f"❌ This command can only be used in the {channel_name} channel!",
                    ephemeral=True
                )
                await self.logger.log_command(interaction, pick_type, success=False, error=f"Wrong channel - expected {channel_name}")
                return
        
        await interaction.response.defer(thinking=True)
        
        try:
            # Validate image
            if not image.content_type or not image.content_type.startswith('image/'):
                await interaction.followup.send("❌ Please upload a valid image file!", ephemeral=True)
                await self.logger.log_command(interaction, pick_type, success=False, error="Invalid image file")
                return
            
            # Download image
            image_bytes = await image.read()
            
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
            
            # Add analysis if enabled
            analysis_enabled = getattr(self.bot, 'ANALYSIS_ENABLED', False)
            if analysis_enabled:
                try:
                    # OCR and AI analysis
                    extracted_text = extract_text_from_image(image_bytes)
                    if extracted_text:
                        bet_details = parse_bet_details(extracted_text)
                        analysis_result = await analyze_bet_slip(bet_details or {}, context)
                        
                        # Add analysis to embed
                        analysis_text = ""
                        if isinstance(analysis_result, dict):
                            if 'recommendation' in analysis_result:
                                rec = analysis_result['recommendation']
                                analysis_text += f"**Recommendation:** {rec.get('action', 'Unknown')}\n"
                                analysis_text += f"**Reasoning:** {rec.get('reasoning', 'N/A')[:200]}...\n\n"
                            
                            if 'confidence_rating' in analysis_result:
                                conf = analysis_result['confidence_rating']
                                analysis_text += f"**Confidence:** {conf.get('score', 0)}/10\n"
                                analysis_text += f"**Reasoning:** {conf.get('reasoning', 'N/A')[:200]}...\n\n"
                            
                            if 'risk_assessment' in analysis_result:
                                risk = analysis_result['risk_assessment']
                                analysis_text += f"**Risk Level:** {risk.get('level', 'Unknown')}\n"
                                analysis_text += f"**Reasoning:** {risk.get('reasoning', 'N/A')[:200]}...\n\n"
                            
                            if 'edge_analysis' in analysis_result:
                                edge = analysis_result['edge_analysis']
                                analysis_text += f"**Edge:** {edge.get('edge_percentage', 0):.2f}%\n"
                                analysis_text += f"**Explanation:** {edge.get('explanation', 'N/A')[:200]}...\n\n"
                        else:
                            analysis_text = str(analysis_result)
                        
                        embed.add_field(
                            name="🤖 AI Analysis",
                            value=analysis_text[:1024] + "..." if len(analysis_text) > 1024 else analysis_text,
                            inline=False
                        )
                        
                        # Add bet details if available
                        if bet_details:
                            details_text = f"**Sport:** {bet_details.get('sport', 'Unknown')}\n"
                            details_text += f"**Teams:** {bet_details.get('teams', 'Unknown')}\n"
                            details_text += f"**Bet Type:** {bet_details.get('bet_type', 'Unknown')}\n"
                            details_text += f"**Odds:** {bet_details.get('odds', 'Unknown')}"
                            
                            embed.add_field(
                                name="📊 Bet Details",
                                value=details_text,
                                inline=True
                            )
                except Exception as e:
                    logger.warning(f"Analysis failed for {pick_type} pick: {e}")
                    embed.add_field(
                        name="⚠️ Analysis Note",
                        value="AI analysis was attempted but failed. Basic pick posted.",
                        inline=False
                    )
            
            embed.set_footer(text=f"GotLockz Bot • {pick_type.upper()} Pick")
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            
            # Send to channel
            await interaction.followup.send(embed=embed)
            
            # Log the pick
            await self.logger.log_pick_posted(interaction, pick_type, analysis_enabled)
            await self.logger.log_command(interaction, pick_type, success=True)
            
            # Sync to dashboard if enabled
            if self.bot.dashboard_enabled:
                try:
                    pick_data = {
                        "type": pick_type,
                        "user": interaction.user.display_name,
                        "user_id": interaction.user.id,
                        "context": context,
                        "image_url": image.url,
                        "timestamp": datetime.now().isoformat(),
                        "analysis_enabled": analysis_enabled
                    }
                    
                    response = requests.post(
                        f"{self.bot.dashboard_url}/run/api_sync_pick",
                        json={"data": [json.dumps(pick_data)]},
                        timeout=10
                    )
                    
                    if response.status_code != 200:
                        logger.warning(f"Failed to sync pick to dashboard: {response.status_code}")
                        
                except Exception as e:
                    logger.warning(f"Error syncing pick to dashboard: {e}")
                    
        except Exception as e:
            logger.exception(f"Error in {pick_type} command")
            await self.logger.log_command(interaction, pick_type, success=False, error=str(e))
            await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

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
        analysis: Dict[str, Any],
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
        
        # Analysis results - convert dict to readable format
        analysis_text = ""
        if isinstance(analysis, dict):
            if 'recommendation' in analysis:
                rec = analysis['recommendation']
                analysis_text += f"**Recommendation:** {rec.get('action', 'Unknown')}\n"
                analysis_text += f"**Reasoning:** {rec.get('reasoning', 'N/A')[:200]}...\n\n"
            
            if 'confidence_rating' in analysis:
                conf = analysis['confidence_rating']
                analysis_text += f"**Confidence:** {conf.get('score', 0)}/10\n"
                analysis_text += f"**Reasoning:** {conf.get('reasoning', 'N/A')[:200]}...\n\n"
            
            if 'risk_assessment' in analysis:
                risk = analysis['risk_assessment']
                analysis_text += f"**Risk Level:** {risk.get('level', 'Unknown')}\n"
                analysis_text += f"**Reasoning:** {risk.get('reasoning', 'N/A')[:200]}...\n\n"
            
            if 'edge_analysis' in analysis:
                edge = analysis['edge_analysis']
                analysis_text += f"**Edge:** {edge.get('edge_percentage', 0):.2f}%\n"
                analysis_text += f"**Explanation:** {edge.get('explanation', 'N/A')[:200]}...\n\n"
        else:
            analysis_text = str(analysis)
        
        embed.add_field(
            name="🤖 AI Analysis",
            value=analysis_text[:1024] + "..." if len(analysis_text) > 1024 else analysis_text,
            inline=False
        )
        
        # Validation status
        validation_text = f"**Valid:** {'✅' if validation.get('is_valid', False) else '❌'}\n"
        validation_text += f"**Quality Score:** {validation.get('quality_score', 0)}%\n"
        if validation.get('warnings'):
            validation_text += f"**Warnings:** {', '.join(validation['warnings'])}"
        
        embed.add_field(
            name="✅ Validation",
            value=validation_text,
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
