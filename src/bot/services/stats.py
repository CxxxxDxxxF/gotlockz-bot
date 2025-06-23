"""
Stats Service - Live statistics and data fetching
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List
import aiohttp

logger = logging.getLogger(__name__)


class StatsService:
    """Service for fetching live statistics and data."""
    
    def __init__(self):
        self.session = None
        self.espn_base_url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb"
        self.mlb_base_url = "https://statsapi.mlb.com/api/v1"
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def get_live_stats(self, bet_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get live stats for betting data."""
        try:
            teams = bet_data.get('teams', [])
            if len(teams) < 2:
                return None
            
            # Fetch team stats
            team1_stats = await self.get_team_stats(teams[0])
            team2_stats = await self.get_team_stats(teams[1])
            
            if not team1_stats or not team2_stats:
                return None
            
            # Combine stats
            combined_stats = {
                'team1': team1_stats,
                'team2': team2_stats,
                'summary': f"{teams[0]} vs {teams[1]} stats loaded"
            }
            
            return combined_stats
            
        except Exception as e:
            logger.error(f"Error getting live stats: {e}")
            return None
    
    async def get_team_stats(self, team_name: str) -> Optional[Dict[str, Any]]:
        """Get team statistics."""
        try:
            session = await self._get_session()
            
            # Try ESPN API first
            stats = await self._get_espn_team_stats(session, team_name)
            if stats:
                return stats
            
            # Fallback to MLB API
            stats = await self._get_mlb_team_stats(session, team_name)
            if stats:
                return stats
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting team stats for {team_name}: {e}")
            return None
    
    async def get_player_stats(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Get player statistics."""
        try:
            session = await self._get_session()
            
            # Try ESPN API first
            stats = await self._get_espn_player_stats(session, player_name)
            if stats:
                return stats
            
            # Fallback to MLB API
            stats = await self._get_mlb_player_stats(session, player_name)
            if stats:
                return stats
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting player stats for {player_name}: {e}")
            return None
    
    async def get_live_scores(self) -> List[Dict[str, Any]]:
        """Get live game scores."""
        try:
            session = await self._get_session()
            
            # Try ESPN API
            games = await self._get_espn_live_scores(session)
            if games:
                return games
            
            # Fallback to MLB API
            games = await self._get_mlb_live_scores(session)
            if games:
                return games
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting live scores: {e}")
            return []
    
    async def _get_espn_team_stats(self, session: aiohttp.ClientSession, team_name: str) -> Optional[Dict[str, Any]]:
        """Get team stats from ESPN API."""
        try:
            # Get scoreboard to find team
            url = f"{self.espn_base_url}/scoreboard"
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                
                # Find team in events
                for event in data.get('events', []):
                    for team in event.get('competitions', [{}])[0].get('competitors', []):
                        if team_name.lower() in team.get('team', {}).get('name', '').lower():
                            stats = team.get('statistics', [])
                            return self._parse_espn_team_stats(stats)
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting ESPN team stats: {e}")
            return None
    
    async def _get_mlb_team_stats(self, session: aiohttp.ClientSession, team_name: str) -> Optional[Dict[str, Any]]:
        """Get team stats from MLB API."""
        try:
            # Get teams
            url = f"{self.mlb_base_url}/teams"
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                
                # Find team
                for team in data.get('teams', []):
                    if team_name.lower() in team.get('name', '').lower():
                        team_id = team.get('id')
                        return await self._get_mlb_team_stats_by_id(session, team_id)
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting MLB team stats: {e}")
            return None
    
    async def _get_mlb_team_stats_by_id(self, session: aiohttp.ClientSession, team_id: int) -> Optional[Dict[str, Any]]:
        """Get team stats by ID from MLB API."""
        try:
            url = f"{self.mlb_base_url}/teams/{team_id}/stats"
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                return self._parse_mlb_team_stats(data)
                
        except Exception as e:
            logger.error(f"Error getting MLB team stats by ID: {e}")
            return None
    
    async def _get_espn_player_stats(self, session: aiohttp.ClientSession, player_name: str) -> Optional[Dict[str, Any]]:
        """Get player stats from ESPN API."""
        try:
            # Search for player
            url = f"{self.espn_base_url}/athletes"
            params = {'search': player_name}
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                
                # Find player
                for athlete in data.get('athletes', []):
                    if player_name.lower() in athlete.get('fullName', '').lower():
                        athlete_id = athlete.get('id')
                        return await self._get_espn_player_stats_by_id(session, athlete_id)
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting ESPN player stats: {e}")
            return None
    
    async def _get_espn_player_stats_by_id(self, session: aiohttp.ClientSession, athlete_id: int) -> Optional[Dict[str, Any]]:
        """Get player stats by ID from ESPN API."""
        try:
            url = f"{self.espn_base_url}/athletes/{athlete_id}/stats"
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                return self._parse_espn_player_stats(data)
                
        except Exception as e:
            logger.error(f"Error getting ESPN player stats by ID: {e}")
            return None
    
    async def _get_mlb_player_stats(self, session: aiohttp.ClientSession, player_name: str) -> Optional[Dict[str, Any]]:
        """Get player stats from MLB API."""
        try:
            # Search for player
            url = f"{self.mlb_base_url}/people"
            params = {'search': player_name}
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                
                # Find player
                for person in data.get('people', []):
                    if player_name.lower() in person.get('fullName', '').lower():
                        person_id = person.get('id')
                        return await self._get_mlb_player_stats_by_id(session, person_id)
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting MLB player stats: {e}")
            return None
    
    async def _get_mlb_player_stats_by_id(self, session: aiohttp.ClientSession, person_id: int) -> Optional[Dict[str, Any]]:
        """Get player stats by ID from MLB API."""
        try:
            url = f"{self.mlb_base_url}/people/{person_id}/stats"
            params = {'stats': 'hitting'}
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                return self._parse_mlb_player_stats(data)
                
        except Exception as e:
            logger.error(f"Error getting MLB player stats by ID: {e}")
            return None
    
    async def _get_espn_live_scores(self, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """Get live scores from ESPN API."""
        try:
            url = f"{self.espn_base_url}/scoreboard"
            async with session.get(url) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                return self._parse_espn_live_scores(data)
                
        except Exception as e:
            logger.error(f"Error getting ESPN live scores: {e}")
            return []
    
    async def _get_mlb_live_scores(self, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """Get live scores from MLB API."""
        try:
            url = f"{self.mlb_base_url}/schedule"
            params = {'sportId': 1, 'date': 'today'}
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                return self._parse_mlb_live_scores(data)
                
        except Exception as e:
            logger.error(f"Error getting MLB live scores: {e}")
            return []
    
    def _parse_espn_team_stats(self, stats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse ESPN team statistics."""
        try:
            parsed_stats = {}
            
            for stat in stats:
                name = stat.get('name', '')
                value = stat.get('value', 0)
                
                if name == 'wins':
                    parsed_stats['wins'] = int(value)
                elif name == 'losses':
                    parsed_stats['losses'] = int(value)
                elif name == 'winPct':
                    parsed_stats['win_pct'] = float(value)
                elif name == 'runsScored':
                    parsed_stats['runs_scored'] = int(value)
                elif name == 'runsAllowed':
                    parsed_stats['runs_allowed'] = int(value)
            
            if 'runs_scored' in parsed_stats and 'runs_allowed' in parsed_stats:
                parsed_stats['run_diff'] = parsed_stats['runs_scored'] - parsed_stats['runs_allowed']
            
            return parsed_stats
            
        except Exception as e:
            logger.error(f"Error parsing ESPN team stats: {e}")
            return {}
    
    def _parse_mlb_team_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse MLB team statistics."""
        try:
            stats = data.get('stats', [])
            parsed_stats = {}
            
            for stat in stats:
                splits = stat.get('splits', [])
                if splits:
                    stats_data = splits[0].get('stat', {})
                    
                    parsed_stats['wins'] = stats_data.get('wins', 0)
                    parsed_stats['losses'] = stats_data.get('losses', 0)
                    parsed_stats['win_pct'] = stats_data.get('winPct', 0.0)
                    parsed_stats['runs_scored'] = stats_data.get('runs', 0)
                    parsed_stats['runs_allowed'] = stats_data.get('runsAllowed', 0)
                    parsed_stats['run_diff'] = parsed_stats['runs_scored'] - parsed_stats['runs_allowed']
            
            return parsed_stats
            
        except Exception as e:
            logger.error(f"Error parsing MLB team stats: {e}")
            return {}
    
    def _parse_espn_player_stats(self, data: Dict[str, Any]]) -> Dict[str, Any]:
        """Parse ESPN player statistics."""
        try:
            stats = data.get('stats', [])
            parsed_stats = {}
            
            for stat in stats:
                name = stat.get('name', '')
                value = stat.get('value', 0)
                
                if name == 'avg':
                    parsed_stats['avg'] = float(value)
                elif name == 'hr':
                    parsed_stats['hr'] = int(value)
                elif name == 'rbi':
                    parsed_stats['rbi'] = int(value)
                elif name == 'ops':
                    parsed_stats['ops'] = float(value)
                elif name == 'hits':
                    parsed_stats['hits'] = int(value)
                elif name == 'atBats':
                    parsed_stats['ab'] = int(value)
            
            return parsed_stats
            
        except Exception as e:
            logger.error(f"Error parsing ESPN player stats: {e}")
            return {}
    
    def _parse_mlb_player_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse MLB player statistics."""
        try:
            stats = data.get('stats', [])
            parsed_stats = {}
            
            for stat in stats:
                splits = stat.get('splits', [])
                if splits:
                    stats_data = splits[0].get('stat', {})
                    
                    parsed_stats['avg'] = stats_data.get('avg', 0.0)
                    parsed_stats['hr'] = stats_data.get('homeRuns', 0)
                    parsed_stats['rbi'] = stats_data.get('rbi', 0)
                    parsed_stats['ops'] = stats_data.get('ops', 0.0)
                    parsed_stats['hits'] = stats_data.get('hits', 0)
                    parsed_stats['ab'] = stats_data.get('atBats', 0)
            
            return parsed_stats
            
        except Exception as e:
            logger.error(f"Error parsing MLB player stats: {e}")
            return {}
    
    def _parse_espn_live_scores(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse ESPN live scores."""
        try:
            games = []
            
            for event in data.get('events', []):
                competition = event.get('competitions', [{}])[0]
                competitors = competition.get('competitors', [])
                
                if len(competitors) >= 2:
                    away_team = competitors[0].get('team', {}).get('name', 'TBD')
                    home_team = competitors[1].get('team', {}).get('name', 'TBD')
                    away_score = competitors[0].get('score', '0')
                    home_score = competitors[1].get('score', '0')
                    status = event.get('status', {}).get('type', {}).get('description', 'Unknown')
                    
                    games.append({
                        'away_team': away_team,
                        'home_team': home_team,
                        'away_score': away_score,
                        'home_score': home_score,
                        'status': status
                    })
            
            return games
            
        except Exception as e:
            logger.error(f"Error parsing ESPN live scores: {e}")
            return []
    
    def _parse_mlb_live_scores(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse MLB live scores."""
        try:
            games = []
            
            for date in data.get('dates', []):
                for game in date.get('games', []):
                    away_team = game.get('teams', {}).get('away', {}).get('team', {}).get('name', 'TBD')
                    home_team = game.get('teams', {}).get('home', {}).get('team', {}).get('name', 'TBD')
                    away_score = game.get('teams', {}).get('away', {}).get('score', '0')
                    home_score = game.get('teams', {}).get('home', {}).get('score', '0')
                    status = game.get('status', {}).get('detailedState', 'Unknown')
                    
                    games.append({
                        'away_team': away_team,
                        'home_team': home_team,
                        'away_score': away_score,
                        'home_score': home_score,
                        'status': status
                    })
            
            return games
            
        except Exception as e:
            logger.error(f"Error parsing MLB live scores: {e}")
            return []
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close() 