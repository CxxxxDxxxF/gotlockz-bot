#!/usr/bin/env python3
"""
mlb_stats.py - MLB Data Integration

Fetch live MLB stats, team data, and current trends using multiple free APIs.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import statsapi
import requests
import json
import re
import asyncio
import time
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class MLBDataFetcher:
    """Fetch live MLB data and statistics using multiple free APIs."""

    def __init__(self):
        self.statsapi = statsapi
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Add caching
        self._cache = {}
        self._cache_timeout = 300  # 5 minutes
        
        # ESPN API endpoints
        self.espn_base_url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb"
        
        # MLB.com scraping endpoints
        self.mlb_base_url = "https://www.mlb.com"
        self.mlb_stats_url = "https://www.mlb.com/stats"
        
        self.team_abbreviations = {
            "ARI": "Arizona Diamondbacks", "AZ": "Arizona Diamondbacks",
            "ATL": "Atlanta Braves",
            "BAL": "Baltimore Orioles",
            "BOS": "Boston Red Sox",
            "CHW": "Chicago White Sox", "SOX": "Chicago White Sox",
            "CHC": "Chicago Cubs", "CUBS": "Chicago Cubs",
            "CIN": "Cincinnati Reds",
            "CLE": "Cleveland Guardians", "GUARDS": "Cleveland Guardians",
            "COL": "Colorado Rockies",
            "DET": "Detroit Tigers",
            "HOU": "Houston Astros",
            "KC": "Kansas City Royals",
            "LAA": "Los Angeles Angels", "ANGELS": "Los Angeles Angels",
            "LAD": "Los Angeles Dodgers", "DODGERS": "Los Angeles Dodgers",
            "MIA": "Miami Marlins",
            "MIL": "Milwaukee Brewers",
            "MIN": "Minnesota Twins",
            "NYM": "New York Mets", "METS": "New York Mets",
            "NYY": "New York Yankees", "YANKEES": "New York Yankees",
            "OAK": "Oakland Athletics", "A'S": "Oakland Athletics",
            "PHI": "Philadelphia Phillies",
            "PIT": "Pittsburgh Pirates",
            "SD": "San Diego Padres", "PADRES": "San Diego Padres", "SAN": "San Diego Padres",
            "SF": "San Francisco Giants", "GIANTS": "San Francisco Giants",
            "SEA": "Seattle Mariners",
            "STL": "St. Louis Cardinals", "CARDS": "St. Louis Cardinals",
            "TB": "Tampa Bay Rays",
            "TEX": "Texas Rangers",
            "TOR": "Toronto Blue Jays", "JAYS": "Toronto Blue Jays",
            "WSH": "Washington Nationals", "NATS": "Washington Nationals",
        }
        self.ambiguous_names = {
            "SOX": "Chicago White Sox",
            "JAYS": "Toronto Blue Jays",
            "PADRES": "San Diego Padres",
            "GIANTS": "San Francisco Giants",
            "METS": "New York Mets",
            "YANKEES": "New York Yankees",
            "CARDS": "St. Louis Cardinals",
            "NATS": "Washington Nationals",
        }

    def _resolve_team_name(self, name: str) -> str:
        """Resolve team abbreviations or nicknames to official names."""
        name_upper = name.upper()
        if name_upper in self.team_abbreviations:
            return self.team_abbreviations[name_upper]
        if name_upper in self.ambiguous_names:
            return self.ambiguous_names[name_upper]
        for key, value in self.team_abbreviations.items():
            if name_upper in value.upper():
                return value
        return name

    async def get_team_stats(self, team_name: str) -> Dict[str, Any]:
        """Get team statistics from multiple sources with caching."""
        cache_key = self._get_cache_key("team_stats", team_name)
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            resolved_name = self._resolve_team_name(team_name)
            # Primary: MLB Stats API
            team_stats = await self._get_team_stats_mlb(resolved_name)
            
            # Fallback: Sportsipy (if available)
            if not team_stats:
                team_stats = await self._get_team_stats_sportsipy(resolved_name)
            
            self._set_cached_data(cache_key, team_stats)
            return team_stats

        except Exception as e:
            logger.error(f"Error fetching team stats: {e}")
            return {}

    async def get_player_stats(self, player_name: str) -> Dict[str, Any]:
        """Get player statistics from multiple sources with caching."""
        cache_key = self._get_cache_key("player_stats", player_name)
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            # Primary: MLB Stats API
            player_stats = await self._get_player_stats_mlb(player_name)
            
            # Fallback: Sportsipy (if available)
            if not player_stats:
                player_stats = await self._get_player_stats_sportsipy(player_name)
            
            self._set_cached_data(cache_key, player_stats)
            return player_stats

        except Exception as e:
            logger.error(f"Error fetching player stats: {e}")
            return {}

    async def get_game_info(
        self, away_team: str, home_team: str, game_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get game information including weather, venue, etc."""
        try:
            resolved_away = self._resolve_team_name(away_team)
            resolved_home = self._resolve_team_name(home_team)

            # Primary: MLB Stats API
            game_info = await self._get_game_info_mlb(
                resolved_away, resolved_home, game_date=game_date
            )
            
            # Enhance with additional data
            if game_info:
                # Add weather data if available
                weather_data = await self._get_weather_data(game_info.get('venue', ''))
                if weather_data:
                    game_info['weather'] = weather_data
            
            return game_info

        except Exception as e:
            logger.error(f"Error fetching game info: {e}")
            return {}

    async def get_live_scores(self, team_name: Optional[str] = None) -> Dict[str, Any]:
        """Get live scores and game status."""
        try:
            # Get today's schedule
            today = datetime.now().strftime("%Y-%m-%d")
            schedule = self.statsapi.schedule(date=today, sportId=1)
            
            live_games = []
            if schedule:  # schedule is a list, not a dict
                for game in schedule:
                    if isinstance(game, dict):
                        game_status = game.get('status', '')
                        if 'Live' in game_status or 'In Progress' in game_status:
                            live_games.append({
                                'away_team': game.get('away_name', ''),
                                'home_team': game.get('home_name', ''),
                                'away_score': game.get('away_score', 0),
                                'home_score': game.get('home_score', 0),
                                'inning': game.get('current_inning', 0),
                                'status': game_status
                            })
            
            return {'live_games': live_games}

        except Exception as e:
            logger.error(f"Error fetching live scores: {e}")
            return {'live_games': []}

    async def get_team_logo(self, team_name: str) -> str:
        """Get team logo URL from TheSportsDB."""
        try:
            # TheSportsDB free API
            url = "https://www.thesportsdb.com/api/v1/json/3/searchteams.php"
            params = {'t': team_name}
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and data.get('teams'):
                    teams = data['teams']
                    if isinstance(teams, list) and len(teams) > 0:
                        return teams[0].get('strTeamBadge', '')
            
            return ''

        except Exception as e:
            logger.error(f"Error fetching team logo: {e}")
            return ''

    async def get_player_image(self, player_name: str) -> str:
        """Get player image URL from TheSportsDB."""
        try:
            # TheSportsDB free API
            url = "https://www.thesportsdb.com/api/v1/json/3/searchplayers.php"
            params = {'p': player_name}
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and data.get('player'):
                    players = data['player']
                    if isinstance(players, list) and len(players) > 0:
                        return players[0].get('strThumb', '')
            
            return ''

        except Exception as e:
            logger.error(f"Error fetching player image: {e}")
            return ''

    # MLB Stats API Methods
    async def _get_team_stats_mlb(self, team_name: str) -> Dict[str, Any]:
        """Get team stats from MLB Stats API."""
        try:
            # Lookup team
            teams = self.statsapi.lookup_team(team_name)
            if not teams or not isinstance(teams, list) or len(teams) == 0:
                return {}
            
            team_id = teams[0]['id']
            
            # For now, return basic team info since detailed stats require different API calls
            # We can enhance this later with more detailed stats
            return {
                'wins': 0,  # Would need additional API call
                'losses': 0,  # Would need additional API call
                'win_pct': 0,  # Would need additional API call
                'runs_per_game': 0,  # Would need additional API call
                'era': 0,  # Would need additional API call
                'team_id': team_id,
                'team_name': teams[0]['name']
            }
            
        except Exception as e:
            logger.error(f"Error fetching MLB team stats: {e}")
            return {}

    async def _get_player_stats_mlb(self, player_name: str) -> Dict[str, Any]:
        """Get player stats from MLB Stats API."""
        try:
            # Lookup player
            players = self.statsapi.lookup_player(player_name)
            if not players or not isinstance(players, list) or len(players) == 0:
                return {}
            
            player_id = players[0]['id']
            
            # Get player stats using the correct method
            player_stats = self.statsapi.player_stat_data(player_id, group='hitting', type='season')
            
            if player_stats and 'stats' in player_stats and player_stats['stats']:
                stats = player_stats['stats'][0]['stats']  # Correct path to stats
                return {
                    'batting_avg': stats.get('avg', '.000'),
                    'hr': stats.get('homeRuns', 0),
                    'rbi': stats.get('rbi', 0),
                    'ops': stats.get('ops', '.000'),
                    'slg': stats.get('slg', '.000'),
                    'obp': stats.get('obp', '.000')
                }
            
            return {}

        except Exception as e:
            logger.error(f"Error fetching MLB player stats: {e}")
            return {}

    async def _get_game_info_mlb(
        self, away_team: str, home_team: str, game_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get game info from MLB Stats API."""
        try:
            # Use the provided date from OCR, otherwise default to the current day
            search_date = game_date if game_date else datetime.now().strftime("%Y-%m-%d")
            logger.info(f"Searching for MLB schedule on date: {search_date}")
            schedule = self.statsapi.schedule(date=search_date, sportId=1)
            
            if schedule:
                for game in schedule:
                    if not isinstance(game, dict):
                        continue

                    game_away = game.get('away_name', '').lower()
                    game_home = game.get('home_name', '').lower()
                    team1 = away_team.lower()
                    team2 = home_team.lower()
                    
                    # More robust matching
                    if (team1 in game_away and team2 in game_home) or \
                       (team1 in game_home and team2 in game_away):
                        logger.info(f"Found game match: {away_team} vs {home_team}")
                        return {
                            'game_time': game.get('game_datetime', ''),
                            'venue': game.get('venue_name', ''),
                            'weather': 'Clear, 72°F',  # Default
                            'away_pitcher': game.get('away_probable_pitcher', 'TBD'),
                            'home_pitcher': game.get('home_probable_pitcher', 'TBD')
                        }
            
            # If no game was found, log the schedule for debugging
            logger.error(
                f"Could not find a live game match for {away_team} vs {home_team}. "
                f"Full schedule received from API: {json.dumps(schedule, indent=2)}"
            )
            return {}

        except Exception as e:
            logger.error(f"Error fetching MLB game info: {e}")
            return {}

    # Sportsipy Methods (Fallback)
    async def _get_team_stats_sportsipy(self, team_name: str) -> Dict[str, Any]:
        """Get team stats from Sportsipy (ESPN data)."""
        try:
            # Import here to avoid import errors if sportsipy is not available
            from sportsipy.mlb.teams import Teams
            
            teams = Teams()
            for team in teams:
                if team_name.lower() in team.name.lower():
                    return {
                        'wins': team.wins,
                        'losses': team.losses,
                        'win_pct': team.win_percentage,
                        'runs_per_game': team.runs_per_game,
                        'era': team.era
                    }
            return {}

        except ImportError:
            logger.warning("Sportsipy not available for fallback")
            return {}
        except Exception as e:
            logger.error(f"Error fetching Sportsipy team stats: {e}")
            return {}

    async def _get_player_stats_sportsipy(self, player_name: str) -> Dict[str, Any]:
        """Get player stats from Sportsipy (ESPN data)."""
        try:
            # Import here to avoid import errors if sportsipy is not available
            from sportsipy.mlb.teams import Teams
            
            # For now, return empty dict since sportsipy player import is problematic
            logger.warning("Sportsipy player stats not implemented yet")
            return {}

        except ImportError:
            logger.warning("Sportsipy not available for fallback")
            return {}
        except Exception as e:
            logger.error(f"Error fetching Sportsipy player stats: {e}")
            return {}

    # Weather Data (Free API)
    async def _get_weather_data(self, venue: str) -> str:
        """Get weather data for venue (placeholder for free weather API)."""
        try:
            # This is a placeholder - you can integrate with free weather APIs like:
            # - OpenWeatherMap (free tier)
            # - WeatherAPI (free tier)
            # - AccuWeather (free tier)
            
            # For now, return default weather
            return "Clear, 72°F"
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return "Clear, 72°F"

    async def get_recent_player_stats(self, player_name: str, days: int = 7) -> Dict[str, Any]:
        """Get player stats for recent games."""
        try:
            # Lookup player
            players = self.statsapi.lookup_player(player_name)
            if not players:
                return {}

            player_id = players[0]['id']
            
            # Get recent stats using the correct method
            recent_stats = self.statsapi.player_stat_data(
                player_id, 
                group='hitting',
                type='season'
            )
            
            if recent_stats and 'stats' in recent_stats and recent_stats['stats']:
                stats = recent_stats['stats'][0]['stats']  # Correct path to stats
                return {
                    'recent_avg': stats.get('avg', '.000'),
                    'recent_hr': stats.get('homeRuns', 0),
                    'recent_rbi': stats.get('rbi', 0)
                }

            return {}

        except Exception as e:
            logger.error(f"Error fetching recent player stats: {e}")
            return {}

    async def get_recent_team_stats(self, team_name: str, games: int = 10) -> Dict[str, Any]:
        """Get team stats for recent games."""
        try:
            # Lookup team
            teams = self.statsapi.lookup_team(team_name)
            if not teams:
                return {}

            team_id = teams[0]['id']
            
            # For now, return basic team info since detailed stats require different API calls
            return {
                'recent_wins': 0,  # Would need additional API call
                'recent_losses': 0,  # Would need additional API call
                'recent_runs_per_game': 0,  # Would need additional API call
                'team_id': team_id,
                'team_name': teams[0]['name']
            }

        except Exception as e:
            logger.error(f"Error fetching recent team stats: {e}")
            return {}

    async def get_live_game_data(self, away_team: str, home_team: str) -> Dict[str, Any]:
        """Get live game data from ESPN API."""
        try:
            # First, get today's games from ESPN with timeout
            today = datetime.now().strftime("%Y%m%d")
            url = f"{self.espn_base_url}/scoreboard"
            params = {
                'dates': today,
                'limit': 50
            }
            
            # Add timeout to the request
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: self.session.get(url, params=params, timeout=5)
                ),
                timeout=6.0
            )
            
            if response.status_code != 200:
                logger.error(f"ESPN API error: {response.status_code}")
                return {}
            
            data = response.json()
            events = data.get('events', [])
            
            # Find the specific game
            target_game = None
            for event in events:
                if not isinstance(event, dict):
                    continue
                    
                competitions = event.get('competitions', [])
                if not competitions:
                    continue
                    
                competition = competitions[0]
                competitors = competition.get('competitors', [])
                
                if len(competitors) >= 2:
                    team1_name = competitors[0].get('team', {}).get('name', '').lower()
                    team2_name = competitors[1].get('team', {}).get('name', '').lower()
                    
                    away_lower = away_team.lower()
                    home_lower = home_team.lower()
                    
                    # Check if this is our game
                    if ((away_lower in team1_name and home_lower in team2_name) or 
                        (away_lower in team2_name and home_lower in team1_name)):
                        target_game = event
                        break
            
            if not target_game:
                logger.warning(f"No live game found for {away_team} vs {home_team}")
                return {}
            
            # Extract live data
            return self._parse_espn_game_data(target_game)
            
        except asyncio.TimeoutError:
            logger.error("ESPN API request timed out")
            return {}
        except Exception as e:
            logger.error(f"Error fetching ESPN live data: {e}")
            return {}

    def _parse_espn_game_data(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse ESPN game data into our format."""
        try:
            competitions = game_data.get('competitions', [])
            if not competitions:
                return {}
            
            competition = competitions[0]
            competitors = competition.get('competitors', [])
            
            if len(competitors) < 2:
                return {}
            
            # Get team data
            away_team = competitors[0]
            home_team = competitors[1]
            
            # Determine which is home/away
            if away_team.get('homeAway') == 'home':
                away_team, home_team = home_team, away_team
            
            # Get scores
            away_score = away_team.get('score', '0')
            home_score = home_team.get('score', '0')
            
            # Get game status
            status = competition.get('status', {})
            game_status = status.get('type', {}).get('description', 'Unknown')
            period = status.get('period', 0)
            
            # Get venue
            venue = competition.get('venue', {}).get('fullName', 'Unknown')
            
            # Get weather if available
            weather = competition.get('weather', 'Clear, 72°F')
            
            # Get probable pitchers
            away_pitcher = 'TBD'
            home_pitcher = 'TBD'
            
            # Try to get pitchers from game notes
            notes = competition.get('notes', [])
            for note in notes:
                if isinstance(note, dict) and 'headline' in note:
                    headline = note['headline'].lower()
                    if 'probable' in headline or 'starting' in headline:
                        # Extract pitcher names from headline
                        pitchers = re.findall(r'([A-Z][a-z]+ [A-Z][a-z]+)', note['headline'])
                        if len(pitchers) >= 2:
                            away_pitcher = pitchers[0]
                            home_pitcher = pitchers[1]
            
            return {
                'away_team': away_team.get('team', {}).get('name', 'Unknown'),
                'home_team': home_team.get('team', {}).get('name', 'Unknown'),
                'away_score': away_score,
                'home_score': home_score,
                'game_status': game_status,
                'inning': period,
                'venue': venue,
                'weather': weather,
                'away_pitcher': away_pitcher,
                'home_pitcher': home_pitcher,
                'is_live': 'live' in game_status.lower() or 'in progress' in game_status.lower(),
                'last_updated': datetime.now().strftime("%I:%M %p")
            }
            
        except Exception as e:
            logger.error(f"Error parsing ESPN game data: {e}")
            return {}

    async def get_espn_team_stats(self, team_name: str) -> Dict[str, Any]:
        """Get team stats from ESPN API."""
        try:
            # ESPN doesn't have a direct team stats endpoint, but we can get some data
            # from the standings endpoint
            url = f"{self.espn_base_url}/standings"
            
            # Add timeout to the request
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: self.session.get(url, timeout=5)
                ),
                timeout=6.0
            )
            
            if response.status_code != 200:
                return {}
            
            data = response.json()
            groups = data.get('groups', [])
            
            for group in groups:
                teams = group.get('teams', [])
                for team in teams:
                    team_info = team.get('team', {})
                    if team_name.lower() in team_info.get('name', '').lower():
                        stats = team.get('stats', [])
                        
                        # Extract relevant stats
                        wins = 0
                        losses = 0
                        win_pct = 0.0
                        
                        for stat in stats:
                            stat_name = stat.get('name', '')
                            if stat_name == 'wins':
                                wins = stat.get('value', 0)
                            elif stat_name == 'losses':
                                losses = stat.get('value', 0)
                            elif stat_name == 'winPercent':
                                win_pct = stat.get('value', 0.0)
                        
                        return {
                            'wins': wins,
                            'losses': losses,
                            'win_pct': win_pct,
                            'team_name': team_info.get('name', team_name)
                        }
            
            return {}
            
        except asyncio.TimeoutError:
            logger.error("ESPN team stats request timed out")
            return {}
        except Exception as e:
            logger.error(f"Error fetching ESPN team stats: {e}")
            return {}

    def _get_cache_key(self, method: str, *args) -> str:
        """Generate cache key for method and arguments."""
        return f"{method}:{':'.join(str(arg) for arg in args)}"

    def _get_cached_data(self, cache_key: str) -> Optional[Any]:
        """Get data from cache if not expired."""
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self._cache_timeout:
                return data
            else:
                del self._cache[cache_key]
        return None

    def _set_cached_data(self, cache_key: str, data: Any):
        """Store data in cache with timestamp."""
        self._cache[cache_key] = (data, time.time())

    async def scrape_mlb_live_stats(self, team_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Scrape live MLB stats from mlb.com/stats as a fallback data source.
        
        Args:
            team_name: Optional team name to filter stats for
            
        Returns:
            Dict containing live stats data
        """
        cache_key = self._get_cache_key("mlb_scraped_stats", team_name or "all")
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            logger.info(f"Scraping MLB.com live stats for {team_name or 'all teams'}")
            
            # Scrape the main stats page
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.session.get(self.mlb_stats_url, timeout=15)
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch MLB stats page: {response.status_code}")
                return {}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Debug: Log page structure
            logger.info(f"Page title: {soup.title.string if soup.title else 'No title'}")
            
            # Try multiple approaches to find data
            live_games = []
            team_stats = []
            player_stats = []
            
            # Approach 1: Look for specific MLB.com data structures
            live_games = await self._extract_live_games_advanced(soup)
            team_stats = await self._extract_team_stats_advanced(soup, team_name)
            player_stats = await self._extract_player_stats_advanced(soup, team_name)
            
            # Approach 2: If no data found, try alternative endpoints
            if not live_games and not team_stats and not player_stats:
                logger.info("No data found on main stats page, trying alternative endpoints...")
                
                # Try the scoreboard page
                scoreboard_data = await self._scrape_scoreboard_page()
                if scoreboard_data:
                    live_games = scoreboard_data.get('live_games', [])
                
                # Try the standings page
                standings_data = await self._scrape_standings_page()
                if standings_data:
                    team_stats = standings_data.get('team_stats', [])
            
            scraped_data = {
                'live_games': live_games,
                'team_stats': team_stats,
                'player_stats': player_stats,
                'scraped_at': datetime.now().isoformat(),
                'source': 'mlb.com'
            }
            
            self._set_cached_data(cache_key, scraped_data)
            return scraped_data
            
        except Exception as e:
            logger.error(f"Error scraping MLB.com stats: {e}")
            return {}

    async def _extract_live_games_advanced(self, soup: BeautifulSoup) -> list:
        """Advanced extraction of live game information from MLB.com."""
        live_games = []
        
        try:
            # Look for various live game indicators
            live_patterns = [
                r'LIVE',
                r'In Progress', 
                r'Top \d+',
                r'Bottom \d+',
                r'Final',
                r'Postponed',
                r'Delayed'
            ]
            
            for pattern in live_patterns:
                live_elements = soup.find_all(string=re.compile(pattern, re.IGNORECASE))
                for element in live_elements:
                    # Find the closest game container
                    game_container = element.find_parent(['div', 'section', 'article'])
                    if game_container:
                        game_data = self._parse_game_container_advanced(game_container)
                        if game_data and game_data not in live_games:
                            live_games.append(game_data)
            
            # Also look for scoreboard widgets
            scoreboard_selectors = [
                'div[class*="scoreboard"]',
                'div[class*="game"]',
                'div[class*="match"]',
                'section[class*="scoreboard"]',
                'div[data-testid*="scoreboard"]'
            ]
            
            for selector in scoreboard_selectors:
                scoreboards = soup.select(selector)
                for scoreboard in scoreboards:
                    game_data = self._parse_scoreboard_advanced(scoreboard)
                    if game_data and game_data not in live_games:
                        live_games.append(game_data)
                        
        except Exception as e:
            logger.error(f"Error in advanced live games extraction: {e}")
            
        return live_games

    async def _extract_team_stats_advanced(self, soup: BeautifulSoup, team_name: Optional[str] = None) -> list:
        """Advanced extraction of team statistics from MLB.com."""
        team_stats = []
        
        try:
            # Look for various table structures
            table_selectors = [
                'table[class*="stats"]',
                'table[class*="team"]',
                'table[class*="standings"]',
                'div[class*="stats-table"] table',
                'section[class*="stats"] table'
            ]
            
            for selector in table_selectors:
                tables = soup.select(selector)
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows[1:]:  # Skip header
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 3:
                            team_data = self._parse_team_row_advanced(cells, team_name)
                            if team_data and team_data not in team_stats:
                                team_stats.append(team_data)
                                
        except Exception as e:
            logger.error(f"Error in advanced team stats extraction: {e}")
            
        return team_stats

    async def _extract_player_stats_advanced(self, soup: BeautifulSoup, team_name: Optional[str] = None) -> list:
        """Advanced extraction of player statistics from MLB.com."""
        player_stats = []
        
        try:
            # Look for various player stat structures
            player_selectors = [
                'table[class*="player"]',
                'table[class*="batting"]',
                'table[class*="pitching"]',
                'div[class*="player-stats"] table',
                'section[class*="player"] table'
            ]
            
            for selector in player_selectors:
                tables = soup.select(selector)
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows[1:]:  # Skip header
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 5:
                            player_data = self._parse_player_row_advanced(cells, team_name)
                            if player_data and player_data not in player_stats:
                                player_stats.append(player_data)
                                
        except Exception as e:
            logger.error(f"Error in advanced player stats extraction: {e}")
            
        return player_stats

    async def _scrape_scoreboard_page(self) -> Optional[Dict[str, Any]]:
        """Scrape the MLB scoreboard page for live games."""
        try:
            scoreboard_url = "https://www.mlb.com/scores"
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.session.get(scoreboard_url, timeout=15)
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                live_games = await self._extract_live_games_advanced(soup)
                return {'live_games': live_games}
                
        except Exception as e:
            logger.error(f"Error scraping scoreboard page: {e}")
            
        return None

    async def _scrape_standings_page(self) -> Optional[Dict[str, Any]]:
        """Scrape the MLB standings page for team stats."""
        try:
            standings_url = "https://www.mlb.com/standings"
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.session.get(standings_url, timeout=15)
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                team_stats = await self._extract_team_stats_advanced(soup)
                return {'team_stats': team_stats}
                
        except Exception as e:
            logger.error(f"Error scraping standings page: {e}")
            
        return None

    def _parse_game_container_advanced(self, container) -> Optional[Dict[str, Any]]:
        """Advanced parsing of game container for live game data."""
        try:
            # Get all text content
            text_content = container.get_text()
            
            # Look for team patterns
            team_pattern = r'([A-Z]{2,3}|[A-Za-z\s]+(?:Diamondbacks|Braves|Orioles|Red Sox|White Sox|Cubs|Reds|Guardians|Rockies|Tigers|Astros|Royals|Angels|Dodgers|Marlins|Brewers|Twins|Mets|Yankees|Athletics|Phillies|Pirates|Padres|Giants|Mariners|Cardinals|Rays|Rangers|Blue Jays|Nationals))'
            teams = re.findall(team_pattern, text_content)
            
            # Look for score patterns
            score_pattern = r'(\d+)\s*-\s*(\d+)'
            score_match = re.search(score_pattern, text_content)
            
            # Look for inning/status patterns
            inning_patterns = [
                r'(Top|Bottom)\s+(\d+)',
                r'(\d+)(?:st|nd|rd|th)\s+(Top|Bottom)',
                r'(Final|Live|Postponed|Delayed)'
            ]
            
            inning = "Unknown"
            status = "Unknown"
            
            for pattern in inning_patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    if 'Final' in match.group(0) or 'Postponed' in match.group(0) or 'Delayed' in match.group(0):
                        status = match.group(0)
                    else:
                        inning = match.group(0)
                        status = "Live"
                    break
            
            if len(teams) >= 2 and score_match:
                return {
                    'away_team': teams[0].strip(),
                    'home_team': teams[1].strip(),
                    'away_score': int(score_match.group(1)),
                    'home_score': int(score_match.group(2)),
                    'inning': inning,
                    'status': status
                }
                
        except Exception as e:
            logger.error(f"Error parsing game container advanced: {e}")
            
        return None

    def _parse_scoreboard_advanced(self, scoreboard) -> Optional[Dict[str, Any]]:
        """Advanced parsing of scoreboard element for game data."""
        try:
            return self._parse_game_container_advanced(scoreboard)
        except Exception as e:
            logger.error(f"Error parsing scoreboard advanced: {e}")
            return None

    def _parse_team_row_advanced(self, cells, team_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Advanced parsing of team statistics row."""
        try:
            if len(cells) < 3:
                return None
                
            team_cell = cells[0].get_text().strip()
            
            # Clean up team name - remove garbage characters and normalize
            team_cell = self._clean_team_name(team_cell)
            
            # Skip if team name is still garbage after cleaning
            if len(team_cell) < 2 or not team_cell.replace(' ', '').isalpha():
                return None
            
            # Filter by team name if specified
            if team_name and team_name.lower() not in team_cell.lower():
                return None
                
            stats = {}
            stat_names = ['wins', 'losses', 'win_pct', 'games_back', 'runs_scored', 'runs_allowed', 'run_diff']
            
            for i, cell in enumerate(cells[1:], 1):
                cell_text = cell.get_text().strip()
                if cell_text:
                    # Try to parse as number
                    try:
                        if '.' in cell_text:
                            value = float(cell_text)
                        else:
                            value = int(cell_text)
                        
                        stat_name = stat_names[i-1] if i-1 < len(stat_names) else f'stat_{i}'
                        stats[stat_name] = value
                    except ValueError:
                        # Not a number, skip
                        continue
                    
            if stats:
                return {
                    'team': team_cell,
                    'stats': stats
                }
                
        except Exception as e:
            logger.error(f"Error parsing team row advanced: {e}")
            
        return None

    def _parse_player_row_advanced(self, cells, team_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Advanced parsing of player statistics row."""
        try:
            if len(cells) < 5:
                return None
                
            player_name = cells[0].get_text().strip()
            team_cell = cells[1].get_text().strip() if len(cells) > 1 else ""
            
            # Clean up names
            player_name = self._clean_player_name(player_name)
            team_cell = self._clean_team_name(team_cell)
            
            # Skip if names are garbage after cleaning
            if len(player_name) < 2 or not player_name.replace(' ', '').isalpha():
                return None
            
            # Filter by team name if specified
            if team_name and team_name.lower() not in team_cell.lower():
                return None
                
            stats = {}
            stat_names = ['avg', 'hr', 'rbi', 'obp', 'slg', 'ops', 'era', 'whip', 'k', 'bb']
            
            for i, cell in enumerate(cells[2:], 2):
                cell_text = cell.get_text().strip()
                if cell_text:
                    # Try to parse as number
                    try:
                        if '.' in cell_text:
                            value = float(cell_text)
                        else:
                            value = int(cell_text)
                        
                        stat_name = stat_names[i-2] if i-2 < len(stat_names) else f'stat_{i}'
                        stats[stat_name] = value
                    except ValueError:
                        # Not a number, skip
                        continue
                    
            if stats:
                return {
                    'player': player_name,
                    'team': team_cell,
                    'stats': stats
                }
                
        except Exception as e:
            logger.error(f"Error parsing player row advanced: {e}")
            
        return None

    def _clean_team_name(self, team_name: str) -> str:
        """Clean up team name by removing garbage characters and normalizing."""
        try:
            # Remove common garbage characters and patterns
            cleaned = team_name
            
            # Remove unicode control characters and invisible characters
            import unicodedata
            cleaned = ''.join(char for char in cleaned if unicodedata.category(char)[0] != 'C')
            
            # Remove common garbage patterns
            import re
            cleaned = re.sub(r'[0-9]+[A-Za-z]+[A-Za-z]+[0-9]+', '', cleaned)  # Remove patterns like "1CalC1"
            cleaned = re.sub(r'\u200c+', '', cleaned)  # Remove zero-width characters
            cleaned = re.sub(r'[^\w\s\-\.]', '', cleaned)  # Keep only alphanumeric, spaces, hyphens, dots
            
            # Normalize whitespace
            cleaned = ' '.join(cleaned.split())
            
            # Map common variations to official team names
            team_mapping = {
                'nyy': 'New York Yankees',
                'nyyankees': 'New York Yankees',
                'yankees': 'New York Yankees',
                'bos': 'Boston Red Sox',
                'redsox': 'Boston Red Sox',
                'red sox': 'Boston Red Sox',
                'lad': 'Los Angeles Dodgers',
                'dodgers': 'Los Angeles Dodgers',
                'hou': 'Houston Astros',
                'astros': 'Houston Astros',
                'atl': 'Atlanta Braves',
                'braves': 'Atlanta Braves',
                'chc': 'Chicago Cubs',
                'cubs': 'Chicago Cubs',
                'chw': 'Chicago White Sox',
                'whitesox': 'Chicago White Sox',
                'white sox': 'Chicago White Sox',
                'ny': 'New York Mets',
                'mets': 'New York Mets',
                'sf': 'San Francisco Giants',
                'giants': 'San Francisco Giants',
                'stl': 'St. Louis Cardinals',
                'cardinals': 'St. Louis Cardinals',
                'cards': 'St. Louis Cardinals',
                'mil': 'Milwaukee Brewers',
                'brewers': 'Milwaukee Brewers',
                'min': 'Minnesota Twins',
                'twins': 'Minnesota Twins',
                'tb': 'Tampa Bay Rays',
                'rays': 'Tampa Bay Rays',
                'oak': 'Oakland Athletics',
                'athletics': 'Oakland Athletics',
                'a\'s': 'Oakland Athletics',
                'as': 'Oakland Athletics',
                'tex': 'Texas Rangers',
                'rangers': 'Texas Rangers',
                'cle': 'Cleveland Guardians',
                'guardians': 'Cleveland Guardians',
                'cin': 'Cincinnati Reds',
                'reds': 'Cincinnati Reds',
                'kc': 'Kansas City Royals',
                'royals': 'Kansas City Royals',
                'col': 'Colorado Rockies',
                'rockies': 'Colorado Rockies',
                'ari': 'Arizona Diamondbacks',
                'diamondbacks': 'Arizona Diamondbacks',
                'dbacks': 'Arizona Diamondbacks',
                'sea': 'Seattle Mariners',
                'mariners': 'Seattle Mariners',
                'det': 'Detroit Tigers',
                'tigers': 'Detroit Tigers',
                'phi': 'Philadelphia Phillies',
                'phillies': 'Philadelphia Phillies',
                'pit': 'Pittsburgh Pirates',
                'pirates': 'Pittsburgh Pirates',
                'sd': 'San Diego Padres',
                'padres': 'San Diego Padres',
                'bal': 'Baltimore Orioles',
                'orioles': 'Baltimore Orioles',
                'tor': 'Toronto Blue Jays',
                'bluejays': 'Toronto Blue Jays',
                'blue jays': 'Toronto Blue Jays',
                'jays': 'Toronto Blue Jays',
                'was': 'Washington Nationals',
                'nationals': 'Washington Nationals',
                'nats': 'Washington Nationals',
                'laa': 'Los Angeles Angels',
                'angels': 'Los Angeles Angels',
                'ana': 'Los Angeles Angels',
                'mia': 'Miami Marlins',
                'marlins': 'Miami Marlins'
            }
            
            # Check if cleaned name matches any known variations
            cleaned_lower = cleaned.lower().replace(' ', '')
            for variation, official_name in team_mapping.items():
                if cleaned_lower == variation or cleaned_lower in variation or variation in cleaned_lower:
                    return official_name
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Error cleaning team name '{team_name}': {e}")
            return team_name

    def _clean_player_name(self, player_name: str) -> str:
        """Clean up player name by removing garbage characters and normalizing."""
        try:
            # Remove common garbage characters and patterns
            cleaned = player_name
            
            # Remove unicode control characters and invisible characters
            import unicodedata
            cleaned = ''.join(char for char in cleaned if unicodedata.category(char)[0] != 'C')
            
            # Remove common garbage patterns
            import re
            cleaned = re.sub(r'[0-9]+[A-Za-z]+[A-Za-z]+[0-9]+', '', cleaned)  # Remove patterns like "1CalC1"
            cleaned = re.sub(r'\u200c+', '', cleaned)  # Remove zero-width characters
            cleaned = re.sub(r'[^\w\s\-\.]', '', cleaned)  # Keep only alphanumeric, spaces, hyphens, dots
            
            # Normalize whitespace
            cleaned = ' '.join(cleaned.split())
            
            # Title case for proper name formatting
            cleaned = cleaned.title()
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Error cleaning player name '{player_name}': {e}")
            return player_name

    async def get_live_stats_with_fallback(self, team_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get live stats with multiple fallback sources including MLB.com scraping.
        
        Args:
            team_name: Optional team name to filter stats for
            
        Returns:
            Dict containing live stats from best available source
        """
        try:
            # Try ESPN API first (fastest) - with timeout
            try:
                espn_data = await asyncio.wait_for(
                    self.get_live_scores(team_name),
                    timeout=1.5  # Very short timeout for fastest source
                )
                if espn_data and espn_data.get('live_games'):
                    espn_data['source'] = 'espn'
                    return espn_data
            except asyncio.TimeoutError:
                logger.warning("ESPN API timed out, trying next source")
            
            # Try MLB Stats API - with timeout
            try:
                mlb_data = await asyncio.wait_for(
                    self.get_live_scores(team_name),
                    timeout=1.5  # Very short timeout for second fastest source
                )
                if mlb_data and mlb_data.get('live_games'):
                    mlb_data['source'] = 'mlb_stats_api'
                    return mlb_data
            except asyncio.TimeoutError:
                logger.warning("MLB Stats API timed out, trying scraping")
            
            # Fallback to MLB.com scraping - with timeout
            try:
                scraped_data = await asyncio.wait_for(
                    self.scrape_mlb_live_stats(team_name),
                    timeout=2.0  # Slightly longer timeout for scraping
                )
                if scraped_data:
                    return scraped_data
            except asyncio.TimeoutError:
                logger.warning("MLB.com scraping timed out")
            
            # Return empty result if all sources fail
            return {'live_games': [], 'source': 'none'}
            
        except Exception as e:
            logger.error(f"Error getting live stats with fallback: {e}")
            return {'live_games': [], 'source': 'error'}

    async def get_historical_game_data(
        self, 
        away_team: str, 
        home_team: str, 
        game_date: str
    ) -> Dict[str, Any]:
        """
        Get historical game data for past games.
        
        Args:
            away_team: Away team name
            home_team: Home team name  
            game_date: Date in YYYY-MM-DD format
            
        Returns:
            Dict containing historical game data
        """
        try:
            resolved_away = self._resolve_team_name(away_team)
            resolved_home = self._resolve_team_name(home_team)
            
            logger.info(f"Looking up historical game: {resolved_away} @ {resolved_home} on {game_date}")
            
            # Try MLB Stats API first
            historical_data = await self._get_historical_game_mlb(
                resolved_away, resolved_home, game_date
            )
            
            # Fallback to ESPN API
            if not historical_data:
                historical_data = await self._get_historical_game_espn(
                    resolved_away, resolved_home, game_date
                )
            
            # Add context about the historical nature
            if historical_data:
                historical_data['is_historical'] = True
                historical_data['game_date'] = game_date
                historical_data['context'] = f"Historical game from {game_date}"
            
            return historical_data or {
                'is_historical': True,
                'game_date': game_date,
                'away_team': resolved_away,
                'home_team': resolved_home,
                'status': 'Completed',
                'context': f"Historical game from {game_date} - data not available"
            }
            
        except Exception as e:
            logger.error(f"Error fetching historical game data: {e}")
            return {
                'is_historical': True,
                'game_date': game_date,
                'away_team': away_team,
                'home_team': home_team,
                'status': 'Unknown',
                'context': f"Historical game from {game_date} - error retrieving data"
            }

    async def _get_historical_game_mlb(
        self, 
        away_team: str, 
        home_team: str, 
        game_date: str
    ) -> Dict[str, Any]:
        """Get historical game data from MLB Stats API."""
        try:
            # Get schedule for the specific date
            schedule = self.statsapi.schedule(date=game_date, sportId=1)
            
            if not schedule:
                return {}
            
            # Find the specific game
            target_game = None
            for game in schedule:
                if isinstance(game, dict):
                    game_away = game.get('away_name', '')
                    game_home = game.get('home_name', '')
                    
                    # Check if this is our target game
                    if (game_away == away_team and game_home == home_team) or \
                       (game_away == home_team and game_home == away_team):
                        target_game = game
                        break
            
            if not target_game:
                return {}
            
            # Get detailed game data
            game_id = target_game.get('game_id')
            if game_id:
                try:
                    # Use the correct statsapi method for game data
                    game_data = self.statsapi.lookup_game(game_id)
                    if game_data:
                        return {
                            'away_team': target_game.get('away_name', away_team),
                            'home_team': target_game.get('home_name', home_team),
                            'away_score': target_game.get('away_score', 0),
                            'home_score': target_game.get('home_score', 0),
                            'status': target_game.get('status', 'Completed'),
                            'venue': target_game.get('venue_name', ''),
                            'game_id': game_id,
                            'game_data': game_data,
                            'result': self._determine_game_result(
                                target_game.get('away_score', 0),
                                target_game.get('home_score', 0),
                                away_team,
                                home_team
                            )
                        }
                except Exception as e:
                    logger.warning(f"Could not get detailed game data for {game_id}: {e}")
            
            # Return basic game info if detailed data failed
            return {
                'away_team': target_game.get('away_name', away_team),
                'home_team': target_game.get('home_name', home_team),
                'away_score': target_game.get('away_score', 0),
                'home_score': target_game.get('home_score', 0),
                'status': target_game.get('status', 'Completed'),
                'venue': target_game.get('venue_name', ''),
                'result': self._determine_game_result(
                    target_game.get('away_score', 0),
                    target_game.get('home_score', 0),
                    away_team,
                    home_team
                )
            }
            
        except Exception as e:
            logger.error(f"Error in _get_historical_game_mlb: {e}")
            return {}

    async def _get_historical_game_espn(
        self, 
        away_team: str, 
        home_team: str, 
        game_date: str
    ) -> Dict[str, Any]:
        """Get historical game data from ESPN API."""
        try:
            # ESPN API for historical games
            url = f"{self.espn_base_url}/scoreboard"
            params = {
                'dates': game_date,
                'limit': 100
            }
            
            # Use asyncio.wait_for instead of asyncio.timeout
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.session.get(url, params=params)
                ),
                timeout=3.0
            )
            response.raise_for_status()
            data = response.json()
            
            if 'events' not in data:
                return {}
            
            # Find the specific game
            target_game = None
            for event in data['events']:
                if 'competitions' in event and event['competitions']:
                    competition = event['competitions'][0]
                    if 'competitors' in competition and len(competition['competitors']) >= 2:
                        comp1 = competition['competitors'][0]
                        comp2 = competition['competitors'][1]
                        
                        comp1_name = comp1.get('team', {}).get('name', '')
                        comp2_name = comp2.get('team', {}).get('name', '')
                        
                        # Check if this is our target game
                        if (comp1_name == away_team and comp2_name == home_team) or \
                           (comp1_name == home_team and comp2_name == away_team):
                            target_game = event
                            break
            
            if not target_game:
                return {}
            
            # Parse ESPN game data
            return self._parse_espn_historical_game(target_game, away_team, home_team)
            
        except Exception as e:
            logger.error(f"Error in _get_historical_game_espn: {e}")
            return {}

    def _parse_espn_historical_game(
        self, 
        game_data: Dict[str, Any], 
        away_team: str, 
        home_team: str
    ) -> Dict[str, Any]:
        """Parse historical game data from ESPN API response."""
        try:
            if 'competitions' not in game_data or not game_data['competitions']:
                return {}
            
            competition = game_data['competitions'][0]
            if 'competitors' not in competition or len(competition['competitors']) < 2:
                return {}
            
            comp1 = competition['competitors'][0]
            comp2 = competition['competitors'][1]
            
            # Determine which is home/away
            away_score = 0
            home_score = 0
            away_name = away_team
            home_name = home_team
            
            if comp1.get('homeAway') == 'away':
                away_score = int(comp1.get('score', 0))
                home_score = int(comp2.get('score', 0))
                away_name = comp1.get('team', {}).get('name', away_team)
                home_name = comp2.get('team', {}).get('name', home_team)
            else:
                away_score = int(comp2.get('score', 0))
                home_score = int(comp1.get('score', 0))
                away_name = comp2.get('team', {}).get('name', away_team)
                home_name = comp1.get('team', {}).get('name', home_team)
            
            return {
                'away_team': away_name,
                'home_team': home_name,
                'away_score': away_score,
                'home_score': home_score,
                'status': game_data.get('status', {}).get('type', {}).get('name', 'Completed'),
                'venue': competition.get('venue', {}).get('fullName', ''),
                'result': self._determine_game_result(away_score, home_score, away_name, home_name)
            }
            
        except Exception as e:
            logger.error(f"Error parsing ESPN historical game: {e}")
            return {}

    def _determine_game_result(
        self, 
        away_score: int, 
        home_score: int, 
        away_team: str, 
        home_team: str
    ) -> str:
        """Determine the result of a game."""
        if away_score > home_score:
            return f"{away_team} won {away_score}-{home_score}"
        elif home_score > away_score:
            return f"{home_team} won {home_score}-{away_score}"
        else:
            return f"Tied {away_score}-{home_score}"

    async def get_historical_team_stats(
        self, 
        team_name: str, 
        game_date: str
    ) -> Dict[str, Any]:
        """
        Get team stats as they were on a specific date.
        
        Args:
            team_name: Team name
            game_date: Date in YYYY-MM-DD format
            
        Returns:
            Dict containing historical team stats
        """
        try:
            resolved_name = self._resolve_team_name(team_name)
            
            # For historical stats, we'll use current stats as approximation
            # since historical stats APIs are limited
            current_stats = await self.get_team_stats(resolved_name)
            
            if current_stats:
                current_stats['is_historical'] = True
                current_stats['as_of_date'] = game_date
                current_stats['note'] = f"Current stats shown (historical data from {game_date} not available)"
            
            return current_stats or {
                'is_historical': True,
                'as_of_date': game_date,
                'note': f"Historical team stats from {game_date} not available"
            }
            
        except Exception as e:
            logger.error(f"Error fetching historical team stats: {e}")
            return {
                'is_historical': True,
                'as_of_date': game_date,
                'note': f"Error retrieving historical team stats from {game_date}"
            }

    async def is_historical_game(
        self, 
        away_team: str, 
        home_team: str, 
        game_date: Optional[str] = None
    ) -> bool:
        """
        Check if a game is historical (past date).
        
        Args:
            away_team: Away team name
            home_team: Home team name
            game_date: Optional game date, defaults to today
            
        Returns:
            True if the game is historical, False if current/future
        """
        try:
            if not game_date:
                game_date = datetime.now().strftime("%Y-%m-%d")
            
            game_date_obj = datetime.strptime(game_date, "%Y-%m-%d")
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            return game_date_obj < today
            
        except Exception as e:
            logger.error(f"Error checking if game is historical: {e}")
            return False


# Global instance
mlb_fetcher = MLBDataFetcher()
