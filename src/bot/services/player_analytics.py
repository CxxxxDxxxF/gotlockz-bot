"""
Simplified Player Analytics Service - MLB player statistics and analysis
"""
import logging
import asyncio
import json
import os
from typing import Dict, Any, Optional, List
import aiohttp
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PlayerAnalyticsService:
    """Service for advanced player analytics and matchup analysis."""

    def __init__(self):
        """Initialize player analytics service."""
        self.session = None
        self.mlb_base = "https://statsapi.mlb.com/api/v1"
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.player_map = {}
        self.mlb_team_ids = [
            108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 133, 134,
            135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 158
        ]
        self._load_player_mapping()
        
    def _load_player_mapping(self):
        """Load the player name to ID mapping."""
        try:
            # Try multiple possible paths for the mapping file
            possible_paths = [
                os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'mlb_player_map.json'),
                os.path.join(os.path.dirname(__file__), '..', '..', '..', 'mlb_player_map.json'),
                'mlb_player_map.json'
            ]
            
            mapping_file = None
            for path in possible_paths:
                if os.path.exists(path):
                    mapping_file = path
                    break
            
            if mapping_file:
                with open(mapping_file, 'r') as f:
                    self.player_map = json.load(f)
                logger.info(f"Loaded {len(self.player_map)} players from mapping: {mapping_file}")
            else:
                logger.warning("Player mapping file not found in any of these paths:")
                for path in possible_paths:
                    logger.warning(f"  - {path}")
        except Exception as e:
            logger.error(f"Error loading player mapping: {e}")
        
    async def initialize(self):
        """Initialize the HTTP session."""
        try:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={'User-Agent': 'GotLockzBot/2.0'}
            )
            logger.info("Player analytics service initialized")
        except Exception as e:
            logger.error(f"Error initializing player analytics service: {e}")
    
    async def get_player_analytics(self, player_name: str, team_name: str) -> Dict[str, Any]:
        """Get comprehensive player analytics."""
        try:
            if not self.session:
                await self.initialize()

            # Get player ID
            player_id = await self._get_player_id(player_name, team_name)
            if not player_id:
                return {'error': f'Player {player_name} not found'}

            # Get player stats
            stats = await self._get_player_stats(player_id)
            if not stats:
                return {'error': f'No stats found for {player_name}'}

            # Get recent performance
            recent_performance = await self._get_recent_performance(player_id)

            # Get matchup analysis
            matchup_analysis = await self._get_matchup_analysis(player_id, team_name)

            return {
                'player_name': player_name,
                'team': team_name,
                'stats': stats,
                'recent_performance': recent_performance,
                'matchup_analysis': matchup_analysis,
                'last_updated': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting player analytics: {e}")
            return {'error': f'Error analyzing {player_name}: {str(e)}'}
    
    async def get_matchup_analysis(self, team1: str, team2: str) -> Dict[str, Any]:
        """Get detailed matchup analysis between two teams."""
        try:
            if not self.session:
                await self.initialize()

            # Get team IDs
            team1_id = await self._get_team_id(team1)
            team2_id = await self._get_team_id(team2)

            if not team1_id or not team2_id:
                return {'error': 'One or both teams not found'}

            # Get team stats
            team1_stats = await self._get_team_stats(team1_id)
            team2_stats = await self._get_team_stats(team2_id)

            # Get head-to-head data
            h2h_data = await self._get_head_to_head(team1_id, team2_id)

            # Get key players
            key_players = await self._get_key_players(team1_id, team2_id)

            return {
                'team1': {'name': team1, 'stats': team1_stats},
                'team2': {'name': team2, 'stats': team2_stats},
                'head_to_head': h2h_data,
                'key_players': key_players,
                'analysis': self._generate_matchup_analysis(team1_stats, team2_stats, h2h_data),
                'last_updated': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting matchup analysis: {e}")
            return {'error': f'Error analyzing matchup: {str(e)}'}
    
    async def _get_player_id(self, player_name: str, team_name: str) -> Optional[int]:
        """Get player ID from MLB API."""
        try:
            # Search for player
            search_url = f"{self.mlb_base}/people"
            params = {
                'search': player_name,
                'sportIds': 1,  # MLB
                'fields': 'people,id,fullName,currentTeam,id,name'
            }

            async with self.session.get(search_url, params=params) as response:
                if response.status != 200:
                    return None

                data = await response.json()
                assert data is not None, "Expected non-None data before calling .get()"
                people = data.get('people', [])

                for person in people:
                    assert person is not None, "Expected non-None data before calling .get()"
                    if person.get('fullName', '').lower() == player_name.lower():
                        current_team = person.get('currentTeam', {})
                        assert current_team is not None, "Expected non-None data before calling .get()"
                        if current_team.get('name', '').lower() == team_name.lower():
                            return person.get('id')

                # If exact match not found, return first match
                if people:
                    assert people[0] is not None, "Expected non-None data before calling .get()"
                    return people[0].get('id')

                return None

        except Exception as e:
            logger.error(f"Error getting player ID: {e}")
            return None
    
    async def _get_player_stats(self, player_id: int) -> Dict[str, Any]:
        """Get player statistics."""
        try:
            # Get current season stats
            stats_url = f"{self.mlb_base}/people/{player_id}/stats"
            params = {
                'stats': 'season',
                'group': 'hitting,pitching',
                'season': datetime.now().year,
                'fields': 'stats,splits,stat,group,type,displayName,value'
            }

            async with self.session.get(stats_url, params=params) as response:
                if response.status != 200:
                    return {}

                data = await response.json()
                assert data is not None, "Expected non-None data before calling .get()"
                stats = data.get('stats', [])

                result = {}
                for stat_group in stats:
                    assert stat_group is not None, "Expected non-None data before calling .get()"
                    group = stat_group.get('group', {}).get('displayName', 'Unknown')
                    splits = stat_group.get('splits', [])
                    if splits:
                        assert splits[0] is not None, "Expected non-None data before calling .get()"
                        result[group] = splits[0].get('stat', {})

                return result

        except Exception as e:
            logger.error(f"Error getting player stats: {e}")
            return {}
    
    async def _get_recent_performance(self, player_id: int) -> Dict[str, Any]:
        """Get player's recent performance."""
        try:
            # Get last 10 games
            stats_url = f"{self.mlb_base}/people/{player_id}/stats"
            params = {
                'stats': 'gameLog',
                'group': 'hitting,pitching',
                'season': datetime.now().year,
                'limit': 10,
                'fields': 'stats,splits,stat,group,type,displayName,value,date'
            }

            async with self.session.get(stats_url, params=params) as response:
                if response.status != 200:
                    return {}

                data = await response.json()
                assert data is not None, "Expected non-None data before calling .get()"
                stats = data.get('stats', [])

                recent_games = []
                for stat_group in stats:
                    assert stat_group is not None, "Expected non-None data before calling .get()"
                    splits = stat_group.get('splits', [])
                    for split in splits:
                        assert split is not None, "Expected non-None data before calling .get()"
                        recent_games.append({
                            'date': split.get('date'),
                            'stats': split.get('stat', {})
                        })

                return {'recent_games': recent_games[:10]}

        except Exception as e:
            logger.error(f"Error getting recent performance: {e}")
            return {}
    
    async def _get_matchup_analysis(self, player_id: int, team_name: str) -> Dict[str, Any]:
        """Get player's performance against specific team."""
        try:
            # Get vs team stats
            stats_url = f"{self.mlb_base}/people/{player_id}/stats"
            params = {
                'stats': 'vsTeam',
                'group': 'hitting,pitching',
                'season': datetime.now().year,
                'fields': 'stats,splits,stat,group,type,displayName,value,opponent,id,name'
            }

            async with self.session.get(stats_url, params=params) as response:
                if response.status != 200:
                    return {}

                data = await response.json()
                assert data is not None, "Expected non-None data before calling .get()"
                stats = data.get('stats', [])

                for stat_group in stats:
                    assert stat_group is not None, "Expected non-None data before calling .get()"
                    splits = stat_group.get('splits', [])
                    for split in splits:
                        assert split is not None, "Expected non-None data before calling .get()"
                        opponent = split.get('opponent', {})
                        assert opponent is not None, "Expected non-None data before calling .get()"
                        if opponent.get('name', '').lower() == team_name.lower():
                            return split.get('stat', {})

                return {}

        except Exception as e:
            logger.error(f"Error getting matchup analysis: {e}")
            return {}
    
    async def _get_team_id(self, team_name: str) -> Optional[int]:
        """Get team ID from MLB API."""
        try:
            # Get all teams
            teams_url = f"{self.mlb_base}/teams"
            params = {
                'sportIds': 1,  # MLB
                'fields': 'teams,id,name'
            }

            async with self.session.get(teams_url, params=params) as response:
                if response.status != 200:
                    return None

                data = await response.json()
                assert data is not None, "Expected non-None data before calling .get()"
                teams = data.get('teams', [])

                for team in teams:
                    assert team is not None, "Expected non-None data before calling .get()"
                    if team.get('name', '').lower() == team_name.lower():
                        logger.info(f"Found MLB team '{team_name}' (matched '{team.get('name')}') with ID {team.get('id')}")
                        return team.get('id')

                return None

        except Exception as e:
            logger.error(f"Error getting team ID: {e}")
            return None
    
    async def _get_team_stats(self, team_id: int) -> Dict[str, Any]:
        """Get team statistics."""
        try:
            # Get team stats
            stats_url = f"{self.mlb_base}/teams/{team_id}/stats"
            params = {
                'stats': 'season',
                'season': datetime.now().year,
                'fields': 'stats,splits,stat,group,type,displayName,value'
            }

            async with self.session.get(stats_url, params=params) as response:
                if response.status != 200:
                    return {}

                data = await response.json()
                assert data is not None, "Expected non-None data before calling .get()"
                stats = data.get('stats', [])

                result = {}
                for stat_group in stats:
                    assert stat_group is not None, "Expected non-None data before calling .get()"
                    group = stat_group.get('group', {}).get('displayName', 'Unknown')
                    splits = stat_group.get('splits', [])
                    if splits:
                        assert splits[0] is not None, "Expected non-None data before calling .get()"
                        result[group] = splits[0].get('stat', {})

                return result

        except Exception as e:
            logger.error(f"Error getting team stats: {e}")
            return {}
    
    async def _get_head_to_head(self, team1_id: int, team2_id: int) -> Dict[str, Any]:
        """Get head-to-head data between teams."""
        try:
            # This would require more complex API calls to get historical matchups
            # For now, return basic structure
            return {
                'games_played': 0,
                'team1_wins': 0,
                'team2_wins': 0,
                'avg_runs_team1': 0,
                'avg_runs_team2': 0
            }

        except Exception as e:
            logger.error(f"Error getting head-to-head data: {e}")
            return {}
    
    async def _get_key_players(self, team1_id: int, team2_id: int) -> Dict[str, Any]:
        """Get key players for both teams."""
        try:
            # This would require roster API calls
            # For now, return basic structure
            return {
                'team1_key_players': [],
                'team2_key_players': []
            }

        except Exception as e:
            logger.error(f"Error getting key players: {e}")
            return {}
    
    def _generate_matchup_analysis(self, team1_stats: Dict, team2_stats: Dict, h2h_data: Dict) -> str:
        """Generate matchup analysis text."""
        try:
            analysis = "**Matchup Analysis:**\n\n"

            # Compare key stats
            if team1_stats and team2_stats:
                analysis += "**Key Statistics Comparison:**\n"
                # Add specific stat comparisons here
                analysis += "• Detailed stats comparison available\n\n"

            if h2h_data:
                analysis += "**Head-to-Head History:**\n"
                analysis += f"• Games played: {h2h_data.get('games_played', 0)}\n"
                analysis += f"• Team 1 wins: {h2h_data.get('team1_wins', 0)}\n"
                analysis += f"• Team 2 wins: {h2h_data.get('team2_wins', 0)}\n\n"

            analysis += "**Recommendation:** Consider recent form, pitching matchups, and weather conditions."

            return analysis

        except Exception as e:
            logger.error(f"Error generating matchup analysis: {e}")
            return "Unable to generate matchup analysis"
    
    async def close(self):
        """Close the HTTP session."""
        try:
            if self.session:
                await self.session.close()
        except Exception as e:
            logger.error(f"Error closing player analytics service: {e}") 