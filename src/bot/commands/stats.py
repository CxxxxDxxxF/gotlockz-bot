"""
Stats Commands - Live statistics and data
"""
import logging
from typing import Optional

import discord
from discord import app_commands

from bot.services.stats import StatsService

logger = logging.getLogger(__name__)


class StatsCommands(app_commands.Group):
    """Commands for getting live statistics."""
    
    def __init__(self, bot):
        super().__init__(name="stats", description="Get live statistics and data")
        self.bot = bot
        self.stats_service = StatsService()
    
    @app_commands.command(name="team", description="Get team statistics")
    @app_commands.describe(team="Team name")
    async def team_stats(
        self,
        interaction: discord.Interaction,
        team: str
    ):
        """Get live team statistics."""
        await interaction.response.defer(thinking=True)
        
        try:
            stats = await self.stats_service.get_team_stats(team)
            
            if not stats:
                await interaction.followup.send(f"❌ Could not find stats for {team}", ephemeral=True)
                return
            
            # Format stats
            embed = discord.Embed(
                title=f"📊 {team} Statistics",
                color=0x00ff00
            )
            
            embed.add_field(
                name="Season Record",
                value=f"{stats.get('wins', 0)}-{stats.get('losses', 0)}",
                inline=True
            )
            
            embed.add_field(
                name="Win %",
                value=f"{stats.get('win_pct', 0):.3f}",
                inline=True
            )
            
            embed.add_field(
                name="Runs Scored",
                value=stats.get('runs_scored', 0),
                inline=True
            )
            
            embed.add_field(
                name="Runs Allowed",
                value=stats.get('runs_allowed', 0),
                inline=True
            )
            
            embed.add_field(
                name="Run Differential",
                value=stats.get('run_diff', 0),
                inline=True
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting team stats: {e}")
            await interaction.followup.send("❌ An error occurred while fetching stats.", ephemeral=True)
    
    @app_commands.command(name="player", description="Get player statistics")
    @app_commands.describe(player="Player name")
    async def player_stats(
        self,
        interaction: discord.Interaction,
        player: str
    ):
        """Get live player statistics."""
        await interaction.response.defer(thinking=True)
        
        try:
            stats = await self.stats_service.get_player_stats(player)
            
            if not stats:
                await interaction.followup.send(f"❌ Could not find stats for {player}", ephemeral=True)
                return
            
            # Format stats
            embed = discord.Embed(
                title=f"👤 {player} Statistics",
                color=0x00ff00
            )
            
            embed.add_field(
                name="Batting Average",
                value=f"{stats.get('avg', 0):.3f}",
                inline=True
            )
            
            embed.add_field(
                name="Home Runs",
                value=stats.get('hr', 0),
                inline=True
            )
            
            embed.add_field(
                name="RBIs",
                value=stats.get('rbi', 0),
                inline=True
            )
            
            embed.add_field(
                name="OPS",
                value=f"{stats.get('ops', 0):.3f}",
                inline=True
            )
            
            embed.add_field(
                name="Hits",
                value=stats.get('hits', 0),
                inline=True
            )
            
            embed.add_field(
                name="At Bats",
                value=stats.get('ab', 0),
                inline=True
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting player stats: {e}")
            await interaction.followup.send("❌ An error occurred while fetching stats.", ephemeral=True)
    
    @app_commands.command(name="live", description="Get live game scores")
    async def live_scores(
        self,
        interaction: discord.Interaction
    ):
        """Get live game scores."""
        await interaction.response.defer(thinking=True)
        
        try:
            live_games = await self.stats_service.get_live_scores()
            
            if not live_games:
                await interaction.followup.send("❌ No live games found.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="⚾ Live Games",
                color=0x00ff00
            )
            
            for game in live_games[:5]:  # Limit to 5 games
                embed.add_field(
                    name=f"{game['away_team']} @ {game['home_team']}",
                    value=f"{game['away_score']} - {game['home_score']} ({game['status']})",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting live scores: {e}")
            await interaction.followup.send("❌ An error occurred while fetching live scores.", ephemeral=True) 