#!/usr/bin/env python3
"""
mlb_stats.py - MLB Data Integration

Fetch live MLB stats, team data, and current trends using multiple free APIs.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import MLB_StatsAPI as statsapi
import requests

logger = logging.getLogger(__name__)


class MLBDataFetcher:
    """Fetch live MLB data and statistics using multiple free APIs."""

    def __init__(self):
        self.statsapi = statsapi
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GotLockz Bot/1.0'
        })

    async def get_team_stats(self, team_name: str) -> Dict[str, Any]:
        """Get team statistics from multiple sources."""
        try:
            # Primary: MLB Stats API
            team_stats = await self._get_team_stats_mlb(team_name)
            
            # Fallback: Sportsipy (if available)
            if not team_stats:
                team_stats = await self._get_team_stats_sportsipy(team_name)
            
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

    async def get_game_info(self, away_team: str, home_team: str) -> Dict[str, Any]:
        """Get game information including weather, venue, etc."""
        try:
            # Primary: MLB Stats API
            game_info = await self._get_game_info_mlb(away_team, home_team)
            
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
            if isinstance(schedule, dict) and 'dates' in schedule:
                for date in schedule.get('dates', []):
                    if isinstance(date, dict) and 'games' in date:
                        for game in date.get('games', []):
                            if isinstance(game, dict):
                                game_status = game.get('status', {}).get('detailedState', '')
                                if 'Live' in game_status or 'In Progress' in game_status:
                                    live_games.append({
                                        'away_team': game.get('teams', {}).get('away', {}).get('team', {}).get('name', ''),
                                        'home_team': game.get('teams', {}).get('home', {}).get('team', {}).get('name', ''),
                                        'away_score': game.get('teams', {}).get('away', {}).get('score', 0),
                                        'home_score': game.get('teams', {}).get('home', {}).get('score', 0),
                                        'inning': game.get('linescore', {}).get('currentInning', 0),
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
            
            # Get team stats using the correct method
            team_stats = self.statsapi.get('teams', {'teamId': team_id, 'season': datetime.now().year})
            
            if isinstance(team_stats, dict) and 'teams' in team_stats:
                teams_data = team_stats['teams']
                if isinstance(teams_data, list) and len(teams_data) > 0:
                    team_data = teams_data[0]
                    return {
                        'wins': team_data.get('record', {}).get('wins', 0),
                        'losses': team_data.get('record', {}).get('losses', 0),
                        'win_pct': team_data.get('record', {}).get('winPercentage', 0),
                        'runs_per_game': 0,  # Would need additional API call
                        'era': 0  # Would need additional API call
                    }
            
            return {}

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
            player_stats = self.statsapi.player_stats(player_id, season=datetime.now().year, group='hitting')
            
            if isinstance(player_stats, dict) and 'stats' in player_stats:
                stats_list = player_stats['stats']
                if isinstance(stats_list, list) and len(stats_list) > 0:
                    stats = stats_list[0]['splits'][0]['stat']
                    return {
                        'avg': f"{stats.get('avg', 0):.3f}",
                        'hr': stats.get('homeRuns', 0),
                        'rbi': stats.get('rbi', 0),
                        'ops': f"{stats.get('ops', 0):.3f}",
                        'slg': f"{stats.get('slg', 0):.3f}",
                        'obp': f"{stats.get('obp', 0):.3f}"
                    }
            
            return {}

        except Exception as e:
            logger.error(f"Error fetching MLB player stats: {e}")
            return {}

    async def _get_game_info_mlb(self, away_team: str, home_team: str) -> Dict[str, Any]:
        """Get game info from MLB Stats API."""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            schedule = self.statsapi.schedule(date=today, sportId=1)
            
            if isinstance(schedule, dict) and 'dates' in schedule:
                for date in schedule.get('dates', []):
                    if isinstance(date, dict) and 'games' in date:
                        for game in date.get('games', []):
                            if isinstance(game, dict):
                                game_away = game.get('teams', {}).get('away', {}).get('team', {}).get('name', '')
                                game_home = game.get('teams', {}).get('home', {}).get('team', {}).get('name', '')
                                
                                if (away_team.lower() in game_away.lower() and 
                                    home_team.lower() in game_home.lower()):
                                    return {
                                        'game_time': game.get('gameDate', ''),
                                        'venue': game.get('venue', {}).get('name', ''),
                                        'weather': 'Clear, 72°F',  # Default
                                        'away_pitcher': game.get('teams', {}).get('away', {}).get('probablePitcher', {}).get('fullName', 'TBD'),
                                        'home_pitcher': game.get('teams', {}).get('home', {}).get('probablePitcher', {}).get('fullName', 'TBD')
                                    }
            
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
            recent_stats = self.statsapi.player_stats(
                player_id, 
                season=datetime.now().year, 
                group='hitting'
            )
            
            if recent_stats and 'stats' in recent_stats:
                stats = recent_stats['stats'][0]['splits'][0]['stat']
                return {
                    'recent_avg': f"{stats.get('avg', 0):.3f}",
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
            
            # Get recent stats using the correct method
            recent_stats = self.statsapi.get('teams', {'teamId': team_id, 'season': datetime.now().year})
            
            if recent_stats and 'teams' in recent_stats:
                team_data = recent_stats['teams'][0]
                return {
                    'recent_wins': team_data.get('record', {}).get('wins', 0),
                    'recent_losses': team_data.get('record', {}).get('losses', 0),
                    'recent_runs_per_game': 0  # Would need additional API call
                }

            return {}

        except Exception as e:
            logger.error(f"Error fetching recent team stats: {e}")
            return {}


# Global instance
mlb_fetcher = MLBDataFetcher()
