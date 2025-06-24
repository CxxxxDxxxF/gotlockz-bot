"""
Pick Command - MLB betting pick command with channel selection
"""
import asyncio
import logging
from typing import Optional
from datetime import datetime

import discord
from discord import app_commands

from bot.services.ocr import OCRService
from bot.services.stats import StatsService
from bot.services.advanced_stats import AdvancedStatsService
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
        self.advanced_stats_service = AdvancedStatsService()
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
        app_commands.Choice(name="VIP Plays", value="vip_pick"),
        app_commands.Choice(name="Lotto Ticket", value="lotto_ticket")
    ])
    async def post_pick(
        self,
        interaction: discord.Interaction,
        channel_type: str,
        image: discord.Attachment,
        description: Optional[str] = None
    ):
        logger.info("Received /pick post command, deferring response immediately.")
        
        # Defer immediately to prevent timeout
        try:
            await interaction.response.defer(thinking=True)
            logger.info("Deferred interaction response successfully.")
        except discord.NotFound:
            logger.error("Interaction already expired - user may have clicked multiple times")
            return
        except Exception as e:
            logger.error(f"Failed to defer interaction: {e}")
            try:
                await interaction.followup.send("❌ Bot is processing your request. Please wait...", ephemeral=True)
            except:
                pass
            return

        try:
            # Validate image
            if not image.content_type or not image.content_type.startswith('image/'):
                await interaction.followup.send("❌ Please provide a valid image file.", ephemeral=True)
                return

            # Download image with timeout
            try:
                image_bytes = await asyncio.wait_for(image.read(), timeout=10.0)
                logger.info("Image downloaded successfully.")
            except asyncio.TimeoutError:
                await interaction.followup.send("❌ Image download timed out. Please try again.", ephemeral=True)
                return
            except Exception as e:
                logger.error(f"Image download failed: {e}")
                await interaction.followup.send("❌ Failed to download image. Please try again.", ephemeral=True)
                return

            # Extract betting data with OCR
            try:
                bet_data = await asyncio.wait_for(
                    self.ocr_service.extract_bet_data(image_bytes),
                    timeout=15.0
                )
                logger.info(f"OCR extraction completed: {bet_data}")
            except asyncio.TimeoutError:
                await interaction.followup.send("❌ Image processing timed out. Please try with a clearer image.", ephemeral=True)
                return
            except Exception as e:
                logger.error(f"OCR extraction failed: {e}")
                await interaction.followup.send("❌ Failed to extract data from the image. Please try a different slip or clearer photo.", ephemeral=True)
                return

            # Add optional description if provided
            if description:
                bet_data['description'] = f"{bet_data.get('description', 'TBD')} - {description}"

            # If OCR failed to extract teams or bet, notify user
            if bet_data.get('teams', ['TBD', 'TBD'])[0] == 'TBD' or bet_data.get('teams', ['TBD', 'TBD'])[1] == 'TBD':
                await interaction.followup.send("❌ Could not extract teams from the bet slip. Please ensure the image is clear and the team names are visible.", ephemeral=True)
                return
            if bet_data.get('description', 'TBD') == 'TBD':
                await interaction.followup.send("❌ Could not extract bet description from the slip. Please ensure the bet type (e.g., Over/Under) is visible.", ephemeral=True)
                return

            # Fetch advanced MLB stats with timeout (try advanced first, fallback to basic)
            stats_data = None
            try:
                stats_data = await asyncio.wait_for(
                    self.advanced_stats_service.get_advanced_stats(bet_data),
                    timeout=15.0
                )
                logger.info("Advanced stats fetched successfully.")
            except asyncio.TimeoutError:
                logger.warning("Advanced stats fetch timed out, trying basic stats")
                try:
                    stats_data = await asyncio.wait_for(
                        self.stats_service.get_live_stats(bet_data),
                        timeout=10.0
                    )
                    logger.info("Basic stats fetched successfully as fallback.")
                except asyncio.TimeoutError:
                    logger.warning("Basic stats fetch also timed out, continuing without stats")
                    stats_data = None
                except Exception as e:
                    logger.error(f"Basic stats fetch failed: {e}")
                    stats_data = None
            except Exception as e:
                logger.error(f"Advanced stats fetch failed: {e}, trying basic stats")
                try:
                    stats_data = await asyncio.wait_for(
                        self.stats_service.get_live_stats(bet_data),
                        timeout=10.0
                    )
                    logger.info("Basic stats fetched successfully as fallback.")
                except Exception as e2:
                    logger.error(f"Basic stats fetch also failed: {e2}")
                    stats_data = None

            # Generate AI analysis with timeout
            try:
                analysis = await asyncio.wait_for(
                    self.analysis_service.generate_analysis(bet_data, stats_data),
                    timeout=20.0
                )
                logger.info("AI analysis generated successfully.")
            except asyncio.TimeoutError:
                logger.warning("AI analysis timed out, using fallback")
                analysis = "AI analysis temporarily unavailable. Please check the betting data manually."
            except Exception as e:
                logger.error(f"AI analysis failed: {e}")
                analysis = "AI analysis temporarily unavailable. Please check the betting data manually."

            # Format content based on channel type
            try:
                if channel_type == "free_play":
                    content = self.template_service.format_free_play(bet_data, stats_data, analysis)
                elif channel_type == "vip_pick":
                    content = self.template_service.format_vip_pick(bet_data, stats_data, analysis)
                elif channel_type == "lotto_ticket":
                    content = self.template_service.format_lotto_ticket(bet_data, stats_data, analysis)
                else:
                    await interaction.followup.send("❌ Invalid channel type selected.", ephemeral=True)
                    return
                logger.info("Content formatted successfully.")
            except Exception as e:
                logger.error(f"Content formatting failed: {e}")
                await interaction.followup.send("❌ Failed to format content. Please try again.", ephemeral=True)
                return

            # Get target channel
            if not interaction.guild:
                await interaction.followup.send("❌ This command can only be used in a server.", ephemeral=True)
                return
            target_channel = await self._get_target_channel(channel_type, interaction.guild)
            if not target_channel:
                await interaction.followup.send("❌ Target channel not found. Please check bot configuration.", ephemeral=True)
                return

            # Post to target channel with image
            try:
                # Create a Discord file from the image bytes
                from io import BytesIO
                image_file = discord.File(BytesIO(image_bytes), filename=f"betslip_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                
                # Post content with image attachment
                await target_channel.send(content, file=image_file)
                logger.info(f"Pick posted successfully to {target_channel.name} with image")
            except Exception as e:
                logger.error(f"Failed to post to channel: {e}")
                await interaction.followup.send("❌ Failed to post to target channel. Please check bot permissions.", ephemeral=True)
                return
            
            # Confirm to user
            await interaction.followup.send(f"✅ Pick posted to {target_channel.mention}!", ephemeral=True)

        except discord.NotFound:
            logger.error("Interaction expired during processing")
            return
        except Exception as e:
            logger.error(f"Error in post_pick: {e}")
            try:
                await interaction.followup.send("❌ An error occurred. Please try again or contact support.", ephemeral=True)
            except:
                pass

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