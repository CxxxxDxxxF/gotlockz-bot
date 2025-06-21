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

from config import (
    GUILD_ID, ANALYSIS_CHANNEL_ID, VIP_CHANNEL_ID, 
    LOTTO_CHANNEL_ID, FREE_CHANNEL_ID, OWNER_ID
)
from image_processing import extract_text_from_image, parse_bet_details
from ai_analysis import analyze_bet_slip, generate_pick_summary, validate_analysis_quality
from data_enrichment import enrich_bet_analysis

logger = logging.getLogger(__name__)


class BettingCommands(commands.Cog):
    """Cog containing all betting-related commands."""
    
    def __init__(self, bot):
        self.bot = bot
        self.analysis_cache = {}
        self.pick_counters = self._load_counters()
    
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
        if interaction.channel_id != ANALYSIS_CHANNEL_ID:
            await interaction.response.send_message(
                "❌ This command can only be used in the analysis channel!",
                ephemeral=True
            )
            return
        
        # Validate image
        if not image.content_type.startswith('image/'):
            await interaction.response.send_message(
                "❌ Please upload a valid image file!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(thinking=True)
        
        try:
            # Download and process image
            image_bytes = await image.read()
            
            # Extract text from image
            text = extract_text_from_image(image_bytes)
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
            
            # Perform AI analysis
            analysis = await analyze_bet_slip(bet_details, context)
            
            # Validate analysis quality
            validation = await validate_analysis_quality(analysis)
            
            # Create response embed
            embed = await self._create_analysis_embed(bet_details, analysis, validation)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.exception("Error in analyze command")
            await interaction.followup.send(
                f"❌ An error occurred during analysis: {str(e)}",
                ephemeral=True
            )
    
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
        """Post a VIP pick to the VIP channel."""
        await self._post_pick(interaction, image, context, "vip", VIP_CHANNEL_ID)
    
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
        """Post a lotto pick to the lotto channel."""
        await self._post_pick(interaction, image, context, "lotto", LOTTO_CHANNEL_ID)
    
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
        """Post a free pick to the free channel."""
        await self._post_pick(interaction, image, context, "free", FREE_CHANNEL_ID)
    
    async def _post_pick(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        context: Optional[str],
        pick_type: str,
        channel_id: int
    ):
        """Internal method to post picks to channels."""
        
        # Check permissions
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "❌ You don't have permission to post picks!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(thinking=True)
        
        try:
            # Process image and analyze
            image_bytes = await image.read()
            text = extract_text_from_image(image_bytes)
            bet_details = parse_bet_details(text)
            
            if not bet_details:
                await interaction.followup.send(
                    "❌ Could not parse betting details from the image.",
                    ephemeral=True
                )
                return
            
            # Perform analysis
            analysis = await analyze_bet_slip(bet_details, context)
            
            # Generate pick summary
            summary = await generate_pick_summary(bet_details, analysis, pick_type)
            
            # Post to target channel
            channel = self.bot.get_channel(channel_id)
            if not channel:
                await interaction.followup.send(
                    "❌ Target channel not found!",
                    ephemeral=True
                )
                return
            
            # Increment counter
            self.pick_counters[pick_type] += 1
            self._save_counters()
            
            # Post the pick
            await channel.send(summary)
            
            # Confirm to user
            await interaction.followup.send(
                f"✅ {pick_type.upper()} pick #{self.pick_counters[pick_type]} posted successfully!",
                ephemeral=True
            )
            
        except Exception as e:
            logger.exception(f"Error posting {pick_type} pick")
            await interaction.followup.send(
                f"❌ Error posting {pick_type} pick: {str(e)}",
                ephemeral=True
            )
    
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
        """View pick history from Google Sheets."""
        
        if pick_type not in ["vip", "lotto", "free"]:
            await interaction.response.send_message(
                "❌ Invalid pick type. Use vip, lotto, or free.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(thinking=True)
        
        try:
            # This would integrate with Google Sheets
            # For now, return basic info
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
            await interaction.followup.send(
                f"❌ Error retrieving history: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="stats", description="View bot statistics")
    async def stats_command(self, interaction: discord.Interaction):
        """View bot statistics and performance metrics."""
        
        await interaction.response.defer(thinking=True)
        
        try:
            embed = discord.Embed(
                title="GotLockz Bot Statistics",
                color=discord.Color.green()
            )
            
            # Pick counts
            embed.add_field(
                name="Total Picks",
                value=f"VIP: {self.pick_counters.get('vip', 0)}\n"
                      f"Lotto: {self.pick_counters.get('lotto', 0)}\n"
                      f"Free: {self.pick_counters.get('free', 0)}",
                inline=True
            )
            
            # Bot stats
            embed.add_field(
                name="Bot Info",
                value=f"Uptime: {self._get_uptime()}\n"
                      f"Servers: {len(self.bot.guilds)}\n"
                      f"Users: {len(self.bot.users)}",
                inline=True
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.exception("Error in stats command")
            await interaction.followup.send(
                f"❌ Error retrieving stats: {str(e)}",
                ephemeral=True
            )
    
    async def _create_analysis_embed(
        self,
        bet_details: Dict[str, Any],
        analysis: Dict[str, Any],
        validation: Dict[str, Any]
    ) -> discord.Embed:
        """Create a Discord embed for analysis results."""
        
        embed = discord.Embed(
            title="🎯 Bet Analysis Results",
            color=discord.Color.blue()
        )
        
        # Bet details
        embed.add_field(
            name="Bet Details",
            value=f"**Type:** {bet_details.get('type', 'Unknown')}\n"
                  f"**Bet:** {bet_details.get('bet', 'Unknown')}\n"
                  f"**Odds:** {bet_details.get('odds', 'Unknown')}",
            inline=False
        )
        
        # Recommendation
        if 'recommendation' in analysis:
            rec = analysis['recommendation']
            color = discord.Color.green() if rec.get('action') == 'Bet' else \
                   discord.Color.red() if rec.get('action') == 'Pass' else \
                   discord.Color.yellow()
            
            embed.color = color
            
            embed.add_field(
                name="Recommendation",
                value=f"**{rec.get('action', 'Unknown')}**\n"
                      f"Stake: {rec.get('stake_suggestion', 'N/A')}\n"
                      f"Reasoning: {rec.get('reasoning', 'N/A')[:100]}...",
                inline=False
            )
        
        # Confidence and Edge
        if 'confidence_rating' in analysis:
            conf = analysis['confidence_rating']
            embed.add_field(
                name="Confidence",
                value=f"**{conf.get('score', 0)}/10**\n{conf.get('reasoning', 'N/A')[:100]}...",
                inline=True
            )
        
        if 'edge_analysis' in analysis:
            edge = analysis['edge_analysis']
            embed.add_field(
                name="Edge Analysis",
                value=f"**{edge.get('edge_percentage', 0):.2f}%**\n"
                      f"Implied: {edge.get('implied_probability', 0):.3f}\n"
                      f"True: {edge.get('true_probability', 0):.3f}",
                inline=True
            )
        
        # Risk assessment
        if 'risk_assessment' in analysis:
            risk = analysis['risk_assessment']
            embed.add_field(
                name="Risk Level",
                value=f"**{risk.get('level', 'Unknown')}**\n{risk.get('reasoning', 'N/A')[:100]}...",
                inline=True
            )
        
        # Quality validation
        if not validation.get('is_valid', True):
            embed.add_field(
                name="⚠️ Analysis Quality",
                value=f"Score: {validation.get('quality_score', 0)}%\n"
                      f"Missing: {', '.join(validation.get('missing_fields', []))}",
                inline=False
            )
        
        embed.set_footer(text="Powered by GotLockz AI Analysis")
        embed.timestamp = datetime.now()
        
        return embed
    
    def _get_uptime(self) -> str:
        """Get bot uptime as a string."""
        # This would calculate actual uptime
        # For now, return placeholder
        return "24h 30m"


async def setup(bot):
    """Setup function for the commands cog."""
    await bot.add_cog(BettingCommands(bot))
