"""
Advanced Stats Service - Enhanced MLB statistics with Statcast data
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List
import aiohttp
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AdvancedStatsService:
    """Service for fetching advanced MLB statistics including Statcast data."""
    
    def __init__(self):
        self.session = None
        self.mlb_base_url = "https://statsapi.mlb.com/api/v1"
        self.statcast_base_url = "https://baseballsavant.mlb.com/statcast_search/csv"
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=15)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def get_advanced_stats(self, bet_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get comprehensive advanced stats for betting analysis."""
        try:
            teams = bet_data.get('teams', [])
            if len(teams) < 2:
                return None
            
            # Get basic team stats
            team1_stats = await self.get_team_stats(teams[0])
            team2_stats = await self.get_team_stats(teams[1])
            
            # Get advanced stats
            team1_advanced = await self.get_advanced_team_stats(teams[0])
            team2_advanced = await self.get_advanced_team_stats(teams[1])
            
            # Get park factors
            park_factors = await self.get_park_factors(teams[0], teams[1])
            
            # Get weather data (if available)
            weather_data = await self.get_weather_data(teams[0], teams[1])
            
            # Combine all stats
            combined_stats = {
                'team1': {**team1_stats, **team1_advanced},
                'team2': {**team2_stats, **team2_advanced},
                'park_factors': park_factors,
                'weather': weather_data,
                'summary': f"Advanced stats loaded for {teams[0]} vs {teams[1]}"
            }
            
            return combined_stats
            
        except Exception as e:
            logger.error(f"Error getting advanced stats: {e}")
            return None
    
    async def get_advanced_team_stats(self, team_name: str) -> Dict[str, Any]:
        """Get advanced team statistics including Statcast data."""
        try:
            session = await self._get_session()
            
            # Get team ID first
            team_id = await self._get_team_id(session, team_name)
            if not team_id:
                return {}
            
            # Get various advanced stats
            stats = {}
            
            # Batting stats
            batting_stats = await self._get_batting_stats(session, team_id)
            if batting_stats:
                stats.update(batting_stats)
            
            # Pitching stats
            pitching_stats = await self._get_pitching_stats(session, team_id)
            if pitching_stats:
                stats.update(pitching_stats)
            
            # Recent performance (last 10 games)
            recent_stats = await self._get_recent_performance(session, team_id)
            if recent_stats:
                stats.update(recent_stats)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting advanced team stats for {team_name}: {e}")
            return {}
    
    async def get_park_factors(self, team1: str, team2: str) -> Dict[str, Any]:
        """Get park factors for the teams."""
        try:
            # This would typically come from a park factors database
            # For now, we'll use some common park factors
            park_factors = {
                'runs': 1.0,  # Neutral park
                'hr': 1.0,    # Neutral HR park
                'k': 1.0,     # Neutral K park
                'bb': 1.0     # Neutral BB park
            }
            
            # Adjust based on known park factors
            if any(team in team1 for team in ['Colorado', 'Rockies']):
                park_factors = {'runs': 1.15, 'hr': 1.25, 'k': 0.95, 'bb': 1.05}
            elif any(team in team1 for team in ['San Francisco', 'Giants']):
                park_factors = {'runs': 0.85, 'hr': 0.75, 'k': 1.05, 'bb': 0.95}
            elif any(team in team1 for team in ['Boston', 'Red Sox']):
                park_factors = {'runs': 1.05, 'hr': 1.15, 'k': 0.98, 'bb': 1.02}
            
            return park_factors
            
        except Exception as e:
            logger.error(f"Error getting park factors: {e}")
            return {'runs': 1.0, 'hr': 1.0, 'k': 1.0, 'bb': 1.0}
    
    async def get_weather_data(self, team1: str, team2: str) -> Dict[str, Any]:
        """Get weather data for the game location."""
        try:
            # This would integrate with a weather API
            # For now, return neutral weather
            return {
                'temperature': 72,
                'wind_speed': 8,
                'wind_direction': 'SW',
                'humidity': 65,
                'conditions': 'Partly Cloudy'
            }
            
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            return {}
    
    async def _get_team_id(self, session: aiohttp.ClientSession, team_name: str) -> Optional[int]:
        """Get team ID from MLB API."""
        try:
            url = f"{self.mlb_base_url}/teams"
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                
                for team in data.get('teams', []):
                    if team_name.lower() in team.get('name', '').lower():
                        return team.get('id')
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting team ID: {e}")
            return None
    
    async def _get_batting_stats(self, session: aiohttp.ClientSession, team_id: int) -> Dict[str, Any]:
        """Get advanced batting statistics."""
        try:
            url = f"{self.mlb_base_url}/teams/{team_id}/stats"
            params = {
                'group': 'hitting',
                'season': datetime.now().year,
                'stats': 'season'
            }
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return {}
                
                data = await response.json()
                return self._parse_batting_stats(data)
                
        except Exception as e:
            logger.error(f"Error getting batting stats: {e}")
            return {}
    
    async def _get_pitching_stats(self, session: aiohttp.ClientSession, team_id: int) -> Dict[str, Any]:
        """Get advanced pitching statistics."""
        try:
            url = f"{self.mlb_base_url}/teams/{team_id}/stats"
            params = {
                'group': 'pitching',
                'season': datetime.now().year,
                'stats': 'season'
            }
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return {}
                
                data = await response.json()
                return self._parse_pitching_stats(data)
                
        except Exception as e:
            logger.error(f"Error getting pitching stats: {e}")
            return {}
    
    async def _get_recent_performance(self, session: aiohttp.ClientSession, team_id: int) -> Dict[str, Any]:
        """Get recent team performance (last 10 games)."""
        try:
            # Get recent games
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            url = f"{self.mlb_base_url}/schedule"
            params = {
                'sportId': 1,
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d'),
                'teamId': team_id,
                'fields': 'dates,games,gamePk,teams,away,home,team,abbreviation,score'
            }
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return {}
                
                data = await response.json()
                return self._parse_recent_performance(data, team_id)
                
        except Exception as e:
            logger.error(f"Error getting recent performance: {e}")
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
                'home_runs': stat_data.get('homeRuns', 0),
                'rbi': stat_data.get('rbi', 0),
                'stolen_bases': stat_data.get('stolenBases', 0),
                'strikeouts': stat_data.get('strikeOuts', 0),
                'walks': stat_data.get('baseOnBalls', 0),
                'hits': stat_data.get('hits', 0),
                'doubles': stat_data.get('doubles', 0),
                'triples': stat_data.get('triples', 0)
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
                'whip': stat_data.get('whip', 0.0),
                'strikeouts': stat_data.get('strikeOuts', 0),
                'walks': stat_data.get('baseOnBalls', 0),
                'hits_allowed': stat_data.get('hits', 0),
                'home_runs_allowed': stat_data.get('homeRuns', 0),
                'innings_pitched': stat_data.get('inningsPitched', 0),
                'saves': stat_data.get('saves', 0),
                'holds': stat_data.get('holds', 0)
            }
            
        except Exception as e:
            logger.error(f"Error parsing pitching stats: {e}")
            return {}
    
    def _parse_recent_performance(self, data: Dict[str, Any], team_id: int) -> Dict[str, Any]:
        """Parse recent performance data."""
        try:
            games = []
            dates = data.get('dates', [])
            
            for date in dates:
                for game in date.get('games', []):
                    away_team = game.get('teams', {}).get('away', {})
                    home_team = game.get('teams', {}).get('home', {})
                    
                    # Determine if this team is home or away
                    if away_team.get('team', {}).get('id') == team_id:
                        team_data = away_team
                        opponent_data = home_team
                        is_home = False
                    elif home_team.get('team', {}).get('id') == team_id:
                        team_data = home_team
                        opponent_data = away_team
                        is_home = True
                    else:
                        continue
                    
                    games.append({
                        'team_score': team_data.get('score', 0),
                        'opponent_score': opponent_data.get('score', 0),
                        'is_home': is_home,
                        'result': 'W' if team_data.get('score', 0) > opponent_data.get('score', 0) else 'L'
                    })
            
            # Calculate recent performance metrics
            if games:
                recent_games = games[-10:]  # Last 10 games
                wins = sum(1 for game in recent_games if game['result'] == 'W')
                avg_runs_scored = sum(game['team_score'] for game in recent_games) / len(recent_games)
                avg_runs_allowed = sum(game['opponent_score'] for game in recent_games) / len(recent_games)
                
                return {
                    'recent_wins': wins,
                    'recent_losses': len(recent_games) - wins,
                    'recent_win_pct': wins / len(recent_games),
                    'avg_runs_scored': round(avg_runs_scored, 1),
                    'avg_runs_allowed': round(avg_runs_allowed, 1),
                    'recent_games': len(recent_games)
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error parsing recent performance: {e}")
            return {}
    
    async def get_team_stats(self, team_name: str) -> Dict[str, Any]:
        """Get basic team statistics (compatibility with existing StatsService)."""
        try:
            session = await self._get_session()
            stats = await self._get_mlb_team_stats(session, team_name)
            return stats or {}
            
        except Exception as e:
            logger.error(f"Error getting team stats for {team_name}: {e}")
            return {}
    
    async def _get_mlb_team_stats(self, session: aiohttp.ClientSession, team_name: str) -> Optional[Dict[str, Any]]:
        """Get team stats from MLB API."""
        try:
            url = f"{self.mlb_base_url}/teams"
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                
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
    
    def _parse_mlb_team_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse MLB team stats from API response."""
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
                'wins': stat_data.get('wins', 0),
                'losses': stat_data.get('losses', 0),
                'win_pct': stat_data.get('winPct', 0.0),
                'runs_scored': stat_data.get('runs', 0),
                'runs_allowed': stat_data.get('runsAllowed', 0),
                'run_diff': stat_data.get('runDifferential', 0),
                'games_played': stat_data.get('gamesPlayed', 0)
            }
            
        except Exception as e:
            logger.error(f"Error parsing MLB team stats: {e}")
            return {}
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close() 