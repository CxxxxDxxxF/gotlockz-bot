"""
MLB Integrated Service - Fast, unified MLB data service using the new scraper
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

from bot.services.mlb_scraper import MLBScraper

logger = logging.getLogger(__name__)


class MLBIntegratedService:
    """Fast, unified service for all MLB data using the new scraper."""
    
    def __init__(self):
        self.scraper = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize the MLB scraper."""
        try:
            self.scraper = MLBScraper()
            success = await self.scraper.initialize()
            if success:
                self.initialized = True
                logger.info("MLB Integrated Service initialized successfully")
            else:
                logger.error("Failed to initialize MLB scraper")
            return success
        except Exception as e:
            logger.error(f"Error initializing MLB Integrated Service: {e}")
            return False
    
    async def get_comprehensive_game_data(self, bet_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get comprehensive game data for betting analysis using the fast scraper."""
        try:
            if not self.initialized or not self.scraper:
                logger.warning("Service not initialized, attempting to initialize")
                await self.initialize()
                if not self.initialized:
                    return None
            
            teams = bet_data.get('teams', [])
            if len(teams) < 2:
                return None
            
            # Use the fast scraper to get all data
            game_data = await self.scraper.get_game_data(teams[0], teams[1])
            
            if 'error' in game_data:
                logger.error(f"Error getting game data: {game_data['error']}")
                return None
            
            # Transform the data to match the expected format
            transformed_data = self._transform_game_data(game_data, bet_data)
            
            return transformed_data
            
        except Exception as e:
            logger.error(f"Error getting comprehensive game data: {e}")
            return None
    
    def _transform_game_data(self, game_data: Dict[str, Any], bet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform scraper data to match the expected format for the bot."""
        try:
            teams = bet_data.get('teams', [])
            team1, team2 = teams[0], teams[1]
            
            # Extract team data
            team1_data = game_data.get('teams', {}).get(team1, {})
            team2_data = game_data.get('teams', {}).get(team2, {})
            
            # Transform to expected format
            transformed = {
                'team1': {
                    'basic_stats': team1_data.get('stats', {}),
                    'weather': team1_data.get('weather', {}),
                    'info': team1_data.get('info', {}),
                    'advanced_stats': self._extract_advanced_stats(team1_data)
                },
                'team2': {
                    'basic_stats': team2_data.get('stats', {}),
                    'weather': team2_data.get('weather', {}),
                    'info': team2_data.get('info', {}),
                    'advanced_stats': self._extract_advanced_stats(team2_data)
                },
                'game_info': {
                    'today_game': game_data.get('today_game'),
                    'live_scores': game_data.get('live_scores', []),
                    'fetch_time': game_data.get('fetch_time', 0)
                },
                'weather': {
                    'data': {
                        team1: team1_data.get('weather', {}),
                        team2: team2_data.get('weather', {})
                    },
                    'summary': self._generate_weather_summary(team1_data.get('weather', {}), team2_data.get('weather', {})),
                    'available': bool(team1_data.get('weather') or team2_data.get('weather'))
                },
                'park_factors': self._get_park_factors(team1, team2),
                'statcast': {
                    'available': False,  # Will be added later if needed
                    'data': {}
                },
                'summary': game_data.get('summary', f"Data loaded for {team1} vs {team2}"),
                'performance_metrics': {
                    'fetch_time': game_data.get('fetch_time', 0),
                    'data_sources': ['mlb_api', 'weather_api'],
                    'cache_status': 'active'
                }
            }
            
            return transformed
            
        except Exception as e:
            logger.error(f"Error transforming game data: {e}")
            return {}
    
    def _extract_advanced_stats(self, team_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract advanced stats from team data."""
        try:
            stats = team_data.get('stats', {})
            
            # Calculate advanced metrics
            advanced = {
                'win_pct': stats.get('win_pct', 0.0),
                'run_diff': stats.get('run_diff', 0),
                'games_played': stats.get('games_played', 0),
                'avg': stats.get('avg', 0.0),
                'obp': stats.get('obp', 0.0),
                'slg': stats.get('slg', 0.0),
                'era': stats.get('era', 0.0),
                'recent_form': self._calculate_recent_form(stats),
                'home_away_splits': self._get_home_away_splits(stats)
            }
            
            return advanced
            
        except Exception as e:
            logger.error(f"Error extracting advanced stats: {e}")
            return {}
    
    def _calculate_recent_form(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate recent form based on available stats."""
        try:
            # This would ideally come from recent games data
            # For now, we'll use basic stats as a proxy
            win_pct = stats.get('win_pct', 0.0)
            
            if win_pct >= 0.600:
                form = "Hot"
            elif win_pct >= 0.500:
                form = "Average"
            else:
                form = "Cold"
            
            return {
                'form': form,
                'win_pct': win_pct,
                'games_analyzed': stats.get('games_played', 0)
            }
            
        except Exception as e:
            logger.error(f"Error calculating recent form: {e}")
            return {'form': 'Unknown', 'win_pct': 0.0, 'games_analyzed': 0}
    
    def _get_home_away_splits(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Get home/away performance splits."""
        try:
            # This would ideally come from home/away specific data
            # For now, we'll use neutral splits
            return {
                'home': {
                    'win_pct': stats.get('win_pct', 0.0),
                    'runs_scored': stats.get('runs_scored', 0),
                    'runs_allowed': stats.get('runs_allowed', 0)
                },
                'away': {
                    'win_pct': stats.get('win_pct', 0.0),
                    'runs_scored': stats.get('runs_scored', 0),
                    'runs_allowed': stats.get('runs_allowed', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting home/away splits: {e}")
            return {'home': {}, 'away': {}}
    
    def _generate_weather_summary(self, weather1: Dict[str, Any], weather2: Dict[str, Any]) -> str:
        """Generate a weather summary for both teams."""
        try:
            if not weather1 and not weather2:
                return "Weather data unavailable"
            
            summaries = []
            
            if weather1:
                temp1 = weather1.get('temperature', 'N/A')
                wind1 = weather1.get('wind_speed', 'N/A')
                conditions1 = weather1.get('conditions', 'N/A')
                summaries.append(f"Team 1: {temp1}°F, {wind1} mph wind, {conditions1}")
            
            if weather2:
                temp2 = weather2.get('temperature', 'N/A')
                wind2 = weather2.get('wind_speed', 'N/A')
                conditions2 = weather2.get('conditions', 'N/A')
                summaries.append(f"Team 2: {temp2}°F, {wind2} mph wind, {conditions2}")
            
            return " | ".join(summaries) if summaries else "Weather data unavailable"
            
        except Exception as e:
            logger.error(f"Error generating weather summary: {e}")
            return "Weather data unavailable"
    
    def _get_park_factors(self, team1: str, team2: str) -> Dict[str, Any]:
        """Get park factors for the teams."""
        try:
            # Use the same park factors logic as before
            park_factors = {
                'runs': 1.0,  # Neutral park
                'hr': 1.0,    # Neutral HR park
                'k': 1.0,     # Neutral K park
                'bb': 1.0     # Neutral BB park
            }
            
            # Adjust based on known park factors
            if any(team in team1 for team in ['Colorado', 'Rockies']):
                park_factors = {'runs': 1.15, 'hr': 1.25, 'k': 0.95, 'bb': 1.05}
            elif any(team in team1 for team in ['San Francisco', 'Giants']):
                park_factors = {'runs': 0.85, 'hr': 0.75, 'k': 1.05, 'bb': 0.95}
            elif any(team in team1 for team in ['Boston', 'Red Sox']):
                park_factors = {'runs': 1.05, 'hr': 1.15, 'k': 0.98, 'bb': 1.02}
            elif any(team in team1 for team in ['New York', 'Yankees']):
                park_factors = {'runs': 1.08, 'hr': 1.20, 'k': 0.97, 'bb': 1.03}
            elif any(team in team1 for team in ['Los Angeles', 'Dodgers']):
                park_factors = {'runs': 0.95, 'hr': 0.90, 'k': 1.02, 'bb': 0.98}
            elif any(team in team1 for team in ['Houston', 'Astros']):
                park_factors = {'runs': 1.02, 'hr': 1.10, 'k': 0.99, 'bb': 1.01}
            
            return park_factors
            
        except Exception as e:
            logger.error(f"Error getting park factors: {e}")
            return {'runs': 1.0, 'hr': 1.0, 'k': 1.0, 'bb': 1.0}
    
    async def get_live_scores(self) -> List[Dict[str, Any]]:
        """Get live game scores."""
        try:
            if not self.initialized or not self.scraper:
                return []
            
            # This would need to be added to the MLBScraper
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Error getting live scores: {e}")
            return []
    
    async def close(self):
        """Close the scraper session."""
        if self.scraper:
            try:
                await self.scraper.close()
            except Exception as e:
                logger.error(f"Error closing MLB Integrated Service: {e}") 