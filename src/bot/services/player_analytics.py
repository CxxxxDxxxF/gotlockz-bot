"""
Advanced Player Analytics Service - MLB player statistics and analysis
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List
import aiohttp
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PlayerAnalyticsService:
    """Service for advanced MLB player analytics and statistics."""
    
    def __init__(self):
        self.session = None
        self.mlb_base_url = "https://statsapi.mlb.com/api/v1"
        self.timeout = aiohttp.ClientTimeout(total=15)
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session
    
    async def get_player_stats(self, player_name: str, season: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get comprehensive player statistics."""
        try:
            if not season:
                season = datetime.now().year
            
            session = await self._get_session()
            
            # Search for player
            player_id = await self._search_player(session, player_name)
            if not player_id:
                return None
            
            # Get player stats
            batting_stats = await self._get_batting_stats(session, player_id, season)
            pitching_stats = await self._get_pitching_stats(session, player_id, season)
            fielding_stats = await self._get_fielding_stats(session, player_id, season)
            
            # Get player info
            player_info = await self._get_player_info(session, player_id)
            
            return {
                'player_info': player_info,
                'batting': batting_stats,
                'pitching': pitching_stats,
                'fielding': fielding_stats,
                'season': season,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting player stats for {player_name}: {e}")
            return None
    
    async def get_head_to_head_stats(self, batter: str, pitcher: str) -> Optional[Dict[str, Any]]:
        """Get head-to-head statistics between batter and pitcher."""
        try:
            session = await self._get_session()
            
            # Get player IDs
            batter_id = await self._search_player(session, batter)
            pitcher_id = await self._search_player(session, pitcher)
            
            if not batter_id or not pitcher_id:
                return None
            
            # Get head-to-head stats
            url = f"{self.mlb_base_url}/stats"
            params = {
                'personIds': batter_id,
                'group': 'hitting',
                'stats': 'vsRHP,vsLHP',
                'season': datetime.now().year
            }
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                return self._parse_head_to_head_stats(data, batter, pitcher)
                
        except Exception as e:
            logger.error(f"Error getting head-to-head stats: {e}")
            return None
    
    async def get_recent_performance(self, player_name: str, days: int = 30) -> Optional[Dict[str, Any]]:
        """Get player's recent performance over specified days."""
        try:
            session = await self._get_session()
            
            # Search for player
            player_id = await self._search_player(session, player_name)
            if not player_id:
                return None
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get recent games
            url = f"{self.mlb_base_url}/stats"
            params = {
                'personIds': player_id,
                'group': 'hitting',
                'stats': 'season',
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d')
            }
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                return self._parse_recent_performance(data, player_name, days)
                
        except Exception as e:
            logger.error(f"Error getting recent performance for {player_name}: {e}")
            return None
    
    async def get_matchup_analysis(self, team1: str, team2: str) -> Dict[str, Any]:
        """Get detailed matchup analysis between two teams."""
        try:
            session = await self._get_session()
            
            # Get team IDs
            team1_id = await self._get_team_id(session, team1)
            team2_id = await self._get_team_id(session, team2)
            
            if not team1_id or not team2_id:
                return {}
            
            # Get team rosters and key players
            team1_roster = await self._get_team_roster(session, team1_id)
            team2_roster = await self._get_team_roster(session, team2_id)
            
            # Analyze key matchups
            key_matchups = await self._analyze_key_matchups(team1_roster, team2_roster)
            
            return {
                'team1': {
                    'name': team1,
                    'roster': team1_roster,
                    'key_players': self._identify_key_players(team1_roster)
                },
                'team2': {
                    'name': team2,
                    'roster': team2_roster,
                    'key_players': self._identify_key_players(team2_roster)
                },
                'key_matchups': key_matchups,
                'analysis': self._generate_matchup_analysis(team1_roster, team2_roster)
            }
            
        except Exception as e:
            logger.error(f"Error getting matchup analysis: {e}")
            return {}
    
    async def _search_player(self, session: aiohttp.ClientSession, player_name: str) -> Optional[int]:
        """Search for player by name and return player ID."""
        try:
            url = f"{self.mlb_base_url}/people"
            params = {'search': player_name}
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                people = data.get('people', [])
                
                if people:
                    return people[0].get('id')
                
                return None
                
        except Exception as e:
            logger.error(f"Error searching for player {player_name}: {e}")
            return None
    
    async def _get_batting_stats(self, session: aiohttp.ClientSession, player_id: int, season: int) -> Dict[str, Any]:
        """Get batting statistics for a player."""
        try:
            url = f"{self.mlb_base_url}/stats"
            params = {
                'personIds': player_id,
                'group': 'hitting',
                'stats': 'season',
                'season': season
            }
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return {}
                
                data = await response.json()
                return self._parse_batting_stats(data)
                
        except Exception as e:
            logger.error(f"Error getting batting stats: {e}")
            return {}
    
    async def _get_pitching_stats(self, session: aiohttp.ClientSession, player_id: int, season: int) -> Dict[str, Any]:
        """Get pitching statistics for a player."""
        try:
            url = f"{self.mlb_base_url}/stats"
            params = {
                'personIds': player_id,
                'group': 'pitching',
                'stats': 'season',
                'season': season
            }
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return {}
                
                data = await response.json()
                return self._parse_pitching_stats(data)
                
        except Exception as e:
            logger.error(f"Error getting pitching stats: {e}")
            return {}
    
    async def _get_fielding_stats(self, session: aiohttp.ClientSession, player_id: int, season: int) -> Dict[str, Any]:
        """Get fielding statistics for a player."""
        try:
            url = f"{self.mlb_base_url}/stats"
            params = {
                'personIds': player_id,
                'group': 'fielding',
                'stats': 'season',
                'season': season
            }
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return {}
                
                data = await response.json()
                return self._parse_fielding_stats(data)
                
        except Exception as e:
            logger.error(f"Error getting fielding stats: {e}")
            return {}
    
    async def _get_player_info(self, session: aiohttp.ClientSession, player_id: int) -> Dict[str, Any]:
        """Get basic player information."""
        try:
            url = f"{self.mlb_base_url}/people/{player_id}"
            
            async with session.get(url) as response:
                if response.status != 200:
                    return {}
                
                data = await response.json()
                people = data.get('people', [])
                
                if people:
                    person = people[0]
                    return {
                        'name': person.get('fullName'),
                        'position': person.get('primaryPosition', {}).get('abbreviation'),
                        'team': person.get('currentTeam', {}).get('name'),
                        'age': person.get('currentAge'),
                        'height': person.get('height'),
                        'weight': person.get('weight'),
                        'bats': person.get('batSide', {}).get('description'),
                        'throws': person.get('throwSide', {}).get('description')
                    }
                
                return {}
                
        except Exception as e:
            logger.error(f"Error getting player info: {e}")
            return {}
    
    def _parse_batting_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse batting statistics from API response."""
        try:
            stats = data.get('stats', [])
            if not stats:
                return {}
            
            stat = stats[0]
            splits = stat.get('splits', [])
            
            if not splits:
                return {}
            
            split = splits[0]
            stat_data = split.get('stat', {})
            
            return {
                'avg': stat_data.get('avg', 0.0),
                'obp': stat_data.get('obp', 0.0),
                'slg': stat_data.get('slg', 0.0),
                'ops': stat_data.get('ops', 0.0),
                'hits': stat_data.get('hits', 0),
                'home_runs': stat_data.get('homeRuns', 0),
                'rbi': stat_data.get('rbi', 0),
                'runs': stat_data.get('runs', 0),
                'stolen_bases': stat_data.get('stolenBases', 0),
                'walks': stat_data.get('baseOnBalls', 0),
                'strikeouts': stat_data.get('strikeOuts', 0),
                'games_played': stat_data.get('gamesPlayed', 0),
                'at_bats': stat_data.get('atBats', 0)
            }
            
        except Exception as e:
            logger.error(f"Error parsing batting stats: {e}")
            return {}
    
    def _parse_pitching_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse pitching statistics from API response."""
        try:
            stats = data.get('stats', [])
            if not stats:
                return {}
            
            stat = stats[0]
            splits = stat.get('splits', [])
            
            if not splits:
                return {}
            
            split = splits[0]
            stat_data = split.get('stat', {})
            
            return {
                'era': stat_data.get('era', 0.0),
                'wins': stat_data.get('wins', 0),
                'losses': stat_data.get('losses', 0),
                'saves': stat_data.get('saves', 0),
                'innings_pitched': stat_data.get('inningsPitched', 0),
                'strikeouts': stat_data.get('strikeOuts', 0),
                'walks': stat_data.get('baseOnBalls', 0),
                'hits_allowed': stat_data.get('hits', 0),
                'runs_allowed': stat_data.get('runs', 0),
                'earned_runs': stat_data.get('earnedRuns', 0),
                'whip': stat_data.get('whip', 0.0),
                'games': stat_data.get('gamesPlayed', 0),
                'games_started': stat_data.get('gamesStarted', 0)
            }
            
        except Exception as e:
            logger.error(f"Error parsing pitching stats: {e}")
            return {}
    
    def _parse_fielding_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse fielding statistics from API response."""
        try:
            stats = data.get('stats', [])
            if not stats:
                return {}
            
            stat = stats[0]
            splits = stat.get('splits', [])
            
            if not splits:
                return {}
            
            split = splits[0]
            stat_data = split.get('stat', {})
            
            return {
                'fielding_pct': stat_data.get('fieldingPct', 0.0),
                'errors': stat_data.get('errors', 0),
                'assists': stat_data.get('assists', 0),
                'put_outs': stat_data.get('putOuts', 0),
                'double_plays': stat_data.get('doublePlaysTurned', 0),
                'games_played': stat_data.get('gamesPlayed', 0)
            }
            
        except Exception as e:
            logger.error(f"Error parsing fielding stats: {e}")
            return {}
    
    async def _get_team_id(self, session: aiohttp.ClientSession, team_name: str) -> Optional[int]:
        """Get team ID by name."""
        try:
            url = f"{self.mlb_base_url}/teams"
            
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                teams = data.get('teams', [])
                
                for team in teams:
                    if team_name.lower() in team.get('name', '').lower():
                        return team.get('id')
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting team ID for {team_name}: {e}")
            return None
    
    async def _get_team_roster(self, session: aiohttp.ClientSession, team_id: int) -> List[Dict[str, Any]]:
        """Get team roster."""
        try:
            url = f"{self.mlb_base_url}/teams/{team_id}/roster"
            
            async with session.get(url) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                roster = data.get('roster', [])
                
                return [
                    {
                        'id': player.get('person', {}).get('id'),
                        'name': player.get('person', {}).get('fullName'),
                        'position': player.get('position', {}).get('abbreviation'),
                        'jersey_number': player.get('jerseyNumber')
                    }
                    for player in roster
                ]
                
        except Exception as e:
            logger.error(f"Error getting team roster: {e}")
            return []
    
    def _identify_key_players(self, roster: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify key players on the roster."""
        try:
            # This is a simplified version - in practice, you'd analyze stats
            key_positions = ['P', 'C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF']
            key_players = []
            
            for player in roster:
                if player.get('position') in key_positions:
                    key_players.append(player)
            
            return key_players[:9]  # Return top 9 players
            
        except Exception as e:
            logger.error(f"Error identifying key players: {e}")
            return []
    
    async def _analyze_key_matchups(self, roster1: List[Dict[str, Any]], roster2: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze key matchups between teams."""
        try:
            matchups = []
            
            # Find starting pitchers
            pitchers1 = [p for p in roster1 if p.get('position') == 'P']
            pitchers2 = [p for p in roster2 if p.get('position') == 'P']
            
            # Find key hitters
            hitters1 = [p for p in roster1 if p.get('position') != 'P']
            hitters2 = [p for p in roster2 if p.get('position') != 'P']
            
            # Create pitcher vs hitter matchups
            for pitcher in pitchers1[:2]:  # Top 2 pitchers
                for hitter in hitters2[:5]:  # Top 5 hitters
                    matchups.append({
                        'type': 'pitcher_vs_hitter',
                        'pitcher': pitcher,
                        'hitter': hitter,
                        'analysis': f"{pitcher['name']} vs {hitter['name']}"
                    })
            
            for pitcher in pitchers2[:2]:
                for hitter in hitters1[:5]:
                    matchups.append({
                        'type': 'pitcher_vs_hitter',
                        'pitcher': pitcher,
                        'hitter': hitter,
                        'analysis': f"{pitcher['name']} vs {hitter['name']}"
                    })
            
            return matchups
            
        except Exception as e:
            logger.error(f"Error analyzing key matchups: {e}")
            return []
    
    def _generate_matchup_analysis(self, roster1: List[Dict[str, Any]], roster2: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate overall matchup analysis."""
        try:
            return {
                'summary': f"Analysis of {len(roster1)} vs {len(roster2)} players",
                'key_factors': [
                    "Starting pitching matchups",
                    "Bullpen depth",
                    "Offensive firepower",
                    "Defensive alignment",
                    "Recent form"
                ],
                'recommendations': [
                    "Focus on starting pitcher performance",
                    "Monitor bullpen usage",
                    "Track key hitter matchups",
                    "Consider weather impact"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating matchup analysis: {e}")
            return {}
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close() 