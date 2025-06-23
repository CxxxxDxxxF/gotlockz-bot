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

logger = logging.getLogger(__name__)


class MLBDataFetcher:
    """Fetch live MLB data and statistics using multiple free APIs."""

    def __init__(self):
        self.statsapi = statsapi
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GotLockz Bot/1.0'
        })
        
        # ESPN API endpoints
        self.espn_base_url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb"
        
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
        """Get team statistics from multiple sources."""
        try:
            resolved_name = self._resolve_team_name(team_name)
            # Primary: MLB Stats API
            team_stats = await self._get_team_stats_mlb(resolved_name)
            
            # Fallback: Sportsipy (if available)
            if not team_stats:
                team_stats = await self._get_team_stats_sportsipy(resolved_name)
            
            return team_stats

        except Exception as e:
            logger.error(f"Error fetching team stats: {e}")
            return {}

    async def get_player_stats(self, player_name: str) -> Dict[str, Any]:
        """Get player statistics from multiple sources."""
        try:
            # Primary: MLB Stats API
            player_stats = await self._get_player_stats_mlb(player_name)
            
            # Fallback: Sportsipy (if available)
            if not player_stats:
                player_stats = await self._get_player_stats_sportsipy(player_name)
            
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
            # First, get today's games from ESPN
            today = datetime.now().strftime("%Y%m%d")
            url = f"{self.espn_base_url}/scoreboard"
            params = {
                'dates': today,
                'limit': 50
            }
            
            response = self.session.get(url, params=params, timeout=10)
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
            
            response = self.session.get(url, timeout=10)
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
            
        except Exception as e:
            logger.error(f"Error fetching ESPN team stats: {e}")
            return {}


# Global instance
mlb_fetcher = MLBDataFetcher()
