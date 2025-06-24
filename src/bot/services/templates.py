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
        """Format a VIP pick with premium styling."""
        try:
            teams = bet_data.get('teams', ['TBD', 'TBD'])
            description = bet_data.get('description', 'TBD')
            odds = bet_data.get('odds', 'TBD')
            units = bet_data.get('units', '1')
            
            current_date = datetime.now().strftime(self.templates.date_format)
            current_time = datetime.now().strftime(self.templates.time_format)
            
            # Premium VIP header with crown and diamond
            header = f"# __**{self.templates.vip_emoji} VIP PICK - {current_date} {self.templates.vip_diamond}**__"
            
            # Units display if specified
            units_display = ""
            if units and units != '1':
                units_display = f"\n{self.templates.vip_units_emoji} **{units} UNITS**"
            
            # Game information with premium formatting
            game_info = f"**{self.templates.vip_matchup_emoji} MATCHUP:**  __{teams[0]} @ {teams[1]}__  ({current_date} {current_time})"
            
            # Bet information with odds
            bet_info = f"**{self.templates.vip_selection_emoji} SELECTION:**  __{description}__"
            if odds != 'TBD':
                bet_info += f"  |  **Odds:** __{odds}__"
            
            # Stats section if available
            stats_section = ""
            if stats_data:
                stats_summary = stats_data.get('summary', 'Advanced stats available')
                stats_section = f"\n\n{self.templates.vip_stats_emoji} **LIVE STATS:**\n{stats_summary}"
            
            # Analysis section with premium formatting
            analysis_section = ""
            if analysis:
                analysis_section = f"\n\n{self.templates.vip_analysis_emoji} **VIP ANALYSIS:**\n{analysis}"
            
            # Combine all sections
            content = f"{header}{units_display}\n\n{game_info}\n\n{bet_info}{stats_section}{analysis_section}"
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
            
            # Premium VIP header with crown and diamond
            header = f"# __**{self.templates.vip_emoji} PREMIUM VIP PICK - {current_date} {self.templates.vip_diamond}**__"
            
            # Confidence level indicator
            confidence_emoji = "🟢" if confidence.upper() == "HIGH" else "🟡" if confidence.upper() == "MEDIUM" else "🔴"
            confidence_display = f"\n{confidence_emoji} **CONFIDENCE:** {confidence.upper()}"
            
            # Units display if specified
            units_display = ""
            if units and units != '1':
                units_display = f"\n{self.templates.vip_units_emoji} **{units} UNITS**"
            
            # Track record if provided
            track_display = ""
            if track_record:
                track_display = f"\n📈 **TRACK RECORD:** {track_record}"
            
            # Game information with premium formatting
            game_info = f"**{self.templates.vip_matchup_emoji} MATCHUP:**  __{teams[0]} @ {teams[1]}__  ({current_date} {current_time})"
            
            # Bet information with odds
            bet_info = f"**{self.templates.vip_selection_emoji} SELECTION:**  __{description}__"
            if odds != 'TBD':
                bet_info += f"  |  **Odds:** __{odds}__"
            
            # Stats section if available
            stats_section = ""
            if stats_data:
                stats_summary = stats_data.get('summary', 'Advanced stats available')
                stats_section = f"\n\n{self.templates.vip_stats_emoji} **LIVE STATS:**\n{stats_summary}"
            
            # Analysis section with premium formatting
            analysis_section = ""
            if analysis:
                analysis_section = f"\n\n{self.templates.vip_analysis_emoji} **VIP ANALYSIS:**\n{analysis}"
            
            # Combine all sections
            content = f"{header}{confidence_display}{units_display}{track_display}\n\n{game_info}\n\n{bet_info}{stats_section}{analysis_section}"
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