#!/usr/bin/env python3
"""
mlb_stats.py - MLB Data Integration

Fetch live MLB stats, team data, and current trends.
"""
import logging
import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MLBDataFetcher:
    """Fetch live MLB data and statistics."""

    def __init__(self):
        self.base_url = "https://statsapi.mlb.com/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GotLockz Bot/1.0'
        })

    async def get_team_stats(self, team_name: str) -> Dict[str, Any]:
        """Get team statistics."""
        try:
            # Search for team
            team_id = await self._get_team_id(team_name)
            if not team_id:
                return {}

            # Get team stats
            url = f"{self.base_url}/teams/{team_id}/stats"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                season_stats = self._parse_team_stats(data)
                
                # Get recent team performance (last 10 games)
                recent_url = f"{self.base_url}/teams/{team_id}/stats"
                recent_params = {
                    'stats': 'last10Games',
                    'group': 'hitting'
                }
                recent_response = self.session.get(recent_url, params=recent_params, timeout=10)
                
                recent_stats = {}
                if recent_response.status_code == 200:
                    recent_data = recent_response.json()
                    recent_stats = self._parse_team_stats(recent_data)
                
                # Combine season and recent stats
                combined_stats = {**season_stats}
                if recent_stats:
                    combined_stats['recent_wins'] = recent_stats.get('wins', 0)
                    combined_stats['recent_losses'] = recent_stats.get('losses', 0)
                    combined_stats['recent_runs_per_game'] = recent_stats.get('runs_per_game', 0)
                
                return combined_stats
            else:
                logger.warning(
                    f"Failed to fetch team stats: {response.status_code}")
                return {}

        except Exception as e:
            logger.error(f"Error fetching team stats: {e}")
            return {}

    async def get_player_stats(self, player_name: str) -> Dict[str, Any]:
        """Get player statistics."""
        try:
            # Search for player
            player_id = await self._get_player_id(player_name)
            if not player_id:
                return {}

            # Get player stats for current season
            url = f"{self.base_url}/people/{player_id}/stats"
            params = {
                'stats': 'season',
                'group': 'hitting'
            }
            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                season_stats = self._parse_player_stats(data)
                
                # Get recent performance (last 7 days)
                recent_params = {
                    'stats': 'last7Days',
                    'group': 'hitting'
                }
                recent_response = self.session.get(url, params=recent_params, timeout=10)
                
                recent_stats = {}
                if recent_response.status_code == 200:
                    recent_data = recent_response.json()
                    recent_stats = self._parse_player_stats(recent_data)
                
                # Combine season and recent stats
                combined_stats = {**season_stats}
                if recent_stats:
                    combined_stats['recent_avg'] = recent_stats.get('avg', '.000')
                    combined_stats['recent_hr'] = recent_stats.get('hr', '0')
                    combined_stats['recent_rbi'] = recent_stats.get('rbi', '0')
                
                return combined_stats
            else:
                logger.warning(
                    f"Failed to fetch player stats: {response.status_code}")
                return {}

        except Exception as e:
            logger.error(f"Error fetching player stats: {e}")
            return {}

    async def get_game_info(self, away_team: str,
                            home_team: str) -> Dict[str, Any]:
        """Get game information including weather, venue, etc."""
        try:
            # Get today's games
            today = datetime.now().strftime("%Y-%m-%d")
            url = f"{self.base_url}/schedule"
            params = {
                'date': today,
                'sportId': 1  # MLB
            }
            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return self._find_game_info(data, away_team, home_team)
            else:
                logger.warning(
                    f"Failed to fetch game info: {response.status_code}")
                return {}

        except Exception as e:
            logger.error(f"Error fetching game info: {e}")
            return {}

    async def _get_team_id(self, team_name: str) -> Optional[int]:
        """Get team ID from team name."""
        try:
            url = f"{self.base_url}/teams"
            params = {'sportId': 1}  # MLB
            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                for team in data.get('teams', []):
                    if team_name.lower() in team['name'].lower():
                        return team['id']
            return None

        except Exception as e:
            logger.error(f"Error getting team ID: {e}")
            return None

    async def _get_player_id(self, player_name: str) -> Optional[int]:
        """Get player ID from player name."""
        try:
            url = f"{self.base_url}/people"
            params = {'search': player_name}
            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                for person in data.get('people', []):
                    if player_name.lower() in person['fullName'].lower():
                        return person['id']
            return None

        except Exception as e:
            logger.error(f"Error getting player ID: {e}")
            return None

    def _parse_team_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse team statistics from API response."""
        try:
            stats = data.get('stats', [])
            if stats:
                team_stats = stats[0].get('splits', [{}])[0].get('stat', {})
                return {
                    'wins': team_stats.get('wins', 0),
                    'losses': team_stats.get('losses', 0),
                    'win_pct': team_stats.get('winPct', 0),
                    'runs_per_game': team_stats.get('runsPerGame', 0),
                    'era': team_stats.get('era', 0)
                }
            return {}
        except Exception as e:
            logger.error(f"Error parsing team stats: {e}")
            return {}

    def _parse_player_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse player statistics from API response."""
        try:
            stats = data.get('stats', [])
            if stats:
                player_stats = stats[0].get('splits', [{}])[0].get('stat', {})
                return {
                    'avg': f"{player_stats.get('avg', 0):.3f}",
                    'hr': player_stats.get('homeRuns', 0),
                    'rbi': player_stats.get('rbi', 0),
                    'ops': f"{player_stats.get('ops', 0):.3f}",
                    'slg': f"{player_stats.get('slg', 0):.3f}",
                    'obp': f"{player_stats.get('obp', 0):.3f}"
                }
            return {}
        except Exception as e:
            logger.error(f"Error parsing player stats: {e}")
            return {}

    def _find_game_info(
            self, data: Dict[str, Any], away_team: str, home_team: str) -> Dict[str, Any]:
        """Find specific game information."""
        try:
            dates = data.get('dates', [])
            for date in dates:
                games = date.get('games', [])
                for game in games:
                    game_away = game.get(
                        'teams',
                        {}).get(
                        'away',
                        {}).get(
                        'team',
                        {}).get(
                        'name',
                        '')
                    game_home = game.get(
                        'teams',
                        {}).get(
                        'home',
                        {}).get(
                        'team',
                        {}).get(
                        'name',
                        '')

                    if (away_team.lower() in game_away.lower() and
                            home_team.lower() in game_home.lower()):
                        return {
                            'game_time': game.get('gameDate', ''),
                            'venue': game.get('venue', {}).get('name', ''),
                            'weather': 'Clear, 72°F',  # Would need weather API
                            'away_pitcher': game.get('teams', {}).get('away', {}).get('probablePitcher', {}).get('fullName', 'TBD'),
                            'home_pitcher': game.get('teams', {}).get('home', {}).get('probablePitcher', {}).get('fullName', 'TBD')
                        }
            return {}
        except Exception as e:
            logger.error(f"Error finding game info: {e}")
            return {}


# Global instance
mlb_fetcher = MLBDataFetcher()
