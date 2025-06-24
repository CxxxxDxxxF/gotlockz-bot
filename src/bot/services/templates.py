"""
Template Service - Handles different posting formats for picks
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from config.settings import settings

logger = logging.getLogger(__name__)


class TemplateService:
    """Service for formatting picks with different templates."""
    
    def __init__(self):
        self.templates = settings.templates
        self.vip_play_counter = 1  # Simple counter for VIP play numbers
    
    def _get_leg_stat_summary(self, leg, stats_data):
        """Return a stat summary string for a leg if stats are available."""
        # Try to match by player or team
        player = leg.get('player', '')
        team = ''
        if 'teams' in leg and len(leg['teams']) > 0:
            team = leg['teams'][0]
        # Example: look for HR, hard-hit, etc. in stats_data
        # This is a simple example; you can expand as needed
        if stats_data:
            for key in ['team1', 'team2']:
                s = stats_data.get(key, {})
                if team and (team.lower() in s.get('team_name', '').lower() or team.lower() in key.lower()):
                    # Example summary for HR and hard-hit
                    hr = s.get('home_runs', None)
                    hard_hit = s.get('hard_hit_pct', None)
                    if hr is not None and hard_hit is not None:
                        return f"📊 {player or team}: {hr} HR, {hard_hit}% hard-hit"
                    elif hr is not None:
                        return f"📊 {player or team}: {hr} HR"
                    elif hard_hit is not None:
                        return f"📊 {player or team}: {hard_hit}% hard-hit"
        return None

    def _get_weather_park_summary(self, stats_data):
        """Return a weather and park factor summary if available."""
        lines = []
        if stats_data:
            weather = stats_data.get('weather', {})
            park = stats_data.get('park_factors', {})
            
            # Handle new weather data structure
            if weather and weather.get('available', False):
                if weather.get('summary'):
                    # Use the formatted summary from weather service
                    lines.append(weather['summary'])
                else:
                    # Fallback to individual weather data
                    weather_data = weather.get('data', {})
                    if weather_data:
                        for team, data in weather_data.items():
                            temp = data.get('temperature', 'N/A')
                            wind = data.get('wind_speed', 'N/A')
                            cond = data.get('conditions', 'N/A')
                            lines.append(f"🌦️ {team}: {temp}°F, {wind} mph wind, {cond}")
            elif weather and weather.get('fallback'):
                # Use fallback weather data
                fallback = weather['fallback']
                temp = fallback.get('temperature', 'N/A')
                wind = fallback.get('wind_speed', 'N/A')
                cond = fallback.get('conditions', 'N/A')
                lines.append(f"🌦️ Weather: {temp}°F, {wind} mph wind, {cond}")
            
            # Park factors
            if park:
                runs = park.get('runs', 'N/A')
                hr = park.get('hr', 'N/A')
                if runs != 'N/A' or hr != 'N/A':
                    lines.append(f"🏟️ Park Factor: {runs} runs, {hr} HR")
        
        return '\n'.join(lines)

    def format_free_play(self, bet_data: Dict[str, Any], stats_data: Optional[Dict[str, Any]] = None, analysis: str = "") -> str:
        """Format a free play pick to match the Discord screenshot style, with stat summaries and weather/park."""
        try:
            teams = bet_data.get('teams', ['TBD', 'TBD'])
            description = bet_data.get('description', 'TBD')
            odds = bet_data.get('odds', 'TBD')
            legs = bet_data.get('legs', [])
            current_date = datetime.now().strftime(self.templates.date_format)
            current_time = datetime.now().strftime(self.templates.time_format)

            header = f"# __**🔒 FREE PLAY - {current_date} 🔒**__"
            game_info = f"**⚾ GAME:**  __{teams[0]} @ {teams[1]}__  ({current_date} {current_time})"
            bet_info = f"**🏆 PICK:**  __{description}__  |  **Odds:** __{odds}__"

            # Add stat summaries for each leg if available
            leg_summaries = []
            for leg in legs:
                summary = self._get_leg_stat_summary(leg, stats_data)
                if summary:
                    leg_summaries.append(summary)
            leg_summaries_section = '\n'.join(leg_summaries) if leg_summaries else ''

            # Add weather/park summary if available
            weather_park_section = self._get_weather_park_summary(stats_data)

            analysis_label = "\n👇 **Analysis Below:**\n"
            analysis_section = f"**{analysis}**" if analysis else "No analysis available."

            content = f"{header}\n\n{game_info}\n\n{bet_info}"
            if leg_summaries_section:
                content += f"\n{leg_summaries_section}"
            if weather_park_section:
                content += f"\n{weather_park_section}"
            content += f"{analysis_label}\n{analysis_section}"
            return content
        except Exception as e:
            logger.error(f"Error formatting free play: {e}")
            return self._get_fallback_format(bet_data, "FREE PLAY")
    
    def format_vip_pick(self, bet_data: Dict[str, Any], stats_data: Optional[Dict[str, Any]] = None, analysis: str = "") -> str:
        """Format a VIP pick with multi-leg parlay/SGP support, stat summaries, and weather/park."""
        try:
            teams = bet_data.get('teams', ['TBD', 'TBD'])
            odds = bet_data.get('odds', 'TBD')
            units = bet_data.get('units', '1')
            legs = bet_data.get('legs', [])
            current_date = datetime.now().strftime(self.templates.date_format)
            current_time = datetime.now().strftime(self.templates.time_format)

            header = f"🔒 I VIP PLAY # {self.vip_play_counter} 🏆 - {current_date}"

            # If multi-leg parlay/SGP, list all games and legs
            if legs and len(legs) > 1:
                # Collect all unique games
                games = set()
                for leg in legs:
                    if 'teams' in leg and len(leg['teams']) == 2:
                        games.add(f"{leg['teams'][0]} @ {leg['teams'][1]}")
                games_list = sorted(games)
                games_section = "\n   - " + "\n   - ".join(games_list) + f"\n   ({current_date} {current_time})"
                game_info = f"⚾️ I Games:{games_section}"

                # List each leg with stat summary if available
                leg_lines = []
                for leg in legs:
                    player = leg.get('player', '').strip()
                    desc = leg.get('description', '').strip()
                    team = ''
                    if 'teams' in leg and len(leg['teams']) == 2:
                        team = f" [{leg['teams'][0][:3].upper()}]"
                    # Only show the most informative, non-redundant pick line
                    if player and desc:
                        # If desc is just a repeat of player, only show one
                        if player == desc or player in desc or desc in player:
                            leg_line = f"🏆 I {desc}{team}"
                        else:
                            leg_line = f"🏆 I {player} {desc}{team}"
                    elif player:
                        leg_line = f"🏆 I {player}{team}"
                    elif desc:
                        leg_line = f"🏆 I {desc}{team}"
                    else:
                        continue
                    # Add stat summary if available
                    summary = self._get_leg_stat_summary(leg, stats_data)
                    if summary:
                        leg_line += f"\n   {summary}"
                    leg_lines.append(leg_line)
                legs_section = "\n".join(leg_lines)

                # Parlayed odds
                parlay_odds = f"💰| Parlayed: {odds}" if odds != 'TBD' else ''

                # Unit size
                units_display = f"💵 I Unit Size: {units}"

                # Weather/park summary if available
                weather_park_section = self._get_weather_park_summary(stats_data)

                # Analysis section
                analysis_label = "👇 I Analysis Below:"
                analysis_section = analysis if analysis else "Analysis to be provided."

                # Combine all sections
                content_parts = [
                    header,
                    game_info,
                    "",
                    legs_section,
                    "",
                    parlay_odds,
                    "",
                    units_display
                ]
                if weather_park_section:
                    content_parts.extend(["", weather_park_section])
                content_parts.extend(["", analysis_label, "", analysis_section])
                content = "\n".join([part for part in content_parts if part])
                self.vip_play_counter += 1
                return content
            else:
                # Fallback to old format for single-leg bets
                description = bet_data.get('description', 'TBD')
                game_info = f"⚾️ I Game: {teams[0]} @ {teams[1]}  ({current_date} {current_time})"
                bet_info = f"🏆 I {description}"
                if odds != 'TBD':
                    bet_info += f" ({odds})"
                units_display = f"💵 I Unit Size: {units}"
                weather_park_section = self._get_weather_park_summary(stats_data)
                analysis_label = "👇 I Analysis Below:"
                analysis_section = analysis if analysis else "Analysis to be provided."
                content_parts = [header, game_info, "", bet_info, "", units_display]
                if weather_park_section:
                    content_parts.extend(["", weather_park_section])
                content_parts.extend(["", analysis_label, "", analysis_section])
                content = "\n".join(content_parts)
                self.vip_play_counter += 1
                return content
        except Exception as e:
            logger.error(f"Error formatting VIP pick: {e}")
            return self._get_fallback_format(bet_data, "VIP PICK")
    
    def format_lotto_ticket(self, bet_data: Dict[str, Any], stats_data: Optional[Dict[str, Any]] = None, analysis: str = "") -> str:
        """Format a lotto ticket pick with stat summaries and weather/park."""
        try:
            teams = bet_data.get('teams', ['TBD', 'TBD'])
            description = bet_data.get('description', 'TBD')
            odds = bet_data.get('odds', 'TBD')
            legs = bet_data.get('legs', [])
            current_date = datetime.now().strftime(self.templates.date_format)
            current_time = datetime.now().strftime(self.templates.time_format)

            header = f"{self.templates.lotto_header} – {current_date}"
            game_info = f"⚾ | Game: {teams[0]} @ {teams[1]} ({current_date} {current_time})"
            bet_info = f"🎯 | Bet: {description}"
            if odds != 'TBD':
                bet_info += f" | Odds: {odds}"

            # Add stat summaries for each leg if available
            leg_summaries = []
            for leg in legs:
                summary = self._get_leg_stat_summary(leg, stats_data)
                if summary:
                    leg_summaries.append(summary)
            leg_summaries_section = '\n'.join(leg_summaries) if leg_summaries else ''

            # Add weather/park summary if available
            weather_park_section = self._get_weather_park_summary(stats_data)

            analysis_section = ""
            if analysis:
                analysis_section = f"\n📊 Analysis:\n{analysis}"

            content = f"{header}\n\n{game_info}\n{bet_info}"
            if leg_summaries_section:
                content += f"\n{leg_summaries_section}"
            if weather_park_section:
                content += f"\n{weather_park_section}"
            content += f"{analysis_section}"
            return content
        except Exception as e:
            logger.error(f"Error formatting lotto ticket: {e}")
            return self._get_fallback_format(bet_data, "LOTTO TICKET")
    
    def _get_fallback_format(self, bet_data: Dict[str, Any], pick_type: str) -> str:
        """Get fallback format when template formatting fails."""
        try:
            teams = bet_data.get('teams', ['TBD', 'TBD'])
            description = bet_data.get('description', 'TBD')
            current_date = datetime.now().strftime(self.templates.date_format)
            
            return f"**{pick_type}** – {current_date}\n\n⚾ | Game: {teams[0]} @ {teams[1]}\n🎯 | Bet: {description}\n\n📊 Analysis: Unable to generate analysis at this time."
            
        except Exception as e:
            logger.error(f"Error in fallback format: {e}")
            return f"**{pick_type}** – Error formatting pick. Please check the betting slip manually." 