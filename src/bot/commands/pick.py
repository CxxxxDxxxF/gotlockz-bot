"""
Pick Commands - Core betting functionality
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

import discord
from discord import app_commands

from bot.services.ocr import OCRService
from bot.services.stats import StatsService
from bot.services.analysis import AnalysisService

logger = logging.getLogger(__name__)


class PickCommands(app_commands.Group):
    """Commands for posting betting picks."""
    
    def __init__(self, bot):
        super().__init__(name="pick", description="Post betting picks with analysis")
        self.bot = bot
        self.ocr_service = OCRService()
        self.stats_service = StatsService()
        self.analysis_service = AnalysisService()
    
    @app_commands.command(name="post", description="Post a betting pick with image analysis")
    @app_commands.describe(
        image="Upload a betting slip image",
        channel="Channel to post the pick in",
        units="Number of units (optional)"
    )
    async def post_pick(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        channel: discord.TextChannel,
        units: int = 0
    ):
        """Post a betting pick with two-phase processing."""
        
        # Phase 1: Immediate Response
        await interaction.response.defer(thinking=True)
        
        try:
            # Validate image
            if not image.content_type or not image.content_type.startswith('image/'):
                await interaction.followup.send("❌ Please provide a valid image file.", ephemeral=True)
                return
            
            # Download image with timeout
            try:
                image_bytes = await asyncio.wait_for(image.read(), timeout=2.0)
            except asyncio.TimeoutError:
                await interaction.followup.send("❌ Image download timed out. Please try again.", ephemeral=True)
                return
            
            # Extract betting data with OCR
            try:
                bet_data = await asyncio.wait_for(
                    self.ocr_service.extract_bet_data(image_bytes),
                    timeout=3.0
                )
            except asyncio.TimeoutError:
                await interaction.followup.send("❌ Image processing timed out. Please try with a clearer image.", ephemeral=True)
                return
            
            # Generate basic content
            basic_content = self._generate_basic_content(bet_data, units)
            
            # Post immediately
            try:
                message = await asyncio.wait_for(
                    channel.send(content=basic_content),
                    timeout=2.0
                )
            except asyncio.TimeoutError:
                await interaction.followup.send("❌ Failed to post message. Please check channel permissions.", ephemeral=True)
                return
            
            # Confirm to user
            await interaction.followup.send(f"✅ Pick posted successfully in {channel.mention}!", ephemeral=True)
            
            # Phase 2: Async Enhancement
            asyncio.create_task(self._enhance_message_async(message, bet_data))
            
        except Exception as e:
            logger.error(f"Error in post_pick: {e}")
            await interaction.followup.send("❌ An error occurred. Please try again.", ephemeral=True)
    
    def _generate_basic_content(self, bet_data: dict, units: int) -> str:
        """Generate basic pick content without API calls."""
        teams = bet_data.get('teams', ['TBD', 'TBD'])
        description = bet_data.get('description', 'TBD')
        odds = bet_data.get('odds', 'TBD')
        
        # Format date and time
        current_date = datetime.now().strftime("%m/%d/%y")
        current_time = datetime.now().strftime("%I:%M")
        
        # Build content
        header = f"**FREE PLAY – {current_date}**"
        if units > 0:
            header += f"\n💰 **{units} UNITS**"
        
        game_info = f"⚾ | Game: {teams[0]} @ {teams[1]} ({current_date} {current_time} EST)"
        bet_info = f"🎯 | Bet: {description}"
        if odds != 'TBD':
            bet_info += f" | Odds: {odds}"
        
        analysis = "📊 Analysis: Loading live data and statistics..."
        
        return f"{header}\n\n{game_info}\n{bet_info}\n\n{analysis}"
    
    async def _enhance_message_async(self, message: discord.Message, bet_data: dict):
        """Enhance the message with live data asynchronously."""
        try:
            logger.info("Starting async message enhancement")
            
            # Fetch live stats
            stats_data = await self.stats_service.get_live_stats(bet_data)
            
            # Generate AI analysis
            analysis = await self.analysis_service.generate_analysis(bet_data, stats_data)
            
            # Create enhanced content
            enhanced_content = self._generate_enhanced_content(bet_data, stats_data, analysis)
            
            # Edit the message
            await message.edit(content=enhanced_content)
            
            logger.info("Message enhancement completed successfully")
            
        except Exception as e:
            logger.error(f"Error in async enhancement: {e}")
            # Don't fail the original command if enhancement fails
    
    def _generate_enhanced_content(self, bet_data: dict, stats_data: dict, analysis: str) -> str:
        """Generate enhanced content with live data and analysis."""
        teams = bet_data.get('teams', ['TBD', 'TBD'])
        description = bet_data.get('description', 'TBD')
        odds = bet_data.get('odds', 'TBD')
        
        current_date = datetime.now().strftime("%m/%d/%y")
        current_time = datetime.now().strftime("%I:%M")
        
        # Build enhanced content
        header = f"**FREE PLAY – {current_date}**"
        if bet_data.get('units', 0) > 0:
            header += f"\n💰 **{bet_data['units']} UNITS**"
        
        game_info = f"⚾ | Game: {teams[0]} @ {teams[1]} ({current_date} {current_time} EST)"
        bet_info = f"🎯 | Bet: {description}"
        if odds != 'TBD':
            bet_info += f" | Odds: {odds}"
        
        # Add live stats if available
        stats_section = ""
        if stats_data:
            stats_section = f"\n📈 Live Stats: {stats_data.get('summary', 'Data available')}"
        
        # Add analysis
        analysis_section = f"\n📊 Analysis:\n{analysis}"
        
        return f"{header}\n\n{game_info}\n{bet_info}{stats_section}{analysis_section}" 