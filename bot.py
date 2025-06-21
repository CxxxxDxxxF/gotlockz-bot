# bot.py

#!/usr/bin/env python3
"""
bot.py

Enhanced Discord bot with comprehensive error handling, logging,
and health monitoring for the GotLockz betting analysis system.
"""
import logging
import asyncio
import json
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import discord
from discord.ext import commands, tasks

from config import (
    DISCORD_TOKEN, GUILD_ID, OWNER_ID, LOG_FILE,
    ANALYSIS_CHANNEL_ID, VIP_CHANNEL_ID, LOTTO_CHANNEL_ID, FREE_CHANNEL_ID
)
from commands import setup as setup_commands

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class GotLockzBot(commands.Bot):
    """Enhanced Discord bot for GotLockz betting analysis."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        
        self.start_time = datetime.now()
        self.health_status = {
            "status": "starting",
            "last_heartbeat": None,
            "errors": [],
            "commands_processed": 0,
            "analysis_count": 0
        }
        
        # Register event handlers
        self.add_listener(self.on_ready, "on_ready")
        self.add_listener(self.on_command_error, "on_command_error")
        self.add_listener(self.on_app_command_error, "on_app_command_error")
        
        # Start background tasks
        self.health_check.start()
        self.cleanup_cache.start()
    
    async def setup_hook(self):
        """Setup hook called when bot is starting."""
        logger.info("Setting up GotLockz bot...")
        
        try:
            # Load commands
            await setup_commands(self)
            logger.info("Commands loaded successfully")
            
            # Sync commands to Discord
            await self.tree.sync(guild=discord.Object(id=GUILD_ID))
            logger.info("Slash commands synced to Discord")
            
        except Exception as e:
            logger.exception("Error in setup_hook")
            await self._notify_owner(f"❌ Bot setup failed: {str(e)}")
            raise
    
    async def on_ready(self):
        """Called when bot is ready and connected to Discord."""
        logger.info(f"GotLockz bot is ready! Logged in as {self.user}")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")
        
        self.health_status["status"] = "online"
        self.health_status["last_heartbeat"] = datetime.now()
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for betting slips 📊"
            )
        )
        
        # Notify owner of successful startup
        if OWNER_ID:
            await self._notify_owner("✅ GotLockz bot is online and ready!")
    
    async def on_command_error(self, ctx, error):
        """Handle command errors."""
        logger.error(f"Command error: {error}")
        
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("❌ Command not found. Use `/help` to see available commands.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ I don't have the required permissions to execute this command.")
        else:
            await ctx.send(f"❌ An error occurred: {str(error)}")
            await self._notify_owner(f"⚠️ Command error: {str(error)}")
    
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        """Handle slash command errors."""
        logger.error(f"Slash command error: {error}")
        
        try:
            if isinstance(error, app_commands.CommandOnCooldown):
                await interaction.response.send_message(
                    f"⏰ Command on cooldown. Try again in {error.retry_after:.1f} seconds.",
                    ephemeral=True
                )
            elif isinstance(error, app_commands.MissingPermissions):
                await interaction.response.send_message(
                    "❌ You don't have permission to use this command.",
                    ephemeral=True
                )
            elif isinstance(error, app_commands.BotMissingPermissions):
                await interaction.response.send_message(
                    "❌ I don't have the required permissions to execute this command.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"❌ An error occurred: {str(error)}",
                    ephemeral=True
                )
                await self._notify_owner(f"⚠️ Slash command error: {str(error)}")
                
        except Exception as e:
            logger.exception("Error handling slash command error")
            await self._notify_owner(f"❌ Error handling slash command error: {str(e)}")
    
    @tasks.loop(minutes=5)
    async def health_check(self):
        """Periodic health check and status update."""
        try:
            self.health_status["last_heartbeat"] = datetime.now()
            
            # Check if bot is still connected
            if not self.is_ready():
                self.health_status["status"] = "disconnected"
                logger.warning("Bot appears to be disconnected")
                await self._notify_owner("⚠️ Bot health check: Bot appears disconnected")
            else:
                self.health_status["status"] = "healthy"
                
            # Log health status
            logger.debug(f"Health check: {self.health_status['status']}")
            
        except Exception as e:
            logger.exception("Error in health check")
            self.health_status["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            })
    
    @tasks.loop(hours=1)
    async def cleanup_cache(self):
        """Clean up old cache entries and logs."""
        try:
            # Clean up old errors (keep last 10)
            if len(self.health_status["errors"]) > 10:
                self.health_status["errors"] = self.health_status["errors"][-10:]
            
            logger.debug("Cache cleanup completed")
            
        except Exception as e:
            logger.exception("Error in cache cleanup")
    
    async def _notify_owner(self, message: str):
        """Send a notification to the bot owner."""
        if not OWNER_ID:
            return
            
        try:
            owner = self.get_user(OWNER_ID)
            if owner:
                await owner.send(message)
            else:
                logger.warning(f"Could not find owner user with ID {OWNER_ID}")
                
        except Exception as e:
            logger.error(f"Failed to notify owner: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        return {
            **self.health_status,
            "uptime": str(datetime.now() - self.start_time),
            "guild_count": len(self.guilds),
            "user_count": len(self.users)
        }
    
    async def close(self):
        """Clean shutdown of the bot."""
        logger.info("Shutting down GotLockz bot...")
        
        # Stop background tasks
        self.health_check.cancel()
        self.cleanup_cache.cancel()
        
        # Notify owner
        await self._notify_owner("🔴 GotLockz bot is shutting down")
        
        # Close bot
        await super().close()


async def main():
    """Main function to run the bot."""
    bot = GotLockzBot()
    
    try:
        logger.info("Starting GotLockz bot...")
        await bot.start(DISCORD_TOKEN)
        
    except discord.LoginFailure:
        logger.error("Invalid Discord token. Please check your .env file.")
        sys.exit(1)
    except Exception as e:
        logger.exception("Fatal error starting bot")
        sys.exit(1)
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
