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
from bot.utils.ocr import ocr_parser
from bot.utils.mlb import mlb_fetcher

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
        return {'vip': 0, 'free': 0, 'lotto': 0, 'parlay': 0}

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
        """Post a VIP pick with enhanced analysis."""
        await self._post_pick(interaction, image, context, "vip")

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
        """Post a lotto pick with enhanced analysis."""
        await self._post_pick(interaction, image, context, "lotto")

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
        """Post a free pick with enhanced analysis."""
        await self._post_pick(interaction, image, context, "free")

    @app_commands.command(name="parlay", description="Post a parlay pick")
    @app_commands.describe(
        image="Upload a parlay betting slip image",
        context="Optional context or notes"
    )
    async def parlay_command(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        context: Optional[str] = None
    ):
        """Post a parlay pick with enhanced analysis."""
        await self._post_pick(interaction, image, context, "parlay")

    @app_commands.command(name="analyze",
                          description="Analyze a betting slip image")
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
        """Analyze a betting slip image with detailed breakdown."""
        await interaction.response.defer(thinking=True)

        try:
            # Validate image
            if not image.content_type or not image.content_type.startswith('image/'):
                await interaction.followup.send("❌ Please upload a valid image file!", ephemeral=True)
                return

            # Analyze the betting slip image
            bet_data = await self._analyze_betting_slip(image)

            # Fetch live MLB data
            mlb_data = await self._fetch_mlb_data(bet_data)

            # Generate analysis
            analysis = await self._generate_analysis(bet_data, mlb_data, str(context or ""))

            # Create detailed breakdown
            breakdown = f"""📊 **BETTING SLIP ANALYSIS**

🎯 **Bet Details:**
• Player: {bet_data.get('player', 'TBD')}
• Description: {bet_data.get('description', 'TBD')}
• Odds: {bet_data.get('odds', 'TBD')}
• Teams: {bet_data.get('teams', ['TBD', 'TBD'])[0]} @ {bet_data.get('teams', ['TBD', 'TBD'])[1]}
• Type: {'Parlay' if bet_data.get('is_parlay') else 'Single'}

📈 **Live Analysis:**
{analysis}

🔍 **Raw OCR Text:**
```
{await self._extract_text_from_image(await image.read())}
```"""

            await interaction.followup.send(content=breakdown, ephemeral=True)

        except Exception as e:
            logger.error(f"Error in analyze command: {e}")
            await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

    async def _post_pick(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        context: Optional[str],
        pick_type: str
    ):
        """Post a pick to Discord using intelligent analysis and live data."""
        await interaction.response.defer(thinking=True)

        try:
            # Validate image
            if not image.content_type or not image.content_type.startswith('image/'):
                await interaction.followup.send("❌ Please upload a valid image file!", ephemeral=True)
                return

            # Increment counter
            self.pick_counters[pick_type] += 1
            self._save_counters()

            # Get current date and time
            current_date = datetime.now().strftime("%m/%d/%y")
            current_time = datetime.now().strftime("%I:%M")

            # Analyze the betting slip image
            bet_data = await self._analyze_betting_slip(image)

            # Fetch live MLB data and current talk
            mlb_data = await self._fetch_mlb_data(bet_data)

            # Generate contextual response based on pick type and channel
            message_content = await self._generate_pick_content(
                pick_type, bet_data, mlb_data, current_date, current_time, str(context or "")
            )

            # Determine target channel based on pick type
            target_channel_id = self._get_target_channel_id(pick_type)

            # Send to appropriate channel
            if target_channel_id and target_channel_id != interaction.channel_id:
                target_channel = self.bot.get_channel(target_channel_id)
                if target_channel:
                    await target_channel.send(content=message_content, file=await image.to_file())
                    await interaction.followup.send(f"✅ {pick_type.upper()} pick posted to <#{target_channel_id}>!", ephemeral=True)
                else:
                    await interaction.followup.send(content=message_content, file=await image.to_file())
            else:
                await interaction.followup.send(content=message_content, file=await image.to_file())

            logger.info(
                f"Posted {pick_type} pick #{self.pick_counters[pick_type]} by {interaction.user}")

        except Exception as e:
            logger.error(f"Error in {pick_type} command: {e}")
            await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

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

    async def _generate_pick_content(
            self,
            pick_type: str,
            bet_data: dict,
            mlb_data: dict,
            current_date: str,
            current_time: str,
            context: str) -> str:
        """Generate contextual pick content based on type and data."""

        try:
            # Extract data with fallbacks
            away_team = mlb_data.get('away_team', bet_data.get('teams', ['TBD', 'TBD'])[0]) or 'TBD'
            home_team = mlb_data.get('home_team', bet_data.get('teams', ['TBD', 'TBD'])[1]) or 'TBD'
            player = bet_data.get('player', 'TBD') or 'TBD'
            description = bet_data.get('description', 'TBD') or 'TBD'
            odds = bet_data.get('odds', 'TBD') or 'TBD'
            units = bet_data.get('units', '1') or '1'

            # Generate analysis based on live data
            analysis = await self._generate_analysis(bet_data, mlb_data, context)

            # Format date/time without leading zeros
            formatted_date = self._format_date_no_zeros(current_date)
            formatted_time = self._format_time_no_zeros(current_time)
            game_time = f"{formatted_date} {formatted_time} PM EST"

            if pick_type == "vip":
                return f"""🔒 | VIP PLAY #{self.pick_counters[pick_type]} 🏆 – {formatted_date}
⚾ | Game: {away_team} @ {home_team} ({game_time})
🏆 | {player} – {description} ({odds})
💵 | Unit Size: {units}
👇 | Analysis Below:

{analysis}"""

            elif pick_type == "free":
                return f"""FREE PLAY – {formatted_date}
⚾ | Game: {away_team} @ {home_team} ({game_time})
🏆 | {player} – {description} ({odds})
👇 | Analysis Below:

{analysis}

LOCK IT. 🔒🔥"""

            elif pick_type == "lotto":
                # Generate multiple picks for lotto
                picks = await self._generate_lotto_picks(bet_data, mlb_data)
                return f"""🔒 | LOTTO TICKET 🎰 – {formatted_date}
{picks}
💰 | Parlayed: {odds}
🍀 | GOOD LUCK TO ALL TAILING
( THESE ARE 1 UNIT PLAYS )"""

            elif pick_type == "parlay":
                # Handle parlay with individual legs
                if bet_data.get('is_parlay', False) and bet_data.get('legs'):
                    legs_content = []
                    for leg in bet_data['legs']:
                        legs_content.append(f"🏆 | {leg.get('player', 'TBD')} – {leg.get('description', 'TBD')} ({leg.get('odds', 'TBD')})")

                    legs_text = '\n'.join(legs_content)
                    return f"""FREE PLAY – {formatted_date}
⚾ | Game: {away_team} @ {home_team} ({game_time})

{legs_text}
💰 | Parlayed: {odds}

👇 | Analysis Below:

{analysis}

LOCK IT. 🔒🔥"""
                else:
                    # Fallback for single parlay
                    return f"""FREE PLAY – {formatted_date}
⚾ | Game: {away_team} @ {home_team} ({game_time})
🏆 | {player} – {description} ({odds})
👇 | Analysis Below:

{analysis}

LOCK IT. 🔒🔥"""

            return "Error generating content"

        except Exception as e:
            logger.error(f"Error generating pick content: {e}")
            return f"❌ Error generating {pick_type} pick content. Please try again."

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
                    if (away_team.lower() in game.get('away_team', '').lower() or 
                        home_team.lower() in game.get('home_team', '').lower()):
                        analysis_parts.append(f"🔥 LIVE GAME: {game.get('away_team', '')} {game.get('away_score', 0)} - {game.get('home_team', '')} {game.get('home_score', 0)} (Inning {game.get('inning', 0)})")

            # Player Performance Analysis
            if player != 'TBD' and player_stats:
                avg = player_stats.get('avg', '.000')
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
            if player_stats: data_sources += 1
            if team_stats: data_sources += 1
            if live_scores: data_sources += 1
            if weather != 'TBD': data_sources += 1

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

    def _get_target_channel_id(self, pick_type: str) -> Optional[int]:
        """Get the target channel ID based on pick type."""
        if pick_type == "vip":
            return self.bot.vip_channel_id
        elif pick_type == "lotto":
            return self.bot.lotto_channel_id
        elif pick_type == "free":
            return self.bot.free_channel_id
        return None


class InfoCommands(app_commands.Group):
    """Information and utility commands."""

    def __init__(self, bot):
        super().__init__(name="info", description="Bot information and utilities")
        self.bot = bot

    @app_commands.command(name="ping", description="Test bot responsiveness")
    async def ping_command(self, interaction: discord.Interaction):
        """Test bot responsiveness."""
        await interaction.response.send_message("🏓 Pong! Bot is online!")

    @app_commands.command(name="status", description="Check bot status")
    async def status_command(self, interaction: discord.Interaction):
        """Check bot status."""
        status_text = f"""🤖 BOT STATUS
✅ Status: Online
⚡ Latency: {round(self.bot.latency * 1000)}ms
⏰ Uptime: {self.bot.get_uptime()}
🏠 Servers: {len(self.bot.guilds)}
👥 Users: {len(self.bot.users)}
🔧 Commands: {len(self.bot.tree.get_commands())}"""

        await interaction.response.send_message(content=status_text)

    @app_commands.command(name="stats", description="View bot statistics")
    async def stats_command(self, interaction: discord.Interaction):
        """View bot statistics."""
        stats_text = f"""📊 BOT STATISTICS
🎯 Pick Counters:
   VIP: {self.bot.pick_counters['vip']}
   Lotto: {self.bot.pick_counters['lotto']}
   Free: {self.bot.pick_counters['free']}
   Parlay: {self.bot.pick_counters['parlay']}

🤖 Bot Status:
   Dashboard: {'✅' if self.bot.dashboard_enabled else '❌'}
   Channels: {'✅' if self.bot.channels_configured else '❌'}
   Uptime: {self.bot.get_uptime()}"""

        await interaction.response.send_message(content=stats_text)

    @app_commands.command(name="force_sync",
                          description="Force sync all commands")
    async def force_sync_command(self, interaction: discord.Interaction):
        """Force sync all commands."""
        await interaction.response.defer(thinking=True)

        try:
            synced = await self.bot.tree.sync()
            sync_text = f"""🔄 FORCE SYNC
✅ Status: Commands synced
🔧 Commands: {len(synced)}"""

            await interaction.followup.send(content=sync_text)
        except Exception as e:
            await interaction.followup.send(f"❌ Force sync failed: {e}")


async def setup(bot):
    """Setup function for the commands."""
    logger.info("🔄 Setting up command groups...")

    try:
        # Add command groups
        betting_commands = BettingCommands(bot)
        info_commands = InfoCommands(bot)

        bot.tree.add_command(betting_commands)
        bot.tree.add_command(info_commands)

        logger.info("✅ Command groups added successfully")
    except Exception as e:
        logger.error(f"❌ Error adding command groups: {e}")
        raise
