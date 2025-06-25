"""
Improved MLB Scraper - Fast, reliable data collection for MLB games
"""
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import time
import os

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
            'Los Angeles Angels': {'id': 108, 'abbr': 'LAA', 'city': 'Anaheim'},
            'Oakland Athletics': {'id': 133, 'abbr': 'OAK', 'city': 'Oakland'},
            'New York Yankees': {'id': 147, 'abbr': 'NYY', 'city': 'New York'},
            'Boston Red Sox': {'id': 111, 'abbr': 'BOS', 'city': 'Boston'},
            'Houston Astros': {'id': 117, 'abbr': 'HOU', 'city': 'Houston'},
            'Los Angeles Dodgers': {'id': 119, 'abbr': 'LAD', 'city': 'Los Angeles'},
            'San Francisco Giants': {'id': 137, 'abbr': 'SF', 'city': 'San Francisco'},
            'Colorado Rockies': {'id': 115, 'abbr': 'COL', 'city': 'Denver'},
            'Chicago Cubs': {'id': 112, 'abbr': 'CHC', 'city': 'Chicago'},
            'Chicago White Sox': {'id': 145, 'abbr': 'CWS', 'city': 'Chicago'},
            'Cleveland Guardians': {'id': 114, 'abbr': 'CLE', 'city': 'Cleveland'},
            'Detroit Tigers': {'id': 116, 'abbr': 'DET', 'city': 'Detroit'},
            'Kansas City Royals': {'id': 118, 'abbr': 'KC', 'city': 'Kansas City'},
            'Minnesota Twins': {'id': 142, 'abbr': 'MIN', 'city': 'Minneapolis'},
            'Baltimore Orioles': {'id': 110, 'abbr': 'BAL', 'city': 'Baltimore'},
            'Tampa Bay Rays': {'id': 139, 'abbr': 'TB', 'city': 'Tampa Bay'},
            'Toronto Blue Jays': {'id': 141, 'abbr': 'TOR', 'city': 'Toronto'},
            'Atlanta Braves': {'id': 144, 'abbr': 'ATL', 'city': 'Atlanta'},
            'Miami Marlins': {'id': 146, 'abbr': 'MIA', 'city': 'Miami'},
            'New York Mets': {'id': 121, 'abbr': 'NYM', 'city': 'New York'},
            'Philadelphia Phillies': {'id': 143, 'abbr': 'PHI', 'city': 'Philadelphia'},
            'Washington Nationals': {'id': 120, 'abbr': 'WSH', 'city': 'Washington'},
            'Arizona Diamondbacks': {'id': 109, 'abbr': 'ARI', 'city': 'Phoenix'},
            'San Diego Padres': {'id': 135, 'abbr': 'SD', 'city': 'San Diego'},
            'Seattle Mariners': {'id': 136, 'abbr': 'SEA', 'city': 'Seattle'},
            'Texas Rangers': {'id': 140, 'abbr': 'TEX', 'city': 'Arlington'},
            'Cincinnati Reds': {'id': 113, 'abbr': 'CIN', 'city': 'Cincinnati'},
            'Milwaukee Brewers': {'id': 158, 'abbr': 'MIL', 'city': 'Milwaukee'},
            'Pittsburgh Pirates': {'id': 134, 'abbr': 'PIT', 'city': 'Pittsburgh'},
            'St. Louis Cardinals': {'id': 138, 'abbr': 'STL', 'city': 'St. Louis'}
        }
    
    async def initialize(self):
        """Initialize the scraper session"""
        try:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
            logger.info("MLB scraper initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize MLB scraper: {e}")
            return False
    
    async def get_game_data(self, team1: str, team2: str) -> Dict[str, Any]:
        """Get comprehensive game data for two teams"""
        try:
            start_time = time.time()
            
            # Get team info
            team1_info = self.team_mapping.get(team1)
            team2_info = self.team_mapping.get(team2)
            
            if not team1_info or not team2_info:
                return {'error': 'Team not found'}
            
            # Fetch data concurrently
            tasks = [
                self._get_team_stats(team1_info['id']),
                self._get_team_stats(team2_info['id']),
                self._get_weather_data(team1_info['city']),
                self._get_weather_data(team2_info['city']),
                self._get_live_scores()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            team1_stats = results[0] if not isinstance(results[0], Exception) else {}
            team2_stats = results[1] if not isinstance(results[1], Exception) else {}
            team1_weather = results[2] if not isinstance(results[2], Exception) else {}
            team2_weather = results[3] if not isinstance(results[3], Exception) else {}
            live_scores = results[4] if not isinstance(results[4], Exception) and isinstance(results[4], list) else []
            
            # Check if teams are playing today
            today_game = self._find_today_game(live_scores, team1_info['abbr'], team2_info['abbr'])
            
            total_time = time.time() - start_time
            
            return {
                'teams': {
                    team1: {
                        'stats': team1_stats,
                        'weather': team1_weather,
                        'info': team1_info
                    },
                    team2: {
                        'stats': team2_stats,
                        'weather': team2_weather,
                        'info': team2_info
                    }
                },
                'today_game': today_game,
                'live_scores': live_scores,
                'fetch_time': total_time,
                'summary': f"Data loaded for {team1} vs {team2} in {total_time:.2f}s"
            }
            
        except Exception as e:
            logger.error(f"Error getting game data: {e}")
            return {'error': str(e)}
    
    async def _get_team_stats(self, team_id: int) -> Dict[str, Any]:
        """Get team statistics from MLB API, merging standings and stats endpoints."""
        cache_key = f"team_stats_{team_id}"
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_timeout:
                return data
        try:
            current_year = datetime.now().year
            # 1. Try to get standings (for win/loss)
            standings = await self._get_team_standings(team_id, current_year)
            # 2. Try to get stats (for advanced stats)
            url = f"{self.mlb_base}/teams/{team_id}/stats"
            params = {
                'season': current_year,
                'group': 'hitting',
                'stats': 'season'
            }
            async with self.session.get(url, params=params) as response:
                stats = {}
                if response.status == 200:
                    data = await response.json()
                    stats = self._parse_team_stats(data)
                # Fallback to previous year if no stats
                if not stats or (stats.get('games_played', 0) == 0):
                    params['season'] = current_year - 1
                    async with self.session.get(url, params=params) as response2:
                        if response2.status == 200:
                            data2 = await response2.json()
                            stats = self._parse_team_stats(data2)
                            if not stats:
                                stats['note'] = 'No stats found for current or previous season.'
                # Merge standings and stats
                merged = {**standings, **stats}
                if not merged or (merged.get('games_played', 0) == 0 and merged.get('wins', 0) == 0):
                    merged['note'] = 'Offseason or no data available.'
                self.cache[cache_key] = (time.time(), merged)
                return merged
        except Exception as e:
            logger.error(f"Error getting team stats: {e}")
            return {'note': f'Error fetching stats: {e}'}

    async def _get_team_standings(self, team_id: int, season: int) -> Dict[str, Any]:
        """Get win/loss records from MLB standings endpoint."""
        try:
            url = f"{self.mlb_base}/standings"
            params = {
                'leagueId': '103,104',  # AL and NL
                'season': season,
                'standingsTypes': 'regularSeason',
                'fields': 'records,team,id,name,wins,losses,runDifferential,divisionRank,leagueRank,divisionGamesBack,leagueGamesBack,elimNumber,clinched,divisionRecord,leagueRecord,home,away'
            }
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    # Traverse to find the team
                    for record in data.get('records', []):
                        for teamrec in record.get('teamRecords', []):
                            team = teamrec.get('team', {})
                            if team.get('id') == team_id:
                                return {
                                    'wins': teamrec.get('wins', 0),
                                    'losses': teamrec.get('losses', 0),
                                    'win_pct': teamrec.get('winningPercentage', 0.0),
                                    'run_diff': teamrec.get('runDifferential', 0),
                                    'games_played': teamrec.get('gamesPlayed', 0),
                                    'division_rank': teamrec.get('divisionRank'),
                                    'league_rank': teamrec.get('leagueRank'),
                                    'note': ''
                                }
            return {}
        except Exception as e:
            logger.error(f"Error getting team standings: {e}")
            return {}

    async def _get_weather_data(self, city: str) -> Dict[str, Any]:
        """Get weather data for a city (using OpenWeatherMap as fallback)"""
        cache_key = f"weather_{city}"
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_timeout:
                return data
        try:
            api_key = os.environ.get('OPENWEATHER_API_KEY')
            if api_key:
                url = f"{self.weather_api}?q={city},US&appid={api_key}&units=imperial"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        weather_data = {
                            'temperature': data.get('main', {}).get('temp', 72),
                            'humidity': data.get('main', {}).get('humidity', 65),
                            'wind_speed': data.get('wind', {}).get('speed', 8),
                            'wind_direction': self._get_wind_direction(data.get('wind', {}).get('deg', 225)),
                            'conditions': data.get('weather', [{}])[0].get('description', 'Partly Cloudy'),
                            'pressure': data.get('main', {}).get('pressure', 1013),
                            'source': 'OpenWeatherMap'
                        }
                    else:
                        weather_data = self._get_mock_weather(city)
                        weather_data['note'] = 'OpenWeatherMap API failed, using mock.'
            else:
                weather_data = self._get_mock_weather(city)
                weather_data['note'] = 'No API key, using mock.'
            self.cache[cache_key] = (time.time(), weather_data)
            return weather_data
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            fallback = self._get_mock_weather(city)
            fallback['note'] = f'Weather error: {e} (using mock)'
            return fallback
    
    def _get_mock_weather(self, city: str) -> Dict[str, Any]:
        """Get mock weather data based on city"""
        # Simple mock weather that varies by city
        import hashlib
        city_hash = int(hashlib.md5(city.encode()).hexdigest()[:8], 16)
        
        return {
            'temperature': 65 + (city_hash % 30),  # 65-95°F
            'humidity': 40 + (city_hash % 40),     # 40-80%
            'wind_speed': 5 + (city_hash % 15),    # 5-20 mph
            'wind_direction': ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'][city_hash % 8],
            'conditions': ['Sunny', 'Partly Cloudy', 'Cloudy', 'Light Rain'][city_hash % 4],
            'pressure': 1000 + (city_hash % 30)    # 1000-1030 hPa
        }
    
    def _get_wind_direction(self, degrees: float) -> str:
        """Convert wind degrees to direction"""
        if degrees is None:
            return 'N'
        
        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                     'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        index = round(degrees / 22.5) % 16
        return directions[index]
    
    async def _get_live_scores(self) -> List[Dict[str, Any]]:
        """Get live game scores"""
        cache_key = "live_scores"
        
        # Check cache (shorter timeout for live data)
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if time.time() - cache_time < 60:  # 1 minute cache for live data
                return data
        
        try:
            # Get today's games
            today = datetime.now().strftime('%Y-%m-%d')
            url = f"{self.mlb_base}/schedule"
            params = {
                'sportId': 1,
                'date': today,
                'fields': 'dates,games,gamePk,teams,away,home,team,abbreviation,score,status,detailedState'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    games = self._parse_live_scores(data)
                    
                    # Cache the result
                    self.cache[cache_key] = (time.time(), games)
                    return games
                else:
                    logger.warning(f"Failed to get live scores: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting live scores: {e}")
            return []
    
    def _parse_team_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse team statistics from MLB API response"""
        try:
            if not data:
                return {}
                
            stats = data.get('stats', [])
            if not stats:
                return {}
            
            # Get the most recent stats
            stat = stats[0]
            splits = stat.get('splits', [])
            if not splits:
                return {}
            
            split = splits[0]
            stat_data = split.get('stat', {})
            
            return {
                'wins': stat_data.get('wins', 0),
                'losses': stat_data.get('losses', 0),
                'win_pct': stat_data.get('winPct', 0.0),
                'runs_scored': stat_data.get('runs', 0),
                'runs_allowed': stat_data.get('runsAllowed', 0),
                'run_diff': stat_data.get('runDifferential', 0),
                'games_played': stat_data.get('gamesPlayed', 0),
                'avg': stat_data.get('avg', 0.0),
                'obp': stat_data.get('obp', 0.0),
                'slg': stat_data.get('slg', 0.0),
                'era': stat_data.get('era', 0.0)
            }
            
        except Exception as e:
            logger.error(f"Error parsing team stats: {e}")
            return {}
    
    def _parse_live_scores(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse live scores from MLB API response"""
        try:
            if not data:
                return []
                
            games = []
            dates = data.get('dates', [])
            
            for date in dates:
                for game in date.get('games', []):
                    away_team = game.get('teams', {}).get('away', {})
                    home_team = game.get('teams', {}).get('home', {})
                    
                    games.append({
                        'away_team': away_team.get('team', {}).get('abbreviation', 'TBD'),
                        'home_team': home_team.get('team', {}).get('abbreviation', 'TBD'),
                        'away_score': away_team.get('score', 0),
                        'home_score': home_team.get('score', 0),
                        'status': game.get('status', {}).get('detailedState', 'Unknown'),
                        'game_pk': game.get('gamePk', 0)
                    })
            
            return games
            
        except Exception as e:
            logger.error(f"Error parsing live scores: {e}")
            return []
    
    def _find_today_game(self, games: List[Dict[str, Any]], team1_abbr: str, team2_abbr: str) -> Optional[Dict[str, Any]]:
        """Find if the two teams are playing today"""
        if not isinstance(games, list):
            return None
            
        for game in games:
            if not isinstance(game, dict):
                continue
                
            away = game.get('away_team')
            home = game.get('home_team')
            
            if (away == team1_abbr and home == team2_abbr) or (away == team2_abbr and home == team1_abbr):
                return game
        
        return None
    
    async def close(self):
        """Close the scraper session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_live_game_updates(self, game_id: Optional[str] = None) -> Dict[str, Any]:
        """Get real-time game updates and current state."""
        try:
            if not self.session:
                return {}
            
            # Get live scores and find specific game or all active games
            live_scores = await self._get_live_scores()
            
            if game_id:
                # Find specific game
                for game in live_scores:
                    if str(game.get('game_pk')) == game_id:
                        return await self._get_detailed_game_state(game)
                return {}
            else:
                # Get all active games
                active_games = []
                for game in live_scores:
                    if game.get('status') in ['Live', 'In Progress', 'Delayed']:
                        detailed_state = await self._get_detailed_game_state(game)
                        if detailed_state:
                            active_games.append(detailed_state)
                
                return {
                    'active_games': active_games,
                    'total_active': len(active_games),
                    'last_updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting live game updates: {e}")
            return {}
    
    async def _get_detailed_game_state(self, game: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed game state including inning, score, and situation."""
        try:
            game_pk = game.get('game_pk')
            if not game_pk:
                return {}
            
            # Get detailed game data from MLB API
            url = f"{self.mlb_base}/game/{game_pk}/feed/live"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {}
                
                data = await response.json()
                return self._parse_detailed_game_state(data, game)
                
        except Exception as e:
            logger.error(f"Error getting detailed game state: {e}")
            return {}
    
    def _parse_detailed_game_state(self, data: Dict[str, Any], basic_game: Dict[str, Any]) -> Dict[str, Any]:
        """Parse detailed game state from MLB API response."""
        try:
            game_data = data.get('gameData', {})
            live_data = data.get('liveData', {})
            
            # Get current inning info
            plays = live_data.get('plays', {})
            current_play = plays.get('currentPlay', {})
            all_plays = plays.get('allPlays', [])
            
            # Get boxscore for detailed stats
            boxscore = live_data.get('boxscore', {})
            teams = boxscore.get('teams', {})
            
            # Determine current situation
            situation = self._determine_game_situation(current_play, all_plays)
            
            return {
                'game_id': basic_game.get('game_pk'),
                'away_team': basic_game.get('away_team'),
                'home_team': basic_game.get('home_team'),
                'away_score': basic_game.get('away_score', 0),
                'home_score': basic_game.get('home_score', 0),
                'status': basic_game.get('status', 'Unknown'),
                'current_inning': situation.get('inning'),
                'inning_state': situation.get('inning_state'),  # top, bottom, middle, end
                'outs': situation.get('outs', 0),
                'runners': situation.get('runners', []),
                'batter': situation.get('batter'),
                'pitcher': situation.get('pitcher'),
                'last_play': situation.get('last_play'),
                'weather': self._get_game_weather(game_data),
                'start_time': game_data.get('datetime', {}).get('officialDate'),
                'venue': game_data.get('venue', {}).get('name'),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing detailed game state: {e}")
            return {}
    
    def _determine_game_situation(self, current_play: Dict[str, Any], all_plays: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Determine current game situation from plays data."""
        try:
            situation = {
                'inning': 1,
                'inning_state': 'top',
                'outs': 0,
                'runners': [],
                'batter': None,
                'pitcher': None,
                'last_play': None
            }
            
            if current_play:
                # Extract info from current play
                situation['inning'] = current_play.get('about', {}).get('inning', 1)
                situation['inning_state'] = current_play.get('about', {}).get('inningState', 'top')
                situation['outs'] = current_play.get('count', {}).get('outs', 0)
                
                # Get batter and pitcher
                situation['batter'] = current_play.get('matchup', {}).get('batter', {}).get('fullName')
                situation['pitcher'] = current_play.get('matchup', {}).get('pitcher', {}).get('fullName')
                
                # Get runners on base
                situation['runners'] = self._get_runners_on_base(current_play)
                
                # Get last play description
                situation['last_play'] = current_play.get('result', {}).get('description', 'No play data')
            
            return situation
            
        except Exception as e:
            logger.error(f"Error determining game situation: {e}")
            return {'inning': 1, 'inning_state': 'top', 'outs': 0, 'runners': []}
    
    def _get_runners_on_base(self, play: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get current runners on base."""
        try:
            runners = []
            runner_data = play.get('runners', [])
            
            for runner in runner_data:
                if runner.get('movement', {}).get('start') != 'batter':
                    runners.append({
                        'name': runner.get('details', {}).get('runner', {}).get('fullName'),
                        'base': runner.get('movement', {}).get('start'),
                        'out': runner.get('movement', {}).get('end') == 'out'
                    })
            
            return runners
            
        except Exception as e:
            logger.error(f"Error getting runners on base: {e}")
            return []
    
    def _get_game_weather(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather data for the game."""
        try:
            weather = game_data.get('weather', {})
            return {
                'temperature': weather.get('temp'),
                'condition': weather.get('condition'),
                'wind_speed': weather.get('wind', {}).get('speed'),
                'wind_direction': weather.get('wind', {}).get('direction'),
                'humidity': weather.get('humidity')
            }
        except Exception as e:
            logger.error(f"Error getting game weather: {e}")
            return {} 