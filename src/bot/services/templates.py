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
        """Format a free play pick."""
        try:
            teams = bet_data.get('teams', ['TBD', 'TBD'])
            description = bet_data.get('description', 'TBD')
            odds = bet_data.get('odds', 'TBD')
            units = bet_data.get('units', '1')
            
            current_date = datetime.now().strftime(self.templates.date_format)
            current_time = datetime.now().strftime(self.templates.time_format)
            
            header = f"{self.templates.free_play_header} – {current_date}"
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
            logger.error(f"Error formatting free play: {e}")
            return self._get_fallback_format(bet_data, "FREE PLAY")
    
    def format_vip_pick(self, bet_data: Dict[str, Any], stats_data: Optional[Dict[str, Any]] = None, analysis: str = "") -> str:
        """Format a VIP pick."""
        try:
            teams = bet_data.get('teams', ['TBD', 'TBD'])
            description = bet_data.get('description', 'TBD')
            odds = bet_data.get('odds', 'TBD')
            units = bet_data.get('units', '1')
            
            current_date = datetime.now().strftime(self.templates.date_format)
            current_time = datetime.now().strftime(self.templates.time_format)
            
            header = f"{self.templates.vip_header} – {current_date}"
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