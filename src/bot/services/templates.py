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
        """Format a VIP pick with the exact style from the examples."""
        try:
            teams = bet_data.get('teams', ['TBD', 'TBD'])
            description = bet_data.get('description', 'TBD')
            odds = bet_data.get('odds', 'TBD')
            units = bet_data.get('units', '1')
            
            current_date = datetime.now().strftime(self.templates.date_format)
            current_time = datetime.now().strftime(self.templates.time_format)
            
            # VIP header with play number (you can customize this)
            header = f"🔒 I VIP PLAY # {self.vip_play_counter} 🏆 - {current_date}"
            
            # Game information
            game_info = f"⚾️ I Game: {teams[0]} @ {teams[1]}  ({current_date} {current_time})"
            
            # Bet selection
            bet_info = f"🏆 I {description}"
            if odds != 'TBD':
                bet_info += f" ({odds})"
            
            # Unit size
            units_display = f"💵 I Unit Size: {units}"
            
            # Stats section if available
            stats_section = ""
            if stats_data:
                stats_summary = stats_data.get('summary', 'Advanced stats available')
                stats_section = f"📊 I Live Stats: {stats_summary}"
            
            # Analysis section
            analysis_label = "👇 I Analysis Below:"
            
            # Analysis content
            analysis_section = analysis if analysis else "Analysis to be provided."
            
            # Combine all sections
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
    
    def format_premium_vip_pick(self, bet_data: Dict[str, Any], stats_data: Optional[Dict[str, Any]] = None, analysis: str = "", confidence: str = "HIGH", track_record: str = "") -> str:
        """Format a premium VIP pick with confidence level and track record."""
        try:
            teams = bet_data.get('teams', ['TBD', 'TBD'])
            description = bet_data.get('description', 'TBD')
            odds = bet_data.get('odds', 'TBD')
            units = bet_data.get('units', '1')
            
            current_date = datetime.now().strftime(self.templates.date_format)
            current_time = datetime.now().strftime(self.templates.time_format)
            
            # Premium VIP header with play number
            header = f"🔒 I VIP PLAY # {self.vip_play_counter} 🏆 - {current_date}"
            
            # Confidence level indicator
            confidence_emoji = "🟢" if confidence.upper() == "HIGH" else "🟡" if confidence.upper() == "MEDIUM" else "🔴"
            confidence_display = f"{confidence_emoji} I Confidence: {confidence.upper()}"
            
            # Track record if provided
            track_display = ""
            if track_record:
                track_display = f"📈 I Track Record: {track_record}"
            
            # Game information
            game_info = f"⚾️ I Game: {teams[0]} @ {teams[1]}  ({current_date} {current_time})"
            
            # Bet selection
            bet_info = f"🏆 I {description}"
            if odds != 'TBD':
                bet_info += f" ({odds})"
            
            # Unit size
            units_display = f"💵 I Unit Size: {units}"
            
            # Stats section if available
            stats_section = ""
            if stats_data:
                stats_summary = stats_data.get('summary', 'Advanced stats available')
                stats_section = f"📊 I Live Stats: {stats_summary}"
            
            # Analysis section
            analysis_label = "👇 I Analysis Below:"
            
            # Analysis content
            analysis_section = analysis if analysis else "Analysis to be provided."
            
            # Combine all sections
            content_parts = [header]
            if track_record:
                content_parts.append(track_display)
            content_parts.extend([
                confidence_display,
                game_info,
                "",
                bet_info,
                "",
                units_display
            ])
            
            if stats_data:
                content_parts.extend(["", stats_section])
            
            content_parts.extend(["", analysis_label, "", analysis_section])
            
            content = "\n".join(content_parts)
            self.vip_play_counter += 1
            return content
            
        except Exception as e:
            logger.error(f"Error formatting premium VIP pick: {e}")
            return self._get_fallback_format(bet_data, "PREMIUM VIP PICK")
    
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