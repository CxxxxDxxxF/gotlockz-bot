"""
Improved MLB Scraper - Fast, reliable data collection for MLB games
"""
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
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
            live_scores = (results[4] if not isinstance(results[4], Exception)
                           and isinstance(results[4], list) else [])

            # Check if teams are playing today
            today_game = self._find_today_game(live_scores, team1_info['abbr'],
                team2_info['abbr'])

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
        
        # Check cache first
        cached_data = self._get_cached_team_stats(cache_key)
        if cached_data:
            return cached_data
            
        try:
            current_year = datetime.now().year
            
            # Get standings and stats
            standings = await self._get_team_standings(team_id, current_year)
            stats = await self._fetch_team_stats_with_fallback(team_id, current_year)
            
            # Merge and handle edge cases
            merged = self._merge_team_data(standings, stats, current_year)
            
            # Cache the result
            self.cache[cache_key] = (time.time(), merged)
            return merged
            
        except Exception as e:
            logger.error(f"Error getting team stats: {e}")
            return {'note': f'Error fetching stats: {e}'}

    def _get_cached_team_stats(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached team stats if available and not expired."""
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_timeout:
                return data
        return None

    async def _fetch_team_stats_with_fallback(self, team_id: int, current_year: int) -> Dict[str, Any]:
        """Fetch team stats with fallback to previous year if needed."""
        # Try current year first
        stats = await self._fetch_team_stats(team_id, current_year)
        
        # Fallback to previous year if no stats or offseason
        if self._should_fallback_to_previous_year(stats):
            stats = await self._fetch_team_stats(team_id, current_year - 1)
            if stats:
                stats['note'] = 'Using previous season data (offseason).'
            else:
                stats = {'note': 'No stats found for current or previous season.'}
        
        return stats

    async def _fetch_team_stats(self, team_id: int, season: int) -> Dict[str, Any]:
        """Fetch team stats for a specific season."""
        url = f"{self.mlb_base}/teams/{team_id}/stats"
        params = {
            'season': season,
            'group': 'hitting',
            'stats': 'season'
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._parse_team_stats(data)
            return {}

    def _should_fallback_to_previous_year(self, stats: Dict[str, Any]) -> bool:
        """Determine if we should fallback to previous year data."""
        return not stats or stats.get('games_played', 0) == 0

    def _merge_team_data(self, standings: Dict[str, Any], stats: Dict[str, Any], 
                        current_year: int) -> Dict[str, Any]:
        """Merge standings and stats data, handling offseason cases."""
        merged = {**standings, **stats}
        
        # Handle offseason case
        if self._is_offseason_data(merged):
            if current_year == datetime.now().year:
                merged['note'] = 'Offseason - no current season data available.'
            else:
                merged['note'] = 'No data available for this season.'
        
        return merged

    def _is_offseason_data(self, data: Dict[str, Any]) -> bool:
        """Check if the data indicates offseason (no games played and no wins)."""
        return (not data or 
                (data.get('games_played', 0) == 0 and data.get('wins', 0) == 0))

    async def _get_team_standings(self, team_id: int, season: int) -> Dict[str, Any]:
        """Get win/loss records from MLB standings endpoint."""
        try:
            url = f"{self.mlb_base}/standings"
            params = {
                'leagueId': '103,104',  # AL and NL
                'season': season,
                'standingsTypes': 'regularSeason',
                'fields': ('records,team,id,name,wins,losses,runDifferential,'
                           'divisionRank,leagueRank,divisionGamesBack,'
                           'leagueGamesBack,elimNumber,clinched,divisionRecord,'
                           'leagueRecord,home,away')
            }
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    assert data is not None, "Expected non-None data before calling .get()"
                    # Traverse to find the team
                    for record in data.get('records', []):
                        assert record is not None, "Expected non-None data before calling .get()"
                        for teamrec in record.get('teamRecords', []):
                            assert teamrec is not None, "Expected non-None data before calling .get()"
                            team = teamrec.get('team', {})
                            assert team is not None, "Expected non-None data before calling .get()"
                            if team.get('id') == team_id:
                                return {
                                    'wins': teamrec.get('wins', 0),
                                    'losses': teamrec.get('losses', 0),
                                    'win_pct': teamrec.get('winPercentage', 0),
                                    'games_back': teamrec.get('divisionGamesBack', 0),
                                    'division_rank': teamrec.get('divisionRank', 0),
                                    'league_rank': teamrec.get('leagueRank', 0),
                                    'run_differential': teamrec.get('runDifferential', 0),
                                    'home_record': teamrec.get('home', {}),
                                    'away_record': teamrec.get('away', {})
                                }
                return {}
        except Exception as e:
            logger.error(f"Error getting team standings: {e}")
            return {}

    async def _get_weather_data(self, city: str) -> Dict[str, Any]:
        """Get weather data from OpenWeatherMap API with fallback."""
        try:
            api_key = os.getenv('OPENWEATHER_API_KEY')
            if not api_key:
                return self._get_mock_weather(city)

            url = self.weather_api
            params = {
                'q': city,
                'appid': api_key,
                'units': 'imperial'
            }

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    assert data is not None, "Expected non-None data before calling .get()"
                    main_data = data.get('main', {})
                    wind_data = data.get('wind', {})
                    weather_data = data.get('weather', [{}])
                    assert main_data is not None, "Expected non-None data before calling .get()"
                    assert wind_data is not None, "Expected non-None data before calling .get()"
                    assert weather_data is not None and len(weather_data) > 0, "Expected non-None data before calling .get()"
                    return {
                        'temperature': main_data.get('temp'),
                        'humidity': main_data.get('humidity'),
                        'pressure': main_data.get('pressure'),
                        'wind_speed': wind_data.get('speed'),
                        'wind_direction': self._get_wind_direction(
                            wind_data.get('deg', 0)),
                        'condition': weather_data[0].get('description', 'Unknown'),
                        'source': 'OpenWeatherMap'
                    }
                else:
                    logger.warning(f"Weather API error: {response.status}")
                    return self._get_mock_weather(city)

        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            return self._get_mock_weather(city)

    def _get_mock_weather(self, city: str) -> Dict[str, Any]:
        """Get mock weather data as fallback."""
        return {
            'temperature': 72,
            'humidity': 65,
            'pressure': 30.1,
            'wind_speed': 8,
            'wind_direction': 'SW',
            'condition': 'Partly Cloudy',
            'source': 'Mock Data'
        }

    def _get_wind_direction(self, degrees: float) -> str:
        """Convert wind degrees to cardinal direction."""
        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                      'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        index = round(degrees / 22.5) % 16
        return directions[index]

    async def _get_live_scores(self) -> List[Dict[str, Any]]:
        """Get live scores for today's games."""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            url = f"{self.mlb_base}/schedule"
            params = {
                'date': today,
                'sportId': 1,
                'fields': 'dates,games,gamePk,gameDate,status,teams,away,home,team,id,name,score'
            }

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_live_scores(data)
                else:
                    logger.warning(f"Live scores API error: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Error getting live scores: {e}")
            return []

    def _parse_team_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse team statistics from MLB API response."""
        try:
            assert data is not None, "Expected non-None data before calling .get()"
            stats = data.get('stats', [])
            if not stats:
                return {}

            # Look for hitting stats
            for stat_group in stats:
                assert stat_group is not None, "Expected non-None data before calling .get()"
                group_data = stat_group.get('group', {})
                assert group_data is not None, "Expected non-None data before calling .get()"
                if group_data.get('displayName') == 'hitting':
                    splits = stat_group.get('splits', [])
                    if splits:
                        assert splits[0] is not None, "Expected non-None data before calling .get()"
                        stat = splits[0].get('stat', {})
                        assert stat is not None, "Expected non-None data before calling .get()"
                        return {
                            'games_played': stat.get('gamesPlayed', 0),
                            'runs': stat.get('runs', 0),
                            'hits': stat.get('hits', 0),
                            'doubles': stat.get('doubles', 0),
                            'triples': stat.get('triples', 0),
                            'home_runs': stat.get('homeRuns', 0),
                            'rbis': stat.get('rbi', 0),
                            'walks': stat.get('baseOnBalls', 0),
                            'strikeouts': stat.get('strikeOuts', 0),
                            'batting_avg': stat.get('avg', 0),
                            'on_base_pct': stat.get('obp', 0),
                            'slugging_pct': stat.get('slg', 0),
                            'ops': stat.get('ops', 0)
                        }
            return {}

        except Exception as e:
            logger.error(f"Error parsing team stats: {e}")
            return {}

    def _parse_live_scores(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse live scores from MLB API response."""
        try:
            games = []
            dates = data.get('dates', [])
            if dates:
                for game in dates[0].get('games', []):
                    away_team = game.get('teams', {}).get('away', {})
                    home_team = game.get('teams', {}).get('home', {})
                    games.append({
                        'game_pk': game.get('gamePk'),
                        'status': game.get('status', {}).get('detailedState', 'Unknown'),
                        'away_team': away_team.get('team', {}).get('name', 'Unknown'),
                        'away_score': away_team.get('score', 0),
                        'home_team': home_team.get('team', {}).get('name', 'Unknown'),
                        'home_score': home_team.get('score', 0)
                    })
            return games

        except Exception as e:
            logger.error(f"Error parsing live scores: {e}")
            return []

    def _find_today_game(self, games: List[Dict[str, Any]], team1_abbr: str,
                         team2_abbr: str) -> Optional[Dict[str, Any]]:
        """Find if the specified teams are playing today."""
        try:
            for game in games:
                away_team = game.get('away_team', '')
                home_team = game.get('home_team', '')

                # Check if either team matches
                if (team1_abbr in away_team or team1_abbr in home_team) and \
                   (team2_abbr in away_team or team2_abbr in home_team):
                    return game
            return None

        except Exception as e:
            logger.error(f"Error finding today's game: {e}")
            return None

    async def close(self):
        """Close the scraper session"""
        if self.session:
            await self.session.close()

    async def get_live_game_updates(self, game_id: Optional[str] = None) -> Dict[str, Any]:
        """Get real-time updates for live games."""
        try:
            if not self.session:
                await self.initialize()

            # Get live scores first
            live_scores = await self._get_live_scores()

            if not live_scores:
                return {'error': 'No live games found'}

            # If specific game_id provided, find that game
            if game_id:
                for game in live_scores:
                    if str(game.get('game_pk')) == str(game_id):
                        detailed_game = await self._get_detailed_game_state(game)
                        return {
                            'game': detailed_game,
                            'live_update': self._format_live_update(detailed_game)
                        }
                return {'error': f'Game {game_id} not found in live games'}

            # Otherwise, return updates for all live games
            live_updates = []
            for game in live_scores:
                if game.get('status') in ['Live', 'In Progress']:
                    detailed_game = await self._get_detailed_game_state(game)
                    live_updates.append({
                        'game': detailed_game,
                        'live_update': self._format_live_update(detailed_game)
                    })

            return {
                'live_games': live_updates,
                'total_live': len(live_updates)
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

    def _parse_detailed_game_state(self, data: Dict[str, Any],
                                   basic_game: Dict[str, Any]) -> Dict[str, Any]:
        """Parse detailed game state from MLB API response."""
        try:
            game_data = data.get('gameData', {})
            live_data = data.get('liveData', {})

            # Get current inning info
            plays = live_data.get('plays', {})
            current_play = plays.get('currentPlay', {})
            all_plays = plays.get('allPlays', [])

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

    def _determine_game_situation(self, current_play: Dict[str, Any],
                                  all_plays: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Determine the current game situation from live data."""
        try:
            situation = {
                'inning': current_play.get('about', {}).get('inning', 0),
                'inning_state': current_play.get('about', {}).get('inningState', 'Unknown'),
                'outs': current_play.get('count', {}).get('outs', 0),
                'balls': current_play.get('count', {}).get('balls', 0),
                'strikes': current_play.get('count', {}).get('strikes', 0),
                'bases': [False, False, False],  # 1B, 2B, 3B
                'batter': current_play.get('matchup', {}).get('batter', {}).get('fullName', 'Unknown'),
                'pitcher': current_play.get('matchup', {}).get('pitcher', {}).get('fullName', 'Unknown'),
                'home_team': current_play.get('teams', {}).get('home', {}).get('team', {}).get('name', 'Unknown'),
                'away_team': current_play.get('teams', {}).get('away', {}).get('team', {}).get('name', 'Unknown')
            }

            # Determine base situation from recent plays
            recent_plays = all_plays[-10:] if len(all_plays) > 10 else all_plays
            for play in reversed(recent_plays):
                if play.get('result', {}).get('event') in ['Single', 'Double', 'Triple', 'Walk', 'Hit By Pitch']:
                    # This is a simplified base tracking - in reality would need more complex logic
                    break

            return situation

        except Exception as e:
            logger.error(f"Error determining game situation: {e}")
            return {}

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

    def _extract_live_game_data(self, boxscore: Dict[str, Any]) -> Dict[str, Any]:
        """Extract live game data from boxscore."""
        try:
            game_data = {
                'status': boxscore.get('status', {}).get('detailedState', 'Unknown'),
                'current_inning': boxscore.get('currentInning', 0),
                'inning_state': boxscore.get('inningState', 'Unknown'),
                'home_score': 0,
                'away_score': 0,
                'home_hits': 0,
                'away_hits': 0,
                'home_errors': 0,
                'away_errors': 0,
                'last_play': None,
                'game_situation': {}
            }

            # Extract team data
            home_team = boxscore.get('teams', {}).get('home', {})
            away_team = boxscore.get('teams', {}).get('away', {})

            if home_team:
                game_data['home_score'] = home_team.get('score', 0)
                game_data['home_hits'] = home_team.get('hits', 0)
                game_data['home_errors'] = home_team.get('errors', 0)

            if away_team:
                game_data['away_score'] = away_team.get('score', 0)
                game_data['away_hits'] = away_team.get('hits', 0)
                game_data['away_errors'] = away_team.get('errors', 0)

            # Extract live feed data
            live_data = boxscore.get('liveData', {})
            plays = live_data.get('plays', {}).get('allPlays', [])
            current_play = live_data.get('plays', {}).get('currentPlay', {})

            if current_play:
                game_data['last_play'] = current_play.get('result', {}).get('description', 'No play data')
                game_data['game_situation'] = self._determine_game_situation(current_play, plays)

            return game_data

        except Exception as e:
            logger.error(f"Error extracting live game data: {e}")
            return {}

    def _format_live_update(self, game_data: Dict[str, Any]) -> str:
        """Format live game data for display."""
        try:
            if not game_data or game_data.get('status') == 'Final':
                return "Game is final or no live data available"

            status = game_data.get('status', 'Unknown')
            inning = game_data.get('current_inning', 0)
            inning_state = game_data.get('inning_state', 'Unknown')
            home_score = game_data.get('home_score', 0)
            away_score = game_data.get('away_score', 0)
            home_hits = game_data.get('home_hits', 0)
            away_hits = game_data.get('away_hits', 0)

            update = "⚾ **LIVE UPDATE** ⚾\n\n"
            update += f"**Status:** {status}\n"
            update += f"**Inning:** {inning} ({inning_state})\n"
            update += f"**Score:** {away_score} - {home_score}\n"
            update += f"**Hits:** {away_hits} - {home_hits}\n"

            last_play = game_data.get('last_play')
            if last_play:
                update += f"\n**Last Play:** {last_play}\n"

            situation = game_data.get('game_situation', {})
            if situation:
                outs = situation.get('outs', 0)
                balls = situation.get('balls', 0)
                strikes = situation.get('strikes', 0)
                batter = situation.get('batter', 'Unknown')
                pitcher = situation.get('pitcher', 'Unknown')

                update += f"\n**Current:** {balls}-{strikes} count, {outs} outs\n"
                update += f"**Batter:** {batter}\n"
                update += f"**Pitcher:** {pitcher}\n"

            return update

        except Exception as e:
            logger.error(f"Error formatting live update: {e}")
            return "Error formatting live update"
