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
    
    def format_free_play(self, bet_data: Dict[str, Any], stats_data: Optional[Dict[str, Any]] = None, analysis: str = "") -> str:
        """Format a free play pick to match the Discord screenshot style."""
        try:
            teams = bet_data.get('teams', ['TBD', 'TBD'])
            description = bet_data.get('description', 'TBD')
            odds = bet_data.get('odds', 'TBD')
            units = bet_data.get('units', '1')
            current_date = datetime.now().strftime(self.templates.date_format)
            current_time = datetime.now().strftime(self.templates.time_format)

            header = f"# __**🔒 FREE PLAY - {current_date} 🔒**__"
            game_info = f"**⚾ GAME:**  __{teams[0]} @ {teams[1]}__  ({current_date} {current_time})"
            bet_info = f"**🏆 PICK:**  __{description}__  |  **Odds:** __{odds}__"
            analysis_label = "\n👇 **Analysis Below:**\n"

            analysis_section = f"**{analysis}**" if analysis else "No analysis available."

            content = f"{header}\n\n{game_info}\n\n{bet_info}\n{analysis_label}\n{analysis_section}"
            return content
        except Exception as e:
            logger.error(f"Error formatting free play: {e}")
            return self._get_fallback_format(bet_data, "FREE PLAY")
    
    def format_vip_pick(self, bet_data: Dict[str, Any], stats_data: Optional[Dict[str, Any]] = None, analysis: str = "") -> str:
        """Format a VIP pick with multi-leg parlay/SGP support, matching the user's requested style."""
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

                # List each leg
                leg_lines = []
                for leg in legs:
                    player = leg.get('player', '')
                    desc = leg.get('description', '')
                    team = ''
                    if 'teams' in leg and len(leg['teams']) == 2:
                        team = f" [{leg['teams'][0][:3].upper()}]"
                    # Prefer player+desc, fallback to desc
                    if player and desc:
                        leg_line = f"🏆 I {player} {desc}{team}"
                    elif player:
                        leg_line = f"🏆 I {player}{team}"
                    elif desc:
                        leg_line = f"🏆 I {desc}{team}"
                    else:
                        continue
                    leg_lines.append(leg_line)
                legs_section = "\n".join(leg_lines)

                # Parlayed odds
                parlay_odds = f"💰| Parlayed: {odds}" if odds != 'TBD' else ''

                # Unit size
                units_display = f"💵 I Unit Size: {units}"

                # Stats section if available
                stats_section = ""
                if stats_data:
                    stats_summary = stats_data.get('summary', 'Advanced stats available')
                    stats_section = f"📊 I Live Stats: {stats_summary}"

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
                if stats_data:
                    content_parts.extend(["", stats_section])
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
                stats_section = ""
                if stats_data:
                    stats_summary = stats_data.get('summary', 'Advanced stats available')
                    stats_section = f"📊 I Live Stats: {stats_summary}"
                analysis_label = "👇 I Analysis Below:"
                analysis_section = analysis if analysis else "Analysis to be provided."
                content_parts = [header, game_info, "", bet_info, "", units_display]
                if stats_data:
                    content_parts.extend(["", stats_section])
                content_parts.extend(["", analysis_label, "", analysis_section])
                content = "\n".join(content_parts)
                self.vip_play_counter += 1
                return content
        except Exception as e:
            logger.error(f"Error formatting VIP pick: {e}")
            return self._get_fallback_format(bet_data, "VIP PICK")
    
    def format_lotto_ticket(self, bet_data: Dict[str, Any], stats_data: Optional[Dict[str, Any]] = None, analysis: str = "") -> str:
        """Format a lotto ticket pick."""
        try:
            teams = bet_data.get('teams', ['TBD', 'TBD'])
            description = bet_data.get('description', 'TBD')
            odds = bet_data.get('odds', 'TBD')
            units = bet_data.get('units', '1')
            
            current_date = datetime.now().strftime(self.templates.date_format)
            current_time = datetime.now().strftime(self.templates.time_format)
            
            header = f"{self.templates.lotto_header} – {current_date}"
            if units and units != '1':
                header += f"\n💰 **{units} UNITS**"
            
            game_info = f"⚾ | Game: {teams[0]} @ {teams[1]} ({current_date} {current_time})"
            bet_info = f"🎯 | Bet: {description}"
            if odds != 'TBD':
                bet_info += f" | Odds: {odds}"
            
            stats_section = ""
            if stats_data:
                stats_section = f"\n📈 Live Stats: {stats_data.get('summary', 'Data available')}"
            
            analysis_section = ""
            if analysis:
                analysis_section = f"\n📊 Analysis:\n{analysis}"
            
            content = f"{header}\n\n{game_info}\n{bet_info}{stats_section}{analysis_section}"
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