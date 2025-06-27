"""
Improved MLB Scraper - Fast, reliable data collection for MLB games
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp

from bot.utils.performance_limiter import rate_limit, safe_operation

logger = logging.getLogger(__name__)


class MLBScraper:
    """High-performance MLB data scraper"""

    def __init__(self):
        self.session = None
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        self.timeout = aiohttp.ClientTimeout(total=10)

        # MLB API endpoints
        self.mlb_base = "https://statsapi.mlb.com/api/v1"
        self.weather_api = "https://api.openweathermap.org/data/2.5/weather"

        # Team mappings
        self.team_mapping = {
            "Los Angeles Angels": {"id": 108, "abbr": "LAA", "city": "Anaheim"},
            "Oakland Athletics": {"id": 133, "abbr": "OAK", "city": "Oakland"},
            "New York Yankees": {"id": 147, "abbr": "NYY", "city": "New York"},
            "Boston Red Sox": {"id": 111, "abbr": "BOS", "city": "Boston"},
            "Houston Astros": {"id": 117, "abbr": "HOU", "city": "Houston"},
            "Los Angeles Dodgers": {"id": 119, "abbr": "LAD", "city": "Los Angeles"},
            "San Francisco Giants": {"id": 137, "abbr": "SF", "city": "San Francisco"},
            "Colorado Rockies": {"id": 115, "abbr": "COL", "city": "Denver"},
            "Chicago Cubs": {"id": 112, "abbr": "CHC", "city": "Chicago"},
            "Chicago White Sox": {"id": 145, "abbr": "CWS", "city": "Chicago"},
            "Cleveland Guardians": {"id": 114, "abbr": "CLE", "city": "Cleveland"},
            "Detroit Tigers": {"id": 116, "abbr": "DET", "city": "Detroit"},
            "Kansas City Royals": {"id": 118, "abbr": "KC", "city": "Kansas City"},
            "Minnesota Twins": {"id": 142, "abbr": "MIN", "city": "Minneapolis"},
            "Baltimore Orioles": {"id": 110, "abbr": "BAL", "city": "Baltimore"},
            "Tampa Bay Rays": {"id": 139, "abbr": "TB", "city": "Tampa Bay"},
            "Toronto Blue Jays": {"id": 141, "abbr": "TOR", "city": "Toronto"},
            "Atlanta Braves": {"id": 144, "abbr": "ATL", "city": "Atlanta"},
            "Miami Marlins": {"id": 146, "abbr": "MIA", "city": "Miami"},
            "New York Mets": {"id": 121, "abbr": "NYM", "city": "New York"},
            "Philadelphia Phillies": {"id": 143, "abbr": "PHI", "city": "Philadelphia"},
            "Washington Nationals": {"id": 120, "abbr": "WSH", "city": "Washington"},
            "Arizona Diamondbacks": {"id": 109, "abbr": "ARI", "city": "Phoenix"},
            "San Diego Padres": {"id": 135, "abbr": "SD", "city": "San Diego"},
            "Seattle Mariners": {"id": 136, "abbr": "SEA", "city": "Seattle"},
            "Texas Rangers": {"id": 140, "abbr": "TEX", "city": "Arlington"},
            "Cincinnati Reds": {"id": 113, "abbr": "CIN", "city": "Cincinnati"},
            "Milwaukee Brewers": {"id": 158, "abbr": "MIL", "city": "Milwaukee"},
            "Pittsburgh Pirates": {"id": 134, "abbr": "PIT", "city": "Pittsburgh"},
            "St. Louis Cardinals": {"id": 138, "abbr": "STL", "city": "St. Louis"},
        }

    async def initialize(self):
        """Initialize the scraper with session."""
        try:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
            logger.info("MLB Scraper initialized")
        except Exception as e:
            logger.error(f"Error initializing MLB Scraper: {e}")

    async def close(self):
        """Close the scraper session."""
        if self.session and not self.session.closed:
            await self.session.close()

    @rate_limit(max_requests=5)
    async def get_game_data(self, team1: str, team2: str) -> Dict[str, Any]:
        """Get comprehensive game data for two teams"""
        try:
            start_time = time.time()

            # Get team info
            team1_info = self.team_mapping.get(team1)
            team2_info = self.team_mapping.get(team2)

            if not team1_info or not team2_info:
                return {"error": "Team not found"}

            # Fetch data concurrently with performance limiting
            tasks = [
                safe_operation(self._get_team_stats, team1_info["id"]),
                safe_operation(self._get_team_stats, team2_info["id"]),
                safe_operation(self._get_weather_data, team1_info["city"]),
                safe_operation(self._get_weather_data, team2_info["city"]),
                safe_operation(self._get_live_scores),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            team1_stats = results[0] if not isinstance(results[0], Exception) else {}
            team2_stats = results[1] if not isinstance(results[1], Exception) else {}
            team1_weather = results[2] if not isinstance(results[2], Exception) else {}
            team2_weather = results[3] if not isinstance(results[3], Exception) else {}
            live_scores = results[4] if not isinstance(results[4], Exception) and isinstance(results[4], list) else []

            # Check if teams are playing today
            today_game = self._find_today_game(live_scores, team1_info["abbr"], team2_info["abbr"])

            total_time = time.time() - start_time
            logger.info(f"Game data fetched in {total_time:.2f}s")

            return {
                "team1": {
                    "name": team1,
                    "stats": team1_stats,
                    "weather": team1_weather
                },
                "team2": {
                    "name": team2,
                    "stats": team2_stats,
                    "weather": team2_weather
                },
                "live_game": today_game,
                "fetch_time": total_time
            }

        except Exception as e:
            logger.error(f"Error getting game data: {e}")
            return {"error": f"Failed to get game data: {str(e)}"}

    @rate_limit(max_requests=3)
    async def _get_team_stats(self, team_id: int) -> Dict[str, Any]:
        """Get team statistics from MLB API."""
        cache_key = f"team_stats_{team_id}"
        
        # Check cache first
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_timeout:
                return data

        try:
            url = f"{self.mlb_base}/teams/{team_id}/stats"
            params = {"season": datetime.now().year, "group": "hitting,pitching"}

            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    return {}

                data = await response.json()
                stats = self._parse_team_stats(data)
                
                # Cache the result
                self.cache[cache_key] = (time.time(), stats)
                return stats

        except Exception as e:
            logger.error(f"Error getting team stats for {team_id}: {e}")
            return {}

    @rate_limit(max_requests=2)
    async def _get_weather_data(self, city: str) -> Dict[str, Any]:
        """Get weather data for a city."""
        cache_key = f"weather_{city}"
        
        # Check cache first
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if time.time() - cache_time < 300:  # 5 minute cache for weather
                return data

        try:
            api_key = os.getenv("OPENWEATHER_API_KEY")
            if not api_key:
                return {"error": "No weather API key"}

            url = self.weather_api
            params = {
                "q": city,
                "appid": api_key,
                "units": "imperial"
            }

            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    return {}

                data = await response.json()
                weather = {
                    "temperature": data.get("main", {}).get("temp"),
                    "humidity": data.get("main", {}).get("humidity"),
                    "wind_speed": data.get("wind", {}).get("speed"),
                    "description": data.get("weather", [{}])[0].get("description"),
                    "city": city
                }
                
                # Cache the result
                self.cache[cache_key] = (time.time(), weather)
                return weather

        except Exception as e:
            logger.error(f"Error getting weather for {city}: {e}")
            return {}

    @rate_limit(max_requests=2)
    async def _get_live_scores(self) -> List[Dict[str, Any]]:
        """Get live game scores."""
        cache_key = "live_scores"
        
        # Check cache first (shorter cache for live data)
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if time.time() - cache_time < 60:  # 1 minute cache for live data
                return data

        try:
            url = f"{self.mlb_base}/schedule"
            params = {
                "sportId": 1,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "fields": "dates,games,gamePk,teams,away,home,team,abbreviation,score,status"
            }

            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    return []

                data = await response.json()
                games = []
                
                for date_data in data.get("dates", []):
                    for game in date_data.get("games", []):
                        away_team = game.get("teams", {}).get("away", {})
                        home_team = game.get("teams", {}).get("home", {})
                        
                        games.append({
                            "game_id": game.get("gamePk"),
                            "away_team": away_team.get("team", {}).get("abbreviation"),
                            "home_team": home_team.get("team", {}).get("abbreviation"),
                            "away_score": away_team.get("score"),
                            "home_score": home_team.get("score"),
                            "status": game.get("status", {}).get("detailedState")
                        })
                
                # Cache the result
                self.cache[cache_key] = (time.time(), games)
                return games

        except Exception as e:
            logger.error(f"Error getting live scores: {e}")
            return []

    def _find_today_game(self, live_scores: List[Dict[str, Any]], team1_abbr: str, team2_abbr: str) -> Optional[Dict[str, Any]]:
        """Find if the two teams are playing today."""
        for game in live_scores:
            away = game.get("away_team")
            home = game.get("home_team")
            
            if (away == team1_abbr and home == team2_abbr) or (away == team2_abbr and home == team1_abbr):
                return game
        return None

    def _parse_team_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse team statistics from MLB API response."""
        try:
            stats = data.get("stats", [])
            result = {}
            
            for stat_group in stats:
                group_name = stat_group.get("group", {}).get("displayName", "")
                splits = stat_group.get("splits", [])
                
                if splits:
                    stat_data = splits[0].get("stat", {})
                    if group_name == "hitting":
                        result.update({
                            "batting_avg": stat_data.get("avg", "N/A"),
                            "runs": stat_data.get("runs", "N/A"),
                            "hits": stat_data.get("hits", "N/A"),
                            "home_runs": stat_data.get("homeRuns", "N/A"),
                            "rbis": stat_data.get("rbi", "N/A")
                        })
                    elif group_name == "pitching":
                        result.update({
                            "era": stat_data.get("era", "N/A"),
                            "wins": stat_data.get("wins", "N/A"),
                            "losses": stat_data.get("losses", "N/A"),
                            "saves": stat_data.get("saves", "N/A"),
                            "strikeouts": stat_data.get("strikeOuts", "N/A")
                        })
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing team stats: {e}")
            return {}
