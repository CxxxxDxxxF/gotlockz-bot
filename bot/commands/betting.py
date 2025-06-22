#!/usr/bin/env python3
"""
betting.py - Enhanced Betting Commands

Production-ready Discord bot commands for posting betting picks
with OCR integration, MLB data analysis, and intelligent formatting.
"""

import logging
import discord
from discord import app_commands
from typing import Optional
from datetime import datetime
import os
import re

# Import utilities
from utils.ocr import ocr_parser
from utils.mlb import mlb_fetcher

logger = logging.getLogger(__name__)


class BettingCommands(app_commands.Group):
    """Enhanced betting commands with OCR and MLB data integration."""

    def __init__(self, bot):
        super().__init__(name="betting", description="Betting pick commands")
        self.bot = bot
        self.pick_counters = self._load_counters()

    def _load_counters(self):
        """Load pick counters from file."""
        try:
            import json
            counter_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'pick_counters.json')
            if os.path.exists(counter_file):
                with open(counter_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading counters: {e}")
        return {'vip': 0, 'free': 0, 'lotto': 0}

    def _save_counters(self):
        """Save pick counters to file."""
        try:
            import json
            counter_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'pick_counters.json')
            os.makedirs(os.path.dirname(counter_file), exist_ok=True)
            with open(counter_file, 'w') as f:
                json.dump(self.pick_counters, f)
        except Exception as e:
            logger.error(f"Error saving counters: {e}")

    @app_commands.command(name="postpick", description="Post a pick with custom units and channel")
    @app_commands.describe(
        unitsize="Number of units (optional - if 0, units won't be shown)",
        channel="Channel to post the pick in",
        image="Upload a betting slip image"
    )
    async def postpick_command(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        image: discord.Attachment,
        unitsize: int = 0
    ):
        """Post a pick with custom units and channel specification."""
        try:
            await interaction.response.defer(thinking=True)

            # Validate inputs
            if not image.content_type or not image.content_type.startswith('image/'):
                await interaction.followup.send("❌ Please upload a valid image file!", ephemeral=True)
                return

            # Check if user has permission to post in the specified channel
            member = interaction.guild.get_member(interaction.user.id) if interaction.guild else None
            if member and not channel.permissions_for(member).send_messages:
                await interaction.followup.send(f"❌ You don't have permission to post in {channel.mention}!", ephemeral=True)
                return

            # Analyze the betting slip image
            bet_data = await self._analyze_betting_slip(image)

            # Fetch live MLB data
            mlb_data = await self._fetch_mlb_data(bet_data)

            # Get current date and time
            current_date = datetime.now().strftime("%m/%d/%y")
            current_time = datetime.now().strftime("%I:%M")

            # Determine channel type and increment counter
            channel_type = self._get_channel_type(channel.id)
            if channel_type:
                self.pick_counters[channel_type] += 1
                self._save_counters()

            # Generate the pick content with channel-specific template
            message_content = await self._generate_channel_specific_content(
                bet_data, mlb_data, current_date, current_time, unitsize, channel_type
            )

            # Post to the specified channel
            await channel.send(content=message_content)

            # Confirm to the user
            await interaction.followup.send(
                f"✅ Pick posted successfully in {channel.mention}!",
                ephemeral=True
            )

        except discord.errors.NotFound:
            logger.error("Interaction timed out and could not be found.")
            await interaction.followup.send(
                "❌ The command took too long to respond and timed out. Please try again.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in postpick command: {e}")
            await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    def _get_channel_type(self, channel_id: int) -> Optional[str]:
        """Determine the type of channel based on channel ID."""
        if channel_id == self.bot.vip_channel_id:
            return "vip"
        elif channel_id == self.bot.free_channel_id:
            return "free"
        elif channel_id == self.bot.lotto_channel_id:
            return "lotto"
        return None

    async def _generate_channel_specific_content(
        self,
        bet_data: dict,
        mlb_data: dict,
        current_date: str,
        current_time: str,
        unitsize: int,
        channel_type: Optional[str]
    ) -> str:
        """Generate channel-specific pick content with appropriate template."""

        # Format date and time without leading zeros
        formatted_date = self._format_date_no_zeros(current_date)
        formatted_time = self._format_time_no_zeros(current_time)

        # Determine pick type based on bet data
        pick_type = "PARLAY" if bet_data.get('is_parlay') else "FREE PLAY"

        # Get channel-specific template
        if channel_type == "vip":
            return await self._generate_vip_template(
                bet_data, mlb_data, formatted_date, formatted_time, unitsize, pick_type
            )
        elif channel_type == "lotto":
            return await self._generate_lotto_template(
                bet_data, mlb_data, formatted_date, formatted_time, unitsize, pick_type
            )
        elif channel_type == "free":
            return await self._generate_free_template(
                bet_data, mlb_data, formatted_date, formatted_time, unitsize, pick_type
            )
        else:
            # Default template for other channels
            return await self._generate_default_template(
                bet_data, mlb_data, formatted_date, formatted_time, unitsize, pick_type
            )

    async def _generate_vip_template(
        self,
        bet_data: dict,
        mlb_data: dict,
        formatted_date: str,
        formatted_time: str,
        unitsize: int,
        pick_type: str
    ) -> str:
        """Generate VIP channel template with premium formatting."""

        # Build the header
        header = f"**VIP PLAY – {formatted_date}**"
        if unitsize > 0:
            header += f"  \n💰 **{unitsize} UNITS**"

        # Game information
        teams = bet_data.get('teams', ['TBD', 'TBD'])
        game_info = f"⚾ | Game: {teams[0]} @ {teams[1]} ({formatted_date} {formatted_time} EST)"

        # Bet details
        bet_details = []
        if bet_data.get('is_parlay'):
            legs = bet_data.get('parlay_legs', [])
            for i, leg in enumerate(legs, 1):
                player = leg.get('player', 'TBD')
                description = leg.get('description', 'TBD')
                odds = leg.get('odds', 'TBD')
                bet_details.append(f"🏆 | Player {chr(64+i)} – {player} {description} ({odds})")

            combined_odds = bet_data.get('combined_odds', 'TBD')
            bet_details.append(f"💰 | Parlayed: {combined_odds}")
        else:
            player = bet_data.get('player', 'TBD')
            description = bet_data.get('description', 'TBD')
            odds = bet_data.get('odds', 'TBD')
            bet_details.append(f"🏆 | {player} – {description} ({odds})")

        # Analysis section
        analysis = await self._generate_analysis(bet_data, mlb_data, "")

        # Live stats section
        live_stats = await self._generate_live_stats_section(bet_data, mlb_data)

        # Build the complete message
        message_parts = [
            header,
            "",
            game_info,
            ""
        ]

        # Add bet details
        message_parts.extend(bet_details)
        message_parts.append("")

        # Add analysis
        message_parts.append("👇 | VIP Analysis Below:")
        message_parts.append("")
        message_parts.append(analysis)

        # Add live stats if available
        if live_stats:
            message_parts.append("")
            message_parts.append("📊 | Live Stats:")
            message_parts.append(live_stats)

        # Add VIP closing
        message_parts.append("")
        message_parts.append("🔒 VIP LOCK. 🔥")

        return "\n".join(message_parts)

    async def _generate_lotto_template(
        self,
        bet_data: dict,
        mlb_data: dict,
        formatted_date: str,
        formatted_time: str,
        unitsize: int,
        pick_type: str
    ) -> str:
        """Generate LOTTO channel template with lottery-style formatting."""

        # Build the header
        header = f"**LOTTO TICKET – {formatted_date}**"
        if unitsize > 0:
            header += f"  \n💰 **{unitsize} UNITS**"

        # Game information
        teams = bet_data.get('teams', ['TBD', 'TBD'])
        game_info = f"🎰 | Game: {teams[0]} @ {teams[1]} ({formatted_date} {formatted_time} EST)"

        # Generate lotto picks
        lotto_picks = await self._generate_lotto_picks(bet_data, mlb_data)

        # Analysis section
        analysis = await self._generate_analysis(bet_data, mlb_data, "")

        # Live stats section
        live_stats = await self._generate_live_stats_section(bet_data, mlb_data)

        # Build the complete message
        message_parts = [
            header,
            "",
            game_info,
            "",
            "🎯 | LOTTO PICKS:",
            lotto_picks,
            "",
            "👇 | Lotto Analysis Below:",
            "",
            analysis
        ]

        # Add live stats if available
        if live_stats:
            message_parts.append("")
            message_parts.append("📊 | Live Stats:")
            message_parts.append(live_stats)

        # Add lotto closing
        message_parts.append("")
        message_parts.append("🎰 HIT THE LOTTO! 🔥")

        return "\n".join(message_parts)

    async def _generate_free_template(
        self,
        bet_data: dict,
        mlb_data: dict,
        formatted_date: str,
        formatted_time: str,
        unitsize: int,
        pick_type: str
    ) -> str:
        """Generate FREE channel template with free play formatting."""

        # Build the header
        header = f"**FREE PLAY – {formatted_date}**"
        if unitsize > 0:
            header += f"  \n💰 **{unitsize} UNITS**"

        # Game information
        teams = bet_data.get('teams', ['TBD', 'TBD'])
        game_info = f"⚾ | Game: {teams[0]} @ {teams[1]} ({formatted_date} {formatted_time} EST)"

        # Bet details
        bet_details = []
        if bet_data.get('is_parlay'):
            legs = bet_data.get('parlay_legs', [])
            for i, leg in enumerate(legs, 1):
                player = leg.get('player', 'TBD')
                description = leg.get('description', 'TBD')
                odds = leg.get('odds', 'TBD')
                bet_details.append(f"🏆 | Player {chr(64+i)} – {player} {description} ({odds})")

            combined_odds = bet_data.get('combined_odds', 'TBD')
            bet_details.append(f"💰 | Parlayed: {combined_odds}")
        else:
            player = bet_data.get('player', 'TBD')
            description = bet_data.get('description', 'TBD')
            odds = bet_data.get('odds', 'TBD')
            bet_details.append(f"🏆 | {player} – {description} ({odds})")

        # Analysis section
        analysis = await self._generate_analysis(bet_data, mlb_data, "")

        # Live stats section
        live_stats = await self._generate_live_stats_section(bet_data, mlb_data)

        # Build the complete message
        message_parts = [
            header,
            "",
            game_info,
            ""
        ]

        # Add bet details
        message_parts.extend(bet_details)
        message_parts.append("")

        # Add analysis
        message_parts.append("👇 | Analysis Below:")
        message_parts.append("")
        message_parts.append(analysis)

        # Add live stats if available
        if live_stats:
            message_parts.append("")
            message_parts.append("📊 | Live Stats:")
            message_parts.append(live_stats)

        # Add free play closing
        message_parts.append("")
        message_parts.append("LOCK IT. 🔒🔥")

        return "\n".join(message_parts)

    async def _generate_default_template(
        self,
        bet_data: dict,
        mlb_data: dict,
        formatted_date: str,
        formatted_time: str,
        unitsize: int,
        pick_type: str
    ) -> str:
        """Generate default template for other channels."""

        # Build the header
        header = f"**{pick_type} – {formatted_date}**"
        if unitsize > 0:
            header += f"  \n💰 **{unitsize} UNITS**"

        # Game information
        teams = bet_data.get('teams', ['TBD', 'TBD'])
        game_info = f"⚾ | Game: {teams[0]} @ {teams[1]} ({formatted_date} {formatted_time} EST)"

        # Bet details
        bet_details = []
        if bet_data.get('is_parlay'):
            legs = bet_data.get('parlay_legs', [])
            for i, leg in enumerate(legs, 1):
                player = leg.get('player', 'TBD')
                description = leg.get('description', 'TBD')
                odds = leg.get('odds', 'TBD')
                bet_details.append(f"🏆 | Player {chr(64+i)} – {player} {description} ({odds})")

            combined_odds = bet_data.get('combined_odds', 'TBD')
            bet_details.append(f"💰 | Parlayed: {combined_odds}")
        else:
            player = bet_data.get('player', 'TBD')
            description = bet_data.get('description', 'TBD')
            odds = bet_data.get('odds', 'TBD')
            bet_details.append(f"🏆 | {player} – {description} ({odds})")

        # Analysis section
        analysis = await self._generate_analysis(bet_data, mlb_data, "")

        # Live stats section
        live_stats = await self._generate_live_stats_section(bet_data, mlb_data)

        # Build the complete message
        message_parts = [
            header,
            "",
            game_info,
            ""
        ]

        # Add bet details
        message_parts.extend(bet_details)
        message_parts.append("")

        # Add analysis
        message_parts.append("👇 | Analysis Below:")
        message_parts.append("")
        message_parts.append(analysis)

        # Add live stats if available
        if live_stats:
            message_parts.append("")
            message_parts.append("📊 | Live Stats:")
            message_parts.append(live_stats)

        # Add closing
        message_parts.append("")
        message_parts.append("LOCK IT. 🔒🔥")

        return "\n".join(message_parts)

    async def _analyze_betting_slip(self, image: discord.Attachment) -> dict:
        """Analyze betting slip image using OCR and extract bet details."""
        try:
            # Download image
            image_bytes = await image.read()

            # Use OCR to extract text from image
            extracted_text = await self._extract_text_from_image(image_bytes)

            # Parse betting details from extracted text
            bet_data = await self._parse_bet_details(extracted_text)

            return bet_data
        except Exception as e:
            logger.error(f"Error analyzing betting slip: {e}")
            return {
                'teams': ['TBD', 'TBD'],
                'player': 'TBD',
                'description': 'TBD',
                'odds': 'TBD',
                'units': '1',
                'game_time': 'TBD',
                'sport': 'MLB'
            }

    async def _extract_text_from_image(self, image_bytes: bytes) -> str:
        """Extract text from image using OCR."""
        try:
            # Use the OCR utility
            return await ocr_parser.extract_text_from_image(image_bytes)
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""

    async def _parse_bet_details(self, text: str) -> dict:
        """Parse betting details from OCR text."""
        try:
            # Use the OCR utility to parse betting details
            bet_data = ocr_parser.parse_betting_details(text)

            # Check if this is a parlay bet
            if self._is_parlay_bet(text, bet_data):
                parlay_data = self._parse_parlay_details(text, bet_data)
                return parlay_data

            return bet_data
        except Exception as e:
            logger.error(f"Error parsing bet details: {e}")
            return {
                'teams': ['TBD', 'TBD'],
                'player': 'TBD',
                'description': 'TBD',
                'odds': 'TBD',
                'units': '1',
                'game_time': 'TBD',
                'sport': 'MLB',
                'is_parlay': False,
                'legs': []
            }

    def _is_parlay_bet(self, text: str, bet_data: dict) -> bool:
        """Detect if this is a parlay bet."""
        parlay_indicators = [
            'parlay', 'parlayed', 'same game parlay', 'sgp',
            'multiple', 'legs', 'combined', 'total odds'
        ]

        text_lower = text.lower()

        # Check for parlay keywords
        for indicator in parlay_indicators:
            if indicator in text_lower:
                return True

        # Check for multiple player/prop patterns
        if text.count(' - ') > 1 or text.count('@') > 1:
            return True

        # Check for combined odds pattern (usually higher than individual)
        if bet_data.get('odds', ''):
            try:
                odds = int(bet_data['odds'].replace('+', '').replace('-', ''))
                if odds > 200:  # High odds often indicate parlays
                    return True
            except ValueError:
                pass

        return False

    def _parse_parlay_details(self, text: str, base_data: dict) -> dict:
        """Parse parlay bet details with multiple legs."""
        try:
            # Initialize parlay data
            parlay_data = {
                'teams': base_data.get('teams', ['TBD', 'TBD']),
                'player': 'PARLAY',
                'description': 'Multi-leg parlay',
                'odds': base_data.get('odds', 'TBD'),
                'units': base_data.get('units', '1'),
                'game_time': base_data.get('game_time', 'TBD'),
                'sport': base_data.get('sport', 'MLB'),
                'is_parlay': True,
                'legs': []
            }

            # Extract individual legs
            legs = self._extract_parlay_legs(text)
            if legs:
                parlay_data['legs'] = legs

                # Update combined odds if found
                combined_odds = self._extract_combined_odds(text)
                if combined_odds:
                    parlay_data['odds'] = combined_odds

            return parlay_data

        except Exception as e:
            logger.error(f"Error parsing parlay details: {e}")
            return {
                'teams': ['TBD', 'TBD'],
                'player': 'PARLAY',
                'description': 'Multi-leg parlay',
                'odds': 'TBD',
                'units': '1',
                'game_time': 'TBD',
                'sport': 'MLB',
                'is_parlay': True,
                'legs': []
            }

    def _extract_parlay_legs(self, text: str) -> list:
        """Extract individual legs from parlay text."""
        try:
            legs = []

            # Common patterns for parlay legs
            patterns = [
                # Pattern: Player - Prop (odds)
                r'([A-Za-z\s]+)\s*-\s*([^()]+)\s*\(([+-]?\d+)\)',
                # Pattern: Team ML/Spread (odds)
                r'([A-Za-z\s]+)\s+(ML|Spread|Total)\s*\(([+-]?\d+)\)',
                # Pattern: Over/Under (odds)
                r'(Over|Under)\s+([\d.]+)\s*\(([+-]?\d+)\)'
            ]

            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match) == 3:
                        legs.append({
                            'player': match[0].strip(),
                            'description': match[1].strip(),
                            'odds': match[2].strip()
                        })

            return legs

        except Exception as e:
            logger.error(f"Error extracting parlay legs: {e}")
            return []

    def _extract_combined_odds(self, text: str) -> str:
        """Extract combined odds from parlay text."""
        try:
            # Look for combined odds patterns
            patterns = [
                r'Combined\s+Odds:\s*([+-]?\d+)',
                r'Total\s+Odds:\s*([+-]?\d+)',
                r'Parlay\s+Odds:\s*([+-]?\d+)'
            ]

            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)

            return 'TBD'

        except Exception as e:
            logger.error(f"Error extracting combined odds: {e}")
            return 'TBD'

    async def _fetch_mlb_data(self, bet_data: dict) -> dict:
        """Fetch live MLB stats and current talk from multiple sources."""
        try:
            teams = bet_data.get('teams', ['TBD', 'TBD'])
            player = bet_data.get('player', 'TBD')

            # Fetch live data using the enhanced MLB utility
            away_team_stats = await mlb_fetcher.get_team_stats(teams[0])
            home_team_stats = await mlb_fetcher.get_team_stats(teams[1])
            player_stats = await mlb_fetcher.get_player_stats(player)
            game_info = await mlb_fetcher.get_game_info(teams[0], teams[1])

            # Get recent stats
            recent_player_stats = await mlb_fetcher.get_recent_player_stats(player)
            recent_away_stats = await mlb_fetcher.get_recent_team_stats(teams[0])

            # Get live scores
            live_scores = await mlb_fetcher.get_live_scores()

            # Combine player stats
            combined_player_stats = {**player_stats}
            if recent_player_stats:
                combined_player_stats.update(recent_player_stats)

            # Combine team stats
            combined_team_stats = {
                'away_record': f"{away_team_stats.get('wins', 0)}-{away_team_stats.get('losses', 0)}",
                'home_record': f"{home_team_stats.get('wins', 0)}-{home_team_stats.get('losses', 0)}",
                'away_pitcher': game_info.get('away_pitcher', 'TBD'),
                'home_pitcher': game_info.get('home_pitcher', 'TBD'),
                'recent_wins': recent_away_stats.get('recent_wins', 0),
                'recent_losses': recent_away_stats.get('recent_losses', 0),
                'recent_runs_per_game': recent_away_stats.get('recent_runs_per_game', 0)
            }

            return {
                'away_team': teams[0],
                'home_team': teams[1],
                'player_stats': combined_player_stats,
                'team_stats': combined_team_stats,
                'current_trends': f"{teams[0]} is {away_team_stats.get('win_pct', 0):.3f} this season",
                'weather': game_info.get('weather', 'Clear, 72°F'),
                'venue': game_info.get('venue', 'TBD Stadium'),
                'game_time': game_info.get('game_time', 'TBD'),
                'live_scores': live_scores.get('live_games', [])
            }
        except Exception as e:
            logger.error(f"Error fetching MLB data: {e}")
            return {
                'away_team': bet_data.get('teams', ['TBD', 'TBD'])[0],
                'home_team': bet_data.get('teams', ['TBD', 'TBD'])[1],
                'player_stats': {},
                'team_stats': {},
                'current_trends': 'Data unavailable',
                'weather': 'TBD',
                'venue': 'TBD',
                'live_scores': []
            }

    async def _generate_analysis(
            self,
            bet_data: dict,
            mlb_data: dict,
            context: str) -> str:
        """Generate intelligent analysis based on live data from multiple sources."""
        try:
            player = bet_data.get('player', 'TBD') or 'TBD'
            player_stats = mlb_data.get('player_stats', {}) or {}
            team_stats = mlb_data.get('team_stats', {}) or {}
            trends = mlb_data.get('current_trends', '') or ''
            weather = mlb_data.get('weather', '') or ''
            away_team = mlb_data.get('away_team', 'TBD') or 'TBD'
            home_team = mlb_data.get('home_team', 'TBD') or 'TBD'
            description = bet_data.get('description', 'TBD') or 'TBD'
            live_scores = mlb_data.get('live_scores', []) or []

            # Build comprehensive analysis
            analysis_parts = []

            # Live Game Status
            if live_scores:
                for game in live_scores:
                    away_match = away_team.lower() in game.get('away_team', '').lower()
                    home_match = home_team.lower() in game.get('home_team', '').lower()
                    if away_match or home_match:
                        analysis_parts.append(f"🔥 LIVE GAME: {game.get('away_team', '')} {game.get('away_score', 0)} - {game.get('home_team', '')} {game.get('home_score', 0)} (Inning {game.get('inning', 0)})")

            # Player Performance Analysis
            if player != 'TBD' and player_stats:
                avg = player_stats.get('batting_avg', '.000')
                hr = player_stats.get('hr', '0')
                rbi = player_stats.get('rbi', '0')
                ops = player_stats.get('ops', '.000')
                slg = player_stats.get('slg', '.000')
                obp = player_stats.get('obp', '.000')
                recent_avg = player_stats.get('recent_avg', '.000')

                # Determine player performance level
                avg_float = float(avg) if avg != '.000' else 0

                if avg_float >= 0.300:
                    performance_level = "🔥 HOT"
                elif avg_float >= 0.280:
                    performance_level = "✅ SOLID"
                elif avg_float >= 0.250:
                    performance_level = "📊 AVERAGE"
                else:
                    performance_level = "❄️ COLD"

                analysis_parts.append(
                    f"🎯 {player} ({performance_level}): Hitting {avg} with {hr} HRs, {rbi} RBIs, {ops} OPS this season."
                )

                # Add recent performance if available
                if recent_avg != '.000' and recent_avg != avg:
                    recent_avg_float = float(recent_avg)
                    if recent_avg_float > avg_float:
                        analysis_parts.append(f"📈 RECENT FORM: {recent_avg} in last 7 days - trending UP!")
                    elif recent_avg_float < avg_float:
                        analysis_parts.append(f"📉 RECENT FORM: {recent_avg} in last 7 days - trending down.")

                # Add specific prop analysis
                if 'hits' in description.lower() or 'total bases' in description.lower():
                    analysis_parts.append(f"📈 {player} has a {slg} slugging percentage, showing power potential.")
                elif 'runs' in description.lower() or 'rbi' in description.lower():
                    analysis_parts.append(f"🏃 {player} has driven in {rbi} runs with a {obp} on-base percentage.")
                elif 'home run' in description.lower():
                    analysis_parts.append(f"💪 {player} has {hr} home runs with a {slg} slugging percentage.")

            # Team Performance Analysis
            if team_stats:
                away_record = team_stats.get('away_record', '0-0')
                home_record = team_stats.get('home_record', '0-0')
                away_pitcher = team_stats.get('away_pitcher', 'TBD')
                home_pitcher = team_stats.get('home_pitcher', 'TBD')
                recent_wins = team_stats.get('recent_wins', 0)
                recent_losses = team_stats.get('recent_losses', 0)
                recent_runs_per_game = team_stats.get('recent_runs_per_game', 0)

                analysis_parts.append(f"🏟️ {away_team} ({away_record}) @ {home_team} ({home_record})")

                # Add recent team performance
                if recent_wins > 0 or recent_losses > 0:
                    recent_record = f"{recent_wins}-{recent_losses}"
                    if recent_wins > recent_losses:
                        analysis_parts.append(f"🔥 {away_team} is {recent_record} in last 10 games - HOT streak!")
                    elif recent_losses > recent_wins:
                        analysis_parts.append(f"❄️ {away_team} is {recent_record} in last 10 games - struggling.")

                if recent_runs_per_game > 0:
                    analysis_parts.append(f"⚡ {away_team} averaging {recent_runs_per_game:.1f} runs per game recently.")

                if away_pitcher != 'TBD' and home_pitcher != 'TBD':
                    analysis_parts.append(f"⚾ Pitching: {away_pitcher} vs {home_pitcher}")

            # Recent Team Trends
            if trends and trends != 'Data unavailable':
                analysis_parts.append(f"📊 {trends}")

            # Weather Impact Analysis
            if weather and weather != 'TBD':
                weather_lower = weather.lower()
                if 'clear' in weather_lower or 'sunny' in weather_lower:
                    analysis_parts.append("☀️ Clear weather conditions are favorable for hitting.")
                elif 'wind' in weather_lower:
                    if 'out' in weather_lower:
                        analysis_parts.append("💨 Wind blowing out - great for home runs and extra base hits.")
                    elif 'in' in weather_lower:
                        analysis_parts.append("💨 Wind blowing in - may suppress power numbers.")
                elif 'rain' in weather_lower:
                    analysis_parts.append("🌧️ Rain in forecast - may affect game conditions.")

            # Bet Type Specific Analysis
            if 'over' in description.lower():
                analysis_parts.append("📈 OVER PLAY: Both teams showing strong offensive potential.")
            elif 'under' in description.lower():
                analysis_parts.append("📉 UNDER PLAY: Pitching matchup favors lower scoring.")
            elif 'moneyline' in description.lower() or 'ml' in description.lower():
                analysis_parts.append("💰 MONEYLINE: Team has strong matchup advantages.")

            # Context Integration
            if context and context.strip():
                analysis_parts.append(f"💭 {context}")

            # Final Analysis Summary
            if not analysis_parts:
                analysis_parts.append("📊 Analysis based on current form and matchup data.")

            # Add confidence indicator based on data availability
            data_sources = 0
            if player_stats:
                data_sources += 1
            if team_stats:
                data_sources += 1
            if live_scores:
                data_sources += 1
            if weather != 'TBD':
                data_sources += 1

            if data_sources >= 3:
                confidence = "🔒 HIGH CONFIDENCE"
            elif data_sources >= 2:
                confidence = "📊 MODERATE CONFIDENCE"
            else:
                confidence = "⚠️ LOW CONFIDENCE"

            analysis_parts.append(f"\n{confidence} - Strong value at current odds.")

            return '\n\n'.join(analysis_parts)

        except Exception as e:
            logger.error(f"Error generating analysis: {e}")
            return f"{context or 'Analysis based on current form and matchup data.'}"

    async def _generate_lotto_picks(
            self,
            bet_data: dict,
            mlb_data: dict) -> str:
        """Generate multiple picks for lotto ticket."""
        try:
            # Extract data with fallbacks
            player = bet_data.get('player', 'TBD') or 'TBD'
            description = bet_data.get('description', 'TBD') or 'TBD'
            odds = bet_data.get('odds', 'TBD') or 'TBD'
            away_team = mlb_data.get('away_team', 'TBD') or 'TBD'
            home_team = mlb_data.get('home_team', 'TBD') or 'TBD'

            # Generate 4 picks based on current MLB data
            picks = [
                f"🏆 | Pick 1: {player} – {description} ({odds})",
                f"🏆 | Pick 2: {away_team} ML – Win ({odds})",
                f"🏆 | Pick 3: {home_team} TT Over – Team Total Over ({odds})",
                f"🏆 | Pick 4: {player} – RBI ({odds})"
            ]
            return '\n'.join(picks)

        except Exception as e:
            logger.error(f"Error generating lotto picks: {e}")
            return "🏆 | Pick 1: TBD – TBD (TBD)\n🏆 | Pick 2: TBD – TBD (TBD)\n🏆 | Pick 3: TBD – TBD (TBD)\n🏆 | Pick 4: TBD – TBD (TBD)"

    async def _generate_live_stats_section(self, bet_data: dict, mlb_data: dict) -> str:
        """Generate live stats section for the pick."""
        if not mlb_data or not mlb_data.get('player_stats'):
            return "Live stats unavailable"

        stats_lines = []
        player_stats = mlb_data.get('player_stats', {})

        # Handle the case where player_stats is a dict with player name as key
        if isinstance(player_stats, dict) and player_stats:
            # Get the player name from bet_data
            player_name = bet_data.get('player', 'Player')

            stats_lines.append(f"**{player_name}:**")
            if player_stats.get('batting_avg'):
                stats_lines.append(f"• AVG: {player_stats['batting_avg']}")
            if player_stats.get('hr'):
                stats_lines.append(f"• HR: {player_stats['hr']}")
            if player_stats.get('rbi'):
                stats_lines.append(f"• RBI: {player_stats['rbi']}")
            if player_stats.get('obp'):
                stats_lines.append(f"• OBP: {player_stats['obp']}")
            if player_stats.get('ops'):
                stats_lines.append(f"• OPS: {player_stats['ops']}")
            if player_stats.get('slg'):
                stats_lines.append(f"• SLG: {player_stats['slg']}")
            stats_lines.append("")

        return "\n".join(stats_lines) if stats_lines else "Live stats unavailable"

    def _format_date_no_zeros(self, date_str: str) -> str:
        """Format date without leading zeros (e.g., '06/22/25' -> '6/22/25')."""
        try:
            if '/' in date_str:
                parts = date_str.split('/')
                if len(parts) == 3:
                    month = str(int(parts[0]))  # Remove leading zero
                    day = str(int(parts[1]))    # Remove leading zero
                    year = parts[2]
                    return f"{month}/{day}/{year}"
        except (ValueError, IndexError):
            pass
        return date_str

    def _format_time_no_zeros(self, time_str: str) -> str:
        """Format time without leading zeros (e.g., '04:15' -> '4:15')."""
        try:
            if ':' in time_str:
                parts = time_str.split(':')
                if len(parts) == 2:
                    hour = str(int(parts[0]))   # Remove leading zero
                    minute = parts[1]
                    return f"{hour}:{minute}"
        except (ValueError, IndexError):
            pass
        return time_str


async def setup(bot):
    """Setup function for the commands."""
    logger.info("🔄 Setting up command groups...")

    try:
        # Add command groups
        betting_commands = BettingCommands(bot)

        bot.tree.add_command(betting_commands)

        logger.info("✅ Command groups added successfully")
    except Exception as e:
        logger.error(f"❌ Error adding command groups: {e}")
        raise
