"""
Pick Command - MLB betting pick command with channel selection
"""
import asyncio
import logging
from typing import Optional

import discord
from discord import app_commands

from bot.services.ocr import OCRService
from bot.services.stats import StatsService
from bot.services.analysis import AnalysisService
from bot.services.templates import TemplateService

logger = logging.getLogger(__name__)


class PickCommands(app_commands.Group):
    """Commands for posting MLB betting picks."""
    
    def __init__(self, bot):
        super().__init__(name="pick", description="Post MLB betting picks with analysis")
        self.bot = bot
        self.ocr_service = OCRService()
        self.stats_service = StatsService()
        self.analysis_service = AnalysisService()
        self.template_service = TemplateService()

    @app_commands.command(name="post", description="Post a betting pick with image analysis and AI")
    @app_commands.describe(
        channel_type="Type of pick to post",
        image="Attach a betting slip image",
        description="Additional notes (optional)"
    )
    @app_commands.choices(channel_type=[
        app_commands.Choice(name="Free Play", value="free_play"),
        app_commands.Choice(name="VIP Pick", value="vip_pick"),
        app_commands.Choice(name="Lotto Ticket", value="lotto_ticket")
    ])
    async def post_pick(
        self,
        interaction: discord.Interaction,
        channel_type: str,
        image: discord.Attachment,
        description: Optional[str] = None
    ):
        """Post a betting pick with OCR, MLB stats, and AI analysis."""
        await interaction.response.defer(thinking=True)
        
        try:
            # Validate image
            if not image.content_type or not image.content_type.startswith('image/'):
                await interaction.followup.send("❌ Please provide a valid image file.", ephemeral=True)
                return

            # Download image with timeout
            try:
                image_bytes = await asyncio.wait_for(image.read(), timeout=5.0)
            except asyncio.TimeoutError:
                await interaction.followup.send("❌ Image download timed out. Please try again.", ephemeral=True)
                return

            # Extract betting data with OCR
            try:
                bet_data = await asyncio.wait_for(
                    self.ocr_service.extract_bet_data(image_bytes),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                await interaction.followup.send("❌ Image processing timed out. Please try with a clearer image.", ephemeral=True)
                return

            # Add optional description if provided
            if description:
                bet_data['description'] = f"{bet_data.get('description', 'TBD')} - {description}"

            # Fetch live MLB stats
            stats_data = await self.stats_service.get_live_stats(bet_data)

            # Generate AI analysis
            analysis = await self.analysis_service.generate_analysis(bet_data, stats_data)

            # Format content based on channel type
            if channel_type == "free_play":
                content = self.template_service.format_free_play(bet_data, stats_data, analysis)
            elif channel_type == "vip_pick":
                content = self.template_service.format_vip_pick(bet_data, stats_data, analysis)
            elif channel_type == "lotto_ticket":
                content = self.template_service.format_lotto_ticket(bet_data, stats_data, analysis)
            else:
                await interaction.followup.send("❌ Invalid channel type selected.", ephemeral=True)
                return

            # Get target channel
            if not interaction.guild:
                await interaction.followup.send("❌ This command can only be used in a server.", ephemeral=True)
                return
                
            target_channel = await self._get_target_channel(channel_type, interaction.guild)
            if not target_channel:
                await interaction.followup.send("❌ Target channel not found. Please check bot configuration.", ephemeral=True)
                return

            # Post to target channel
            await target_channel.send(content)
            
            # Confirm to user
            await interaction.followup.send(f"✅ Pick posted to {target_channel.mention}!", ephemeral=True)

        except Exception as e:
            logger.error(f"Error in post_pick: {e}")
            await interaction.followup.send("❌ An error occurred. Please try again.", ephemeral=True)

    async def _get_target_channel(self, channel_type: str, guild: discord.Guild) -> Optional[discord.TextChannel]:
        """Get the target channel based on channel type."""
        try:
            from config.settings import settings
            
            channel_id = None
            if channel_type == "free_play":
                channel_id = settings.channels.free_channel_id
            elif channel_type == "vip_pick":
                channel_id = settings.channels.vip_channel_id
            elif channel_type == "lotto_ticket":
                channel_id = settings.channels.lotto_channel_id
            
            if not channel_id:
                return None
            
            channel = guild.get_channel(channel_id)
            if isinstance(channel, discord.TextChannel):
                return channel
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting target channel: {e}")
            return None 