# commands.py

#!/usr/bin/env python3
"""
commands.py

Discord slash commands for the GotLockz bot.
Includes enhanced commands for betting analysis, pick management,
and administrative functions with production-grade safety features.
"""
import logging
import json
import asyncio
import functools
import aiofiles
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timedelta
import psutil
import os

import discord
from discord import app_commands
from discord.ext import commands
import requests

# Import config if available, otherwise use environment variables
try:
    from config import (
        GUILD_ID, ANALYSIS_CHANNEL_ID, VIP_CHANNEL_ID, 
        LOTTO_CHANNEL_ID, FREE_CHANNEL_ID, OWNER_ID
    )
except ImportError:
    # Fallback to environment variables
    GUILD_ID = int(os.getenv('GUILD_ID', 0))
    ANALYSIS_CHANNEL_ID = int(os.getenv('ANALYSIS_CHANNEL_ID', 0))
    VIP_CHANNEL_ID = int(os.getenv('VIP_CHANNEL_ID', 0))
    LOTTO_CHANNEL_ID = int(os.getenv('LOTTO_CHANNEL_ID', 0))
    FREE_CHANNEL_ID = int(os.getenv('FREE_CHANNEL_ID', 0))
    OWNER_ID = int(os.getenv('OWNER_ID', 0))

logger = logging.getLogger(__name__)


class PermissionError(Exception):
    """Custom exception for permission errors."""
    pass


class CooldownError(Exception):
    """Custom exception for cooldown errors."""
    pass


class PermissionsManager:
    """Manages role and user-based permissions for commands."""
    
    def __init__(self, bot):
        self.bot = bot
        self.vip_roles = self._load_vip_roles()
        self.admin_roles = self._load_admin_roles()
        self.blocked_users = self._load_blocked_users()
        self.cooldowns = {}  # {user_id: {command: last_used_time}}
    
    def _load_vip_roles(self) -> List[int]:
        """Load VIP role IDs from environment or config."""
        vip_roles_str = os.getenv('VIP_ROLE_IDS', '')
        if vip_roles_str:
            return [int(role_id.strip()) for role_id in vip_roles_str.split(',') if role_id.strip()]
        return []
    
    def _load_admin_roles(self) -> List[int]:
        """Load admin role IDs from environment or config."""
        admin_roles_str = os.getenv('ADMIN_ROLE_IDS', '')
        if admin_roles_str:
            return [int(role_id.strip()) for role_id in admin_roles_str.split(',') if role_id.strip()]
        return []
    
    def _load_blocked_users(self) -> List[int]:
        """Load blocked user IDs from environment or config."""
        blocked_users_str = os.getenv('BLOCKED_USER_IDS', '')
        if blocked_users_str:
            return [int(user_id.strip()) for user_id in blocked_users_str.split(',') if user_id.strip()]
        return []
    
    def has_vip_role(self, member: discord.Member) -> bool:
        """Check if member has VIP role."""
        if not member:
            return False
        
        # Check if user is owner
        if member.id == OWNER_ID:
            return True
        
        # Check VIP roles
        member_role_ids = [role.id for role in member.roles]
        return any(role_id in member_role_ids for role_id in self.vip_roles)
    
    def has_admin_role(self, member: discord.Member) -> bool:
        """Check if member has admin role."""
        if not member:
            return False
        
        # Check if user is owner
        if member.id == OWNER_ID:
            return True
        
        # Check admin roles
        member_role_ids = [role.id for role in member.roles]
        return any(role_id in member_role_ids for role_id in self.admin_roles)
    
    def is_blocked(self, user_id: int) -> bool:
        """Check if user is blocked."""
        return user_id in self.blocked_users
    
    def check_cooldown(self, user_id: int, command: str, cooldown_seconds: int) -> bool:
        """Check if user is on cooldown for a command."""
        if user_id not in self.cooldowns:
            self.cooldowns[user_id] = {}
        
        if command not in self.cooldowns[user_id]:
            return True  # No cooldown recorded, allow command
        
        last_used = self.cooldowns[user_id][command]
        time_since_last = (datetime.now() - last_used).total_seconds()
        
        return time_since_last >= cooldown_seconds
    
    def set_cooldown(self, user_id: int, command: str):
        """Set cooldown for user and command."""
        if user_id not in self.cooldowns:
            self.cooldowns[user_id] = {}
        
        self.cooldowns[user_id][command] = datetime.now()


def require_vip():
    """Decorator to require VIP role for commands."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            # Check if user is blocked
            if self.bot.permissions.is_blocked(interaction.user.id):
                await interaction.response.send_message(
                    "❌ You are blocked from using this bot.", 
                    ephemeral=True
                )
                return
            
            # Check VIP permissions
            member = None
            if interaction.guild:
                member = interaction.guild.get_member(interaction.user.id)
            if not member or not self.bot.permissions.has_vip_role(member):
                await interaction.response.send_message(
                    "❌ This command requires VIP access. Please contact an administrator.", 
                    ephemeral=True
                )
                return
            
            # Check cooldown
            cooldown_seconds = 30  # 30 seconds for VIP commands
            if not self.bot.permissions.check_cooldown(interaction.user.id, func.__name__, cooldown_seconds):
                remaining = cooldown_seconds - (datetime.now() - self.bot.permissions.cooldowns[interaction.user.id][func.__name__]).total_seconds()
                await interaction.response.send_message(
                    f"⏰ Please wait {remaining:.1f} seconds before using this command again.", 
                    ephemeral=True
                )
                return
            
            # Set cooldown
            self.bot.permissions.set_cooldown(interaction.user.id, func.__name__)
            
            # Execute command
            try:
                return await func(self, interaction, *args, **kwargs)
            except Exception as e:
                await self.bot.logger.log_command(interaction, func.__name__, success=False, error=str(e))
                raise
        return wrapper
    return decorator


def require_admin():
    """Decorator to require admin role for commands."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            # Check if user is blocked
            if self.bot.permissions.is_blocked(interaction.user.id):
                await interaction.response.send_message(
                    "❌ You are blocked from using this bot.", 
                    ephemeral=True
                )
                return
            
            # Check admin permissions
            member = None
            if interaction.guild:
                member = interaction.guild.get_member(interaction.user.id)
            if not member or not self.bot.permissions.has_admin_role(member):
                await interaction.response.send_message(
                    "❌ This command requires administrator access.", 
                    ephemeral=True
                )
                return
            
            # Execute command
            try:
                return await func(self, interaction, *args, **kwargs)
            except Exception as e:
                await self.bot.logger.log_command(interaction, func.__name__, success=False, error=str(e))
                raise
        return wrapper
    return decorator


def validate_input(func):
    """Decorator to validate command input."""
    @functools.wraps(func)
    async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
        try:
            # Validate interaction
            if not interaction or not interaction.user:
                raise ValueError("Invalid interaction")
            
            # Validate guild context for guild-specific commands
            if hasattr(func, '__guild_required__') and func.__guild_required__:
                if not interaction.guild:
                    await interaction.response.send_message(
                        "❌ This command can only be used in a server.", 
                        ephemeral=True
                    )
                    return
            
            # Execute command
            return await func(self, interaction, *args, **kwargs)
            
        except ValueError as e:
            await interaction.response.send_message(
                f"❌ Invalid input: {str(e)}", 
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ An error occurred: {str(e)}", 
                ephemeral=True
            )
            raise
    
    return wrapper


class BotLogger:
    """Handles logging bot events to Discord channels and files."""
    
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = getattr(bot, 'log_channel_id', None)
        self.log_level = getattr(bot, 'log_level', 'INFO')
        self.log_file = 'bot_logs.txt'
        self.setup_file_logging()
    
    def setup_file_logging(self):
        """Setup file logging for debugging."""
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    async def log_event(self, level: str, title: str, description: str, fields: Optional[Dict[str, str]] = None, color: int = 0x00ff00):
        """Log an event to the designated logging channel and file."""
        # Log to file
        log_message = f"{level}: {title} - {description}"
        if fields:
            log_message += f" | Fields: {fields}"
        logger.info(log_message)
        
        # Log to Discord channel if configured
        if not self.log_channel_id:
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
        """Log command usage with detailed information."""
        # Log to file
        def safe_id(val):
            try:
                return int(val)
            except Exception:
                try:
                    return str(val)
                except Exception:
                    return None
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'user_id': safe_id(getattr(interaction.user, 'id', None)),
            'user_name': str(getattr(interaction.user, 'name', getattr(interaction.user, 'display_name', 'Unknown'))),
            'command': command_name,
            'guild_id': safe_id(getattr(getattr(interaction, 'guild', None), 'id', None)),
            'guild_name': str(getattr(getattr(interaction, 'guild', None), 'name', 'None')),
            'channel_id': safe_id(getattr(interaction, 'channel_id', None)),
            'channel_name': str(getattr(interaction, 'channel', 'None')),
            'success': success,
            'error': error
        }
        try:
            logger.info(f"Command executed: {json.dumps(log_data)}")
        except TypeError:
            logger.info(f"Command executed (fallback): {str(log_data)}")
        
        # Log to Discord
        if not success:
            await self.log_event(
                'ERROR',
                f"Command Error: /{command_name}",
                f"Command failed for {getattr(interaction, 'user', 'Unknown')}",
                {
                    'User': f"{getattr(interaction, 'user', 'Unknown')} ({safe_id(getattr(getattr(interaction, 'user', None), 'id', None))})",
                    'Channel': f"{getattr(interaction, 'channel', 'Unknown')} ({safe_id(getattr(interaction, 'channel_id', None))})",
                    'Error': error or 'Unknown error'
                }
            )
        else:
            await self.log_event(
                'SUCCESS',
                f"Command Used: /{command_name}",
                f"Command executed successfully by {getattr(interaction, 'user', 'Unknown')}",
                {
                    'User': f"{getattr(interaction, 'user', 'Unknown')} ({safe_id(getattr(getattr(interaction, 'user', None), 'id', None))})",
                    'Channel': f"{getattr(interaction, 'channel', 'Unknown')} ({safe_id(getattr(interaction, 'channel_id', None))})",
                    'Guild': f"{getattr(interaction, 'guild', 'Unknown')} ({safe_id(getattr(getattr(interaction, 'guild', None), 'id', None))})" if getattr(interaction, 'guild', None) else 'DM'
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
    
    async def log_heartbeat(self, cpu_percent: float, memory_percent: float, uptime: str):
        """Log heartbeat with system metrics."""
        await self.log_event(
            'INFO',
            'Bot Heartbeat',
            'Bot is running normally',
            {
                'CPU Usage': f"{cpu_percent:.1f}%",
                'Memory Usage': f"{memory_percent:.1f}%",
                'Uptime': uptime,
                'Guilds': str(len(self.bot.guilds)),
                'Latency': f"{round(self.bot.latency * 1000)}ms"
            }
        )
    
    def log_exception(self, error: Exception, context: str = ""):
        """Log exceptions with full traceback."""
        logger.exception(f"Exception in {context}: {str(error)}")
        
        # Also log to file with timestamp
        with open('error_logs.txt', 'a') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Context: {context}\n")
            f.write(f"Error: {str(error)}\n")
            f.write(f"Traceback:\n")
            import traceback
            f.write(traceback.format_exc())
            f.write(f"{'='*50}\n")


class GotLockzCommands(app_commands.Group):
    """GotLockz Bot slash commands with production-grade safety features."""
    
    def __init__(self, bot):
        super().__init__(name="gotlockz", description="GotLockz Bot commands")
        self.bot = bot
        self.logger = BotLogger(bot)

    @app_commands.command(name="ping", description="Test bot responsiveness")
    @validate_input
    async def ping(self, interaction: discord.Interaction):
        """Test bot responsiveness"""
        try:
            await interaction.response.send_message("🏓 Pong! Bot is online!")
            await self.logger.log_command(interaction, "ping", success=True)
        except Exception as e:
            await self.logger.log_command(interaction, "ping", success=False, error=str(e))
            raise

    @app_commands.command(name="status", description="Show detailed bot status and system metrics")
    @validate_input
    async def status_command(self, interaction: discord.Interaction):
        """Show detailed bot status with system metrics."""
        await interaction.response.defer(thinking=True)
        
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Calculate uptime
            uptime = datetime.now() - self.bot.start_time
            uptime_str = self._format_uptime(uptime)
            
            # Create status embed
            embed = discord.Embed(
                title="🤖 Bot Status & System Metrics",
                description="Comprehensive bot health and system information",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            
            # Bot status
            embed.add_field(
                name="🟢 Bot Status",
                value=f"**Status:** Online\n"
                      f"**Latency:** {round(self.bot.latency * 1000)}ms\n"
                      f"**Uptime:** {uptime_str}\n"
                      f"**Guilds:** {len(self.bot.guilds)}\n"
                      f"**Users:** {len(self.bot.users)}",
                inline=True
            )
            
            # System metrics
            embed.add_field(
                name="💻 System Metrics",
                value=f"**CPU Usage:** {cpu_percent:.1f}%\n"
                      f"**Memory:** {memory.percent:.1f}%\n"
                      f"**Disk:** {disk.percent:.1f}%\n"
                      f"**Memory Used:** {memory.used // (1024**3):.1f}GB\n"
                      f"**Memory Total:** {memory.total // (1024**3):.1f}GB",
                inline=True
            )
            
            # Services status
            services_status = []
            services_status.append(f"**Analysis:** {'✅' if getattr(self.bot, 'ANALYSIS_ENABLED', False) else '❌'}")
            services_status.append(f"**Dashboard:** {'✅' if self.bot.dashboard_enabled else '❌'}")
            services_status.append(f"**Logging:** {'✅' if self.bot.log_channel_id else '❌'}")
            services_status.append(f"**Permissions:** {'✅' if hasattr(self.bot, 'permissions') else '❌'}")
            
            embed.add_field(
                name="🔧 Services",
                value="\n".join(services_status),
                inline=True
            )
            
            # Environment warnings
            warnings = self._check_environment_warnings()
            if warnings:
                embed.add_field(
                    name="⚠️ Warnings",
                    value="\n".join(warnings),
                    inline=False
                )
            
            embed.set_footer(text="GotLockz Bot • Production Ready")
            
            await interaction.followup.send(embed=embed)
            await self.logger.log_command(interaction, "status", success=True)
            
        except Exception as e:
            self.logger.log_exception(e, "status command")
            await self.logger.log_command(interaction, "status", success=False, error=str(e))
            await interaction.followup.send(f"❌ Error getting status: {str(e)}", ephemeral=True)
    
    def _format_uptime(self, uptime: timedelta) -> str:
        """Format uptime as a readable string."""
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"
    
    def _check_environment_warnings(self) -> List[str]:
        """Check for missing or invalid environment variables."""
        warnings = []
        
        # Check required environment variables
        required_vars = {
            'DISCORD_TOKEN': 'Bot token',
            'OPENAI_API_KEY': 'OpenAI API key',
            'DASHBOARD_URL': 'Dashboard URL'
        }
        
        for var, description in required_vars.items():
            if not os.getenv(var):
                warnings.append(f"❌ Missing {description} ({var})")
        
        # Check optional but recommended variables
        optional_vars = {
            'VIP_ROLE_IDS': 'VIP role IDs',
            'ADMIN_ROLE_IDS': 'Admin role IDs',
            'LOG_CHANNEL_ID': 'Logging channel ID'
        }
        
        for var, description in optional_vars.items():
            if not os.getenv(var):
                warnings.append(f"⚠️ Missing {description} ({var})")
        
        return warnings

    @app_commands.command(name="debug", description="Debug bot status and configuration")
    @require_admin()
    @validate_input
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
            
            # Permissions
            if hasattr(self.bot, 'permissions'):
                vip_roles = len(self.bot.permissions.vip_roles)
                admin_roles = len(self.bot.permissions.admin_roles)
                blocked_users = len(self.bot.permissions.blocked_users)
                
                embed.add_field(
                    name="🔐 Permissions",
                    value=f"VIP Roles: {vip_roles}\n"
                          f"Admin Roles: {admin_roles}\n"
                          f"Blocked Users: {blocked_users}",
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
            self.logger.log_exception(e, "debug command")
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
    """Betting-related slash commands.
    NOTE: After instantiation, call `await instance._load_counters_async()` to load counters.
    """
    
    def __init__(self, bot):
        super().__init__(name="betting", description="Betting analysis and pick management")
        self.bot = bot
        self.pick_counters = {"vip": 0, "lotto": 0, "free": 0}  # Default values
        self.logger = BotLogger(bot)
        # No async task creation here; must call _load_counters_async() explicitly in async context

    async def _load_counters_async(self):
        """Load counters asynchronously after initialization."""
        self.pick_counters = await self._load_counters()

    async def _load_counters(self) -> Dict[str, int]:
        """Load pick counters from file asynchronously."""
        try:
            async with aiofiles.open('counters.json', 'r') as f:
                content = await f.read()
                return json.loads(content)
        except FileNotFoundError:
            return {"vip": 0, "lotto": 0, "free": 0}
        except Exception as e:
            logger.error(f"Error loading counters: {e}")
            return {"vip": 0, "lotto": 0, "free": 0}

    async def _save_counters(self):
        """Save pick counters to file asynchronously."""
        try:
            async with aiofiles.open('counters.json', 'w') as f:
                await f.write(json.dumps(self.pick_counters, indent=2))
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
        """Analyze a betting slip image."""
        
        # Check if command is used in the correct channel
        if hasattr(self.bot, 'channels_configured') and self.bot.channels_configured:
            if hasattr(self.bot, 'analysis_channel_id') and self.bot.analysis_channel_id:
                if interaction.channel_id != self.bot.analysis_channel_id:
                    await interaction.response.send_message(
                        "❌ This command can only be used in the Analysis channel!",
                        ephemeral=True
                    )
                    await self.logger.log_command(interaction, "analyze", success=False, error="Wrong channel - expected Analysis")
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
            
            # Create basic analysis embed
            embed = discord.Embed(
                title="📊 Bet Analysis",
                description="Basic image analysis completed",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            
            # Add image
            embed.set_image(url=image.url)
            
            # Add basic image info
            embed.add_field(
                name="📋 Image Details",
                value=f"**Filename:** {image.filename}\n"
                      f"**Size:** {len(image_bytes)} bytes\n"
                      f"**Type:** {image.content_type}\n"
                      f"**Dimensions:** Image uploaded successfully",
                inline=True
            )
            
            # Add context
            embed.add_field(
                name="📝 Context",
                value=context or "No context provided",
                inline=True
            )
            
            # Add analysis note
            embed.add_field(
                name="🤖 Analysis Status",
                value="✅ Basic analysis completed\n"
                      "📊 Image processed successfully\n"
                      "💡 Advanced AI analysis not available",
                inline=False
            )
            
            embed.set_footer(text="GotLockz Bot • Basic Analysis")
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            
            await interaction.followup.send(embed=embed)
            await self.logger.log_command(interaction, "analyze", success=True)
                    
        except Exception as e:
            logger.exception("Error in analysis")
            await interaction.followup.send(f"❌ Analysis failed: {str(e)}", ephemeral=True)
            await self.logger.log_command(interaction, "analyze", success=False, error=str(e))

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
            await self._save_counters()
            
            # Create embed
            embed = discord.Embed(
                title=f"🎯 {pick_type.upper()} PICK #{self.pick_counters[pick_type]}",
                description=context or f"New {pick_type} pick posted!",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            
            # Add image
            embed.set_image(url=image.url)
            
            # Add basic bet details
            embed.add_field(
                name="📊 Bet Details",
                value=f"**Image:** {image.filename}\n"
                      f"**Size:** {len(image_bytes)} bytes\n"
                      f"**Type:** {image.content_type}\n"
                      f"**Context:** {context or 'No context provided'}",
                inline=True
            )
            
            # Add user info
            embed.add_field(
                name="👤 Posted By",
                value=f"**User:** {interaction.user.display_name}\n"
                      f"**ID:** {interaction.user.id}\n"
                      f"**Channel:** <#{interaction.channel_id}>",
                inline=True
            )
            
            embed.set_footer(text=f"GotLockz Bot • {pick_type.upper()} Pick")
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            
            # Send to channel
            await interaction.followup.send(embed=embed)
            
            # Log the pick
            await self.logger.log_pick_posted(interaction, pick_type, False)
            await self.logger.log_command(interaction, pick_type, success=True)
            
            # Sync to dashboard if enabled
            if hasattr(self.bot, 'dashboard_enabled') and self.bot.dashboard_enabled:
                try:
                    pick_data = {
                        "pick_number": self.pick_counters[pick_type],
                        "pick_type": pick_type,
                        "bet_details": {
                            "image": image.filename,
                            "context": context or "No context"
                        },
                        "user": interaction.user.display_name,
                        "user_id": interaction.user.id,
                        "image_url": image.url,
                        "timestamp": datetime.now().isoformat(),
                        "analysis_enabled": False
                    }
                    
                    response = requests.post(
                        f"{self.bot.dashboard_url}/run/api_sync_discord",
                        json={"data": [json.dumps(pick_data)]},
                        timeout=10
                    )
                    
                    if response.status_code != 200:
                        logger.warning(f"Failed to sync pick to dashboard: {response.status_code}")
                    else:
                        logger.info(f"Successfully synced {pick_type} pick to dashboard")
                        
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
    
    # Add essential standalone commands that might be missing
    try:
        # Standalone ping command (fallback)
        @bot.tree.command(name="ping", description="Test bot responsiveness")
        async def ping_standalone(interaction: discord.Interaction):
            """Test bot responsiveness."""
            await interaction.response.send_message("🏓 Pong! Bot is online!")
        
        # Standalone status command (fallback)
        @bot.tree.command(name="status", description="Check bot status")
        async def status_standalone(interaction: discord.Interaction):
            """Check bot status."""
            await interaction.response.defer(thinking=True)
            
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
                value=f"{round(bot.latency * 1000)}ms",
                inline=True
            )
            
            embed.add_field(
                name="Servers",
                value=str(len(bot.guilds)),
                inline=True
            )
            
            await interaction.followup.send(embed=embed)
        
        # Standalone force_sync command (essential)
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

        print("✅ Essential standalone commands added to tree")
    except Exception as e:
        print(f"❌ Error adding essential standalone commands: {e}")

    print("✅ All commands setup complete")
