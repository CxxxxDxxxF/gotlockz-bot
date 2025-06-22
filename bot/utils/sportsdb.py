#!/usr/bin/env python3
"""
sportsdb.py - TheSportsDB API Integration

Fetch team logos, player images, and additional metadata from TheSportsDB.
"""
import logging
import requests
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class SportsDBAPI:
    """TheSportsDB API integration for team and player metadata."""

    def __init__(self):
        self.base_url = "https://www.thesportsdb.com/api/v1/json/3"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GotLockz Bot/1.0'
        })

    async def get_team_info(self, team_name: str) -> Dict[str, Any]:
        """Get comprehensive team information."""
        try:
            url = f"{self.base_url}/searchteams.php"
            params = {'t': team_name}
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and data.get('teams'):
                    teams = data['teams']
                    if isinstance(teams, list) and len(teams) > 0:
                        team = teams[0]
                        return {
                            'name': team.get('strTeam', ''),
                            'logo': team.get('strTeamBadge', ''),
                            'banner': team.get('strTeamBanner', ''),
                            'stadium': team.get('strStadium', ''),
                            'location': team.get('strLocation', ''),
                            'league': team.get('strLeague', ''),
                            'description': team.get('strDescriptionEN', ''),
                            'website': team.get('strWebsite', ''),
                            'facebook': team.get('strFacebook', ''),
                            'twitter': team.get('strTwitter', ''),
                            'instagram': team.get('strInstagram', ''),
                            'youtube': team.get('strYoutube', '')
                        }
            
            return {}

        except Exception as e:
            logger.error(f"Error fetching team info: {e}")
            return {}

    async def get_player_info(self, player_name: str) -> Dict[str, Any]:
        """Get comprehensive player information."""
        try:
            url = f"{self.base_url}/searchplayers.php"
            params = {'p': player_name}
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and data.get('player'):
                    players = data['player']
                    if isinstance(players, list) and len(players) > 0:
                        player = players[0]
                        return {
                            'name': player.get('strPlayer', ''),
                            'image': player.get('strThumb', ''),
                            'cutout': player.get('strCutout', ''),
                            'position': player.get('strPosition', ''),
                            'team': player.get('strTeam', ''),
                            'nationality': player.get('strNationality', ''),
                            'birth_date': player.get('dateBorn', ''),
                            'birth_place': player.get('strBirthLocation', ''),
                            'height': player.get('strHeight', ''),
                            'weight': player.get('strWeight', ''),
                            'description': player.get('strDescriptionEN', ''),
                            'website': player.get('strWebsite', ''),
                            'facebook': player.get('strFacebook', ''),
                            'twitter': player.get('strTwitter', ''),
                            'instagram': player.get('strInstagram', ''),
                            'youtube': player.get('strYoutube', '')
                        }
            
            return {}

        except Exception as e:
            logger.error(f"Error fetching player info: {e}")
            return {}

    async def get_team_logo(self, team_name: str) -> str:
        """Get team logo URL."""
        try:
            team_info = await self.get_team_info(team_name)
            return team_info.get('logo', '')

        except Exception as e:
            logger.error(f"Error fetching team logo: {e}")
            return ''

    async def get_player_image(self, player_name: str) -> str:
        """Get player image URL."""
        try:
            player_info = await self.get_player_info(player_name)
            return player_info.get('image', '')

        except Exception as e:
            logger.error(f"Error fetching player image: {e}")
            return ''

    async def search_teams(self, query: str) -> List[Dict[str, Any]]:
        """Search for teams by query."""
        try:
            url = f"{self.base_url}/searchteams.php"
            params = {'t': query}
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and data.get('teams'):
                    teams = data['teams']
                    if isinstance(teams, list):
                        return teams
            
            return []

        except Exception as e:
            logger.error(f"Error searching teams: {e}")
            return []

    async def search_players(self, query: str) -> List[Dict[str, Any]]:
        """Search for players by query."""
        try:
            url = f"{self.base_url}/searchplayers.php"
            params = {'p': query}
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and data.get('player'):
                    players = data['player']
                    if isinstance(players, list):
                        return players
            
            return []

        except Exception as e:
            logger.error(f"Error searching players: {e}")
            return []

    async def get_league_teams(self, league_name: str) -> List[Dict[str, Any]]:
        """Get all teams in a league."""
        try:
            url = f"{self.base_url}/search_all_teams.php"
            params = {'l': league_name}
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and data.get('teams'):
                    teams = data['teams']
                    if isinstance(teams, list):
                        return teams
            
            return []

        except Exception as e:
            logger.error(f"Error fetching league teams: {e}")
            return []

    async def get_team_players(self, team_name: str) -> List[Dict[str, Any]]:
        """Get all players on a team."""
        try:
            url = f"{self.base_url}/searchplayers.php"
            params = {'t': team_name}
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and data.get('player'):
                    players = data['player']
                    if isinstance(players, list):
                        return players
            
            return []

        except Exception as e:
            logger.error(f"Error fetching team players: {e}")
            return []


# Global instance
sportsdb_api = SportsDBAPI() 