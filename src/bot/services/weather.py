"""
Weather Service for MLB Stadium Weather Data
Integrates with the weather scraper to get real-time conditions
"""
import asyncio
import os
import sys
import json
from typing import Dict, Optional, List
import logging

# Add weather_scraper to path and set working directory
weather_scraper_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'weather_scraper')
sys.path.insert(0, weather_scraper_path)

# Change to weather_scraper directory for imports
original_cwd = os.getcwd()
try:
    os.chdir(weather_scraper_path)
    from weather_scraper import WeatherScraper
except ImportError:
    logging.warning("Weather scraper not available - weather data will be limited")
    WeatherScraper = None
finally:
    os.chdir(original_cwd)

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for fetching weather data for MLB stadiums"""
    
    def __init__(self):
        self.scraper = None
        self.stadium_mapping = self._load_stadium_mapping()
        self.weather_scraper_path = weather_scraper_path
        
    def _load_stadium_mapping(self) -> Dict[str, str]:
        """Load mapping of team names to stadium locations"""
        return {
            # AL East
            'Baltimore Orioles': 'Oriole Park at Camden Yards',
            'Boston Red Sox': 'Fenway Park', 
            'New York Yankees': 'Yankee Stadium',
            'Tampa Bay Rays': 'Tropicana Field',
            'Toronto Blue Jays': 'Rogers Centre',
            
            # AL Central
            'Chicago White Sox': 'Guaranteed Rate Field',
            'Cleveland Guardians': 'Progressive Field',
            'Detroit Tigers': 'Comerica Park',
            'Kansas City Royals': 'Kauffman Stadium',
            'Minnesota Twins': 'Target Field',
            
            # AL West
            'Houston Astros': 'Minute Maid Park',
            'Los Angeles Angels': 'Angel Stadium',
            'Oakland Athletics': 'Oakland Coliseum',
            'Seattle Mariners': 'T-Mobile Park',
            'Texas Rangers': 'Globe Life Field',
            
            # NL East
            'Atlanta Braves': 'Truist Park',
            'Miami Marlins': 'loanDepot park',
            'New York Mets': 'Citi Field',
            'Philadelphia Phillies': 'Citizens Bank Park',
            'Washington Nationals': 'Nationals Park',
            
            # NL Central
            'Chicago Cubs': 'Wrigley Field',
            'Cincinnati Reds': 'Great American Ball Park',
            'Milwaukee Brewers': 'American Family Field',
            'Pittsburgh Pirates': 'PNC Park',
            'St. Louis Cardinals': 'Busch Stadium',
            
            # NL West
            'Arizona Diamondbacks': 'Chase Field',
            'Colorado Rockies': 'Coors Field',
            'Los Angeles Dodgers': 'Dodger Stadium',
            'San Diego Padres': 'Petco Park',
            'San Francisco Giants': 'Oracle Park'
        }
    
    async def initialize(self):
        """Initialize the weather scraper"""
        if WeatherScraper is None:
            logger.warning("Weather scraper not available")
            return False
            
        try:
            # Change to weather_scraper directory for initialization
            original_cwd = os.getcwd()
            os.chdir(self.weather_scraper_path)
            
            self.scraper = WeatherScraper()
            await self.scraper.initialize()
            
            logger.info("Weather service initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize weather service: {e}")
            return False
        finally:
            os.chdir(original_cwd)
    
    def _get_stadium_for_team(self, team_name: str) -> Optional[str]:
        """Get stadium name for a team"""
        return self.stadium_mapping.get(team_name)
    
    async def get_weather_for_teams(self, teams: List[str]) -> Dict:
        """Get weather data for teams involved in a bet"""
        if not self.scraper:
            return {}
            
        weather_data = {}
        
        # Change to weather_scraper directory for operations
        original_cwd = os.getcwd()
        os.chdir(self.weather_scraper_path)
        
        try:
            for team in teams:
                stadium = self._get_stadium_for_team(team)
                if stadium:
                    try:
                        # Get weather for this stadium
                        weather = await self.scraper.get_weather_for_location(stadium)
                        if weather:
                            weather_data[team] = {
                                'stadium': stadium,
                                'temperature': weather.get('temperature'),
                                'humidity': weather.get('humidity'),
                                'wind_speed': weather.get('wind_speed'),
                                'wind_direction': weather.get('wind_direction'),
                                'conditions': weather.get('conditions'),
                                'pressure': weather.get('pressure')
                            }
                    except Exception as e:
                        logger.error(f"Error getting weather for {team} ({stadium}): {e}")
        finally:
            os.chdir(original_cwd)
        
        return weather_data
    
    async def get_weather_summary(self, teams: List[str]) -> str:
        """Get a formatted weather summary for teams"""
        weather_data = await self.get_weather_for_teams(teams)
        
        if not weather_data:
            return ""
        
        summary_lines = []
        for team, data in weather_data.items():
            temp = data.get('temperature', 'N/A')
            wind = data.get('wind_speed', 'N/A')
            conditions = data.get('conditions', 'N/A')
            
            summary_lines.append(f"**{team}**: {temp}°F, {wind} mph wind, {conditions}")
        
        return "\n".join(summary_lines)
    
    async def close(self):
        """Clean up resources"""
        if self.scraper:
            try:
                await self.scraper.close()
            except Exception as e:
                logger.error(f"Error closing weather service: {e}") 