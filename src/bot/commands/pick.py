"""
Pick Command - MLB betting pick command with channel selection
"""
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from bot.services.ocr import OCRService
from bot.services.mlb_integrated_service import MLBIntegratedService
from bot.services.analysis import AnalysisService
from bot.services.templates import TemplateService
from bot.services.player_analytics import PlayerAnalyticsService
from bot.services.weather_impact import WeatherImpactService

logger = logging.getLogger(__name__)


class PickCommands(app_commands.Group):
    """Commands for posting MLB betting picks."""
    
    def __init__(self, bot):
        super().__init__(name="pick", description="Post MLB betting picks with analysis")
        self.bot = bot
        self.ocr_service = OCRService()
        self.mlb_service = MLBIntegratedService()
        self.analysis_service = AnalysisService()
        self.template_service = TemplateService()
        self.player_service = PlayerAnalyticsService()
        self.weather_service = WeatherImpactService()

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
                assert bet_data is not None, "Expected non-None data before calling .get()"
                bet_data['description'] = f"{bet_data.get('description', 'TBD')} - {description}"

            # If OCR failed to extract teams or bet, notify user
            assert bet_data is not None, "Expected non-None data before calling .get()"
            if bet_data.get('teams', ['TBD', 'TBD'])[0] == 'TBD' or bet_data.get('teams', ['TBD', 'TBD'])[1] == 'TBD':
                await interaction.followup.send("❌ Could not extract teams from the bet slip. Please ensure the image is clear and the team names are visible.", ephemeral=True)
                return
            if bet_data.get('description', 'TBD') == 'TBD':
                await interaction.followup.send("❌ Could not extract bet description from the slip. Please ensure the bet type (e.g., Over/Under) is visible.", ephemeral=True)
                return

            # Fetch comprehensive MLB data with the new fast service
            stats_data = None
            try:
                stats_data = await asyncio.wait_for(
                    self.mlb_service.get_comprehensive_game_data(bet_data),
                    timeout=10.0  # Much faster timeout since new service is fast
                )
                logger.info("MLB data fetched successfully with new integrated service.")
                
                if stats_data:
                    logger.info(f"Data fetch time: {stats_data.get('performance_metrics', {}).get('fetch_time', 0):.2f}s")
                else:
                    logger.warning("No MLB data returned from integrated service")
                    
            except asyncio.TimeoutError:
                logger.warning("MLB data fetch timed out")
                stats_data = None
            except Exception as e:
                logger.error(f"MLB data fetch failed: {e}")
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
                
                # Send success message to user
                await interaction.followup.send(
                    f"✅ Pick posted successfully to {target_channel.mention}!",
                    ephemeral=True
                )
                
            except Exception as e:
                logger.error(f"Failed to post pick: {e}")
                await interaction.followup.send("❌ Failed to post pick. Please try again.", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Unexpected error in post_pick: {e}")
            await interaction.followup.send("❌ An unexpected error occurred. Please try again.", ephemeral=True)

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


class PickCommand(commands.Cog):
    """Advanced MLB pick command with real-time updates, player analytics, and weather impact."""
    
    def __init__(self, bot):
        self.bot = bot
        self.mlb_service = MLBIntegratedService()
        self.player_service = PlayerAnalyticsService()
        self.weather_service = WeatherImpactService()
    
    @commands.command(name="pick", help="Get advanced MLB analysis for a game")
    async def pick(self, ctx, team1: str, team2: str):
        """Get comprehensive MLB analysis including real-time updates, player analytics, and weather impact."""
        try:
            # Send initial response
            embed = discord.Embed(
                title="⚾ GotLockz Family - Advanced MLB Analysis",
                description="Loading comprehensive analysis...",
                color=0x00ff00
            )
            embed.set_footer(text="Powered by advanced MLB analytics")
            message = await ctx.send(embed=embed)
            
            # Initialize service if needed
            if not self.mlb_service.initialized:
                await self.mlb_service.initialize()
            
            # Get comprehensive game data
            bet_data = {'teams': [team1, team2]}
            game_data = await self.mlb_service.get_comprehensive_game_data(bet_data)
            
            if not game_data:
                error_embed = discord.Embed(
                    title="❌ Analysis Failed",
                    description=f"Could not load data for {team1} vs {team2}",
                    color=0xff0000
                )
                await message.edit(embed=error_embed)
                return
            
            # Extract weather data for analysis
            team1_weather = game_data.get('team1', {}).get('weather', {})
            venue = game_data.get('team1', {}).get('info', {}).get('venue', 'Unknown')
            
            # Get advanced analytics
            weather_impact = self.weather_service.analyze_weather_impact(team1_weather, venue)
            matchup_analysis = await self.player_service.get_matchup_analysis(team1, team2)
            
            # Get live updates if scraper is available
            live_updates = {}
            if self.mlb_service.scraper:
                live_updates = await self.mlb_service.scraper.get_live_game_updates()
            
            # Build comprehensive embed
            embed = await self._build_advanced_embed(
                game_data, weather_impact, matchup_analysis, live_updates, team1, team2
            )
            
            await message.edit(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in pick command: {e}")
            error_embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while analyzing the game.",
                color=0xff0000
            )
            await message.edit(embed=error_embed)
    
    @commands.command(name="live", help="Get real-time game updates")
    async def live(self, ctx, game_id: Optional[str] = None):
        """Get real-time updates for active games."""
        try:
            embed = discord.Embed(
                title="🔴 Live Game Updates",
                description="Loading live data...",
                color=0xff0000
            )
            message = await ctx.send(embed=embed)
            
            # Initialize service if needed
            if not self.mlb_service.initialized:
                await self.mlb_service.initialize()
            
            live_updates = {}
            if self.mlb_service.scraper:
                live_updates = await self.mlb_service.scraper.get_live_game_updates(game_id)
            
            if not live_updates:
                embed = discord.Embed(
                    title="🔴 Live Games",
                    description="No active games found",
                    color=0x808080
                )
                await message.edit(embed=embed)
                return
            
            embed = await self._build_live_embed(live_updates)
            await message.edit(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in live command: {e}")
            error_embed = discord.Embed(
                title="❌ Error",
                description="Failed to load live updates.",
                color=0xff0000
            )
            await message.edit(embed=error_embed)
    
    @commands.command(name="player", help="Get advanced player analytics")
    async def player(self, ctx, player_name: str):
        """Get comprehensive player statistics and analysis."""
        try:
            embed = discord.Embed(
                title="👤 Player Analytics",
                description=f"Loading data for {player_name}...",
                color=0x0099ff
            )
            message = await ctx.send(embed=embed)
            
            player_stats = await self.player_service.get_player_stats(player_name)
            
            if not player_stats:
                embed = discord.Embed(
                    title="❌ Player Not Found",
                    description=f"Could not find data for {player_name}",
                    color=0xff0000
                )
                await message.edit(embed=embed)
                return
            
            embed = await self._build_player_embed(player_stats)
            await message.edit(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in player command: {e}")
            error_embed = discord.Embed(
                title="❌ Error",
                description="Failed to load player data.",
                color=0xff0000
            )
            await message.edit(embed=error_embed)
    
    @commands.command(name="weather", help="Get weather impact analysis")
    async def weather(self, ctx, team1: str, team2: str):
        """Get detailed weather impact analysis for a game."""
        try:
            embed = discord.Embed(
                title="🌤️ Weather Impact Analysis",
                description="Analyzing weather conditions...",
                color=0x87ceeb
            )
            message = await ctx.send(embed=embed)
            
            # Initialize service if needed
            if not self.mlb_service.initialized:
                await self.mlb_service.initialize()
            
            # Get game data for weather
            bet_data = {'teams': [team1, team2]}
            game_data = await self.mlb_service.get_comprehensive_game_data(bet_data)
            
            if not game_data:
                error_embed = discord.Embed(
                    title="❌ Analysis Failed",
                    description=f"Could not load weather data for {team1} vs {team2}",
                    color=0xff0000
                )
                await message.edit(embed=error_embed)
                return
            
            team1_weather = game_data.get('team1', {}).get('weather', {})
            venue = game_data.get('team1', {}).get('info', {}).get('venue', 'Unknown')
            
            weather_impact = self.weather_service.analyze_weather_impact(team1_weather, venue)
            
            embed = await self._build_weather_embed(weather_impact, team1, team2)
            await message.edit(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in weather command: {e}")
            error_embed = discord.Embed(
                title="❌ Error",
                description="Failed to analyze weather impact.",
                color=0xff0000
            )
            await message.edit(embed=error_embed)
    
    async def _build_advanced_embed(self, game_data: Dict[str, Any], weather_impact: Dict[str, Any],
                                   matchup_analysis: Dict[str, Any], live_updates: Dict[str, Any],
                                   team1: str, team2: str) -> discord.Embed:
        """Build comprehensive analysis embed."""
        embed = discord.Embed(
            title="⚾ GotLockz Family - Advanced MLB Analysis",
            description="Free play is here! Comprehensive game analysis with real-time updates",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        
        # Basic game info
        team1_data = game_data.get('team1', {})
        team2_data = game_data.get('team2', {})
        
        # Game summary
        embed.add_field(
            name="🏟️ Game Info",
            value=f"**{team1}** vs **{team2}**\n"
                  f"Venue: {team1_data.get('info', {}).get('venue', 'Unknown')}\n"
                  f"Status: {game_data.get('game_info', {}).get('status', 'Unknown')}",
            inline=False
        )
        
        # Team records
        team1_stats = team1_data.get('basic_stats', {})
        team2_stats = team2_data.get('basic_stats', {})
        
        embed.add_field(
            name=f"📊 {team1}",
            value=f"Record: {team1_stats.get('record', 'N/A')}\n"
                  f"Win %: {team1_stats.get('win_pct', 0):.3f}",
            inline=True
        )
        
        embed.add_field(
            name=f"📊 {team2}",
            value=f"Record: {team2_stats.get('record', 'N/A')}\n"
                  f"Win %: {team2_stats.get('win_pct', 0):.3f}",
            inline=True
        )
        
        # Weather impact
        weather_summary = self.weather_service.get_weather_summary(
            team1_data.get('weather', {}), team1_data.get('info', {}).get('venue')
        )
        embed.add_field(
            name="🌤️ Weather Impact",
            value=weather_summary,
            inline=False
        )
        
        # Live updates if available
        active_games = live_updates.get('active_games', [])
        if active_games:
            for game in active_games:
                if (game.get('away_team') == team1 and game.get('home_team') == team2) or \
                   (game.get('away_team') == team2 and game.get('home_team') == team1):
                    embed.add_field(
                        name="🔴 Live Game",
                        value=f"Score: {game.get('away_score', 0)}-{game.get('home_score', 0)}\n"
                              f"Inning: {game.get('current_inning', 'N/A')} {game.get('inning_state', '')}\n"
                              f"Batter: {game.get('batter', 'N/A')}",
                        inline=False
                    )
                    break
        
        # Matchup analysis
        if matchup_analysis:
            key_matchups = matchup_analysis.get('key_matchups', [])
            embed.add_field(
                name="⚔️ Key Matchups",
                value=f"{len(key_matchups)} key matchups identified\n"
                      "Focus on starting pitcher performance",
                inline=False
            )
        
        embed.set_footer(text="Advanced analytics powered by MLB data")
        return embed
    
    async def _build_live_embed(self, live_updates: Dict[str, Any]) -> discord.Embed:
        """Build live updates embed."""
        embed = discord.Embed(
            title="🔴 Live MLB Games",
            description="Real-time game updates",
            color=0xff0000,
            timestamp=datetime.now()
        )
        
        active_games = live_updates.get('active_games', [])
        total_active = live_updates.get('total_active', 0)
        
        if not active_games:
            embed.description = "No active games currently"
            return embed
        
        embed.description = f"**{total_active}** active games"
        
        for i, game in enumerate(active_games[:5]):  # Show max 5 games
            embed.add_field(
                name=f"⚾ {game.get('away_team')} @ {game.get('home_team')}",
                value=f"Score: **{game.get('away_score', 0)}-{game.get('home_score', 0)}**\n"
                      f"Inning: {game.get('current_inning', 'N/A')} {game.get('inning_state', '')}\n"
                      f"Outs: {game.get('outs', 0)}\n"
                      f"Runners: {len(game.get('runners', []))} on base",
                inline=False
            )
        
        embed.set_footer(text=f"Last updated: {live_updates.get('last_updated', 'Unknown')}")
        return embed
    
    async def _build_player_embed(self, player_stats: Dict[str, Any]) -> discord.Embed:
        """Build player analytics embed."""
        player_info = player_stats.get('player_info', {})
        batting_stats = player_stats.get('batting', {})
        pitching_stats = player_stats.get('pitching', {})
        
        embed = discord.Embed(
            title=f"👤 {player_info.get('name', 'Unknown Player')}",
            description=f"Advanced player analytics",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        # Player info
        embed.add_field(
            name="📋 Player Info",
            value=f"Position: {player_info.get('position', 'N/A')}\n"
                  f"Team: {player_info.get('team', 'N/A')}\n"
                  f"Age: {player_info.get('age', 'N/A')}\n"
                  f"Bats: {player_info.get('bats', 'N/A')} | Throws: {player_info.get('throws', 'N/A')}",
            inline=False
        )
        
        # Batting stats
        if batting_stats:
            embed.add_field(
                name="⚾ Batting Stats",
                value=f"AVG: {batting_stats.get('avg', 0):.3f}\n"
                      f"OBP: {batting_stats.get('obp', 0):.3f}\n"
                      f"SLG: {batting_stats.get('slg', 0):.3f}\n"
                      f"HR: {batting_stats.get('home_runs', 0)} | RBI: {batting_stats.get('rbi', 0)}",
                inline=True
            )
        
        # Pitching stats
        if pitching_stats:
            embed.add_field(
                name="🎯 Pitching Stats",
                value=f"ERA: {pitching_stats.get('era', 0):.2f}\n"
                      f"W-L: {pitching_stats.get('wins', 0)}-{pitching_stats.get('losses', 0)}\n"
                      f"SO: {pitching_stats.get('strikeouts', 0)}\n"
                      f"WHIP: {pitching_stats.get('whip', 0):.2f}",
                inline=True
            )
        
        embed.set_footer(text=f"Season: {player_stats.get('season', 'N/A')}")
        return embed
    
    async def _build_weather_embed(self, weather_impact: Dict[str, Any], team1: str, team2: str) -> discord.Embed:
        """Build weather impact embed."""
        embed = discord.Embed(
            title=f"🌤️ Weather Impact: {team1} vs {team2}",
            description="Detailed weather analysis and betting implications",
            color=0x87ceeb,
            timestamp=datetime.now()
        )
        
        overall_impact = weather_impact.get('overall_impact', {})
        recommendations = weather_impact.get('recommendations', [])
        betting_implications = weather_impact.get('betting_implications', {})
        
        # Overall impact
        embed.add_field(
            name="📊 Overall Impact",
            value=f"Category: **{overall_impact.get('category', 'Unknown')}**\n"
                  f"Factor: {overall_impact.get('factor', 1.0)}\n"
                  f"Hitting Boost: {overall_impact.get('hitting_boost', 0):+.1f}%\n"
                  f"Risk Level: {weather_impact.get('risk_level', 'UNKNOWN')}",
            inline=False
        )
        
        # Recommendations
        if recommendations:
            rec_text = "\n".join([f"• {rec}" for rec in recommendations[:3]])
            embed.add_field(
                name="💡 Recommendations",
                value=rec_text,
                inline=False
            )
        
        # Betting implications
        if betting_implications:
            bet_text = ""
            for bet_type, data in betting_implications.items():
                bet_text += f"• **{bet_type.replace('_', ' ').title()}**: {data.get('adjustment', '0%')} - {data.get('recommendation', 'Neutral')}\n"
            
            embed.add_field(
                name="💰 Betting Implications",
                value=bet_text,
                inline=False
            )
        
        embed.set_footer(text="Weather analysis based on historical MLB data")
        return embed


async def setup(bot):
    """Setup the pick command cog."""
    await bot.add_cog(PickCommand(bot)) 