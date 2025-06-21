# data_enrichment.py

#!/usr/bin/env python3
"""
data_enrichment.py

Dynamic data enrichment for betting analysis:
- Game schedules and times
- Weather data
- Head-to-head statistics
- Edge calculations
- Real-time odds updates
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import aiohttp
import json

from pybaseball import schedule_and_record, batting_stats, pitching_stats
from pybaseball import playerid_lookup, statcast_batter, statcast_pitcher

logger = logging.getLogger(__name__)


class DataEnrichment:
    """Handles dynamic data enrichment for betting analysis."""
    
    def __init__(self):
        self.session = None
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_game_info(self, team1: str, team2: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive game information including:
        - Game time and date
        - Weather conditions
        - Starting pitchers
        - Venue
        """
        try:
            # Get today's schedule
            today = datetime.now().strftime("%Y-%m-%d")
            schedule = schedule_and_record(2024, team1)
            
            # Find the specific game
            game = None
            for _, row in schedule.iterrows():
                if (team1 in str(row['Opp']) and team2 in str(row['Opp'])) or \
                   (team2 in str(row['Opp']) and team1 in str(row['Opp'])):
                    game = row
                    break
            
            if game is None:
                logger.warning(f"Game not found for {team1} vs {team2}")
                return None
            
            # Get weather data
            weather = await self._get_weather_data(game.get('Home', 'Unknown'))
            
            # Get starting pitchers if available
            pitchers = await self._get_starting_pitchers(team1, team2)
            
            return {
                "game_time": game.get('Date', 'Unknown'),
                "venue": game.get('Home', 'Unknown'),
                "weather": weather,
                "starting_pitchers": pitchers,
                "game_id": game.get('Gm#', 'Unknown')
            }
            
        except Exception as e:
            logger.exception(f"Error getting game info for {team1} vs {team2}")
            return None
    
    async def get_h2h_stats(self, team1: str, team2: str, last_n_games: int = 10) -> Optional[Dict[str, Any]]:
        """
        Get head-to-head statistics between two teams.
        """
        try:
            # Get recent games between the teams
            h2h_data = {
                "team1_wins": 0,
                "team2_wins": 0,
                "avg_runs_team1": 0,
                "avg_runs_team2": 0,
                "last_meetings": []
            }
            
            # This would require more complex MLB Stats API calls
            # For now, return basic structure
            logger.info(f"Getting H2H stats for {team1} vs {team2}")
            
            return h2h_data
            
        except Exception as e:
            logger.exception(f"Error getting H2H stats for {team1} vs {team2}")
            return None
    
    async def get_player_stats(self, player_name: str, stat_type: str = "batting") -> Optional[Dict[str, Any]]:
        """
        Get player statistics for prop bets.
        """
        try:
            # Look up player ID
            player_lookup = playerid_lookup(player_name.split()[1], player_name.split()[0])
            
            if player_lookup.empty:
                logger.warning(f"Player not found: {player_name}")
                return None
            
            player_id = player_lookup.iloc[0]['key_mlbam']
            
            if stat_type == "batting":
                stats = batting_stats(2024, qual=1)
                player_stats = stats[stats['Name'] == player_name]
            else:
                stats = pitching_stats(2024, qual=1)
                player_stats = stats[stats['Name'] == player_name]
            
            if player_stats.empty:
                logger.warning(f"No stats found for {player_name}")
                return None
            
            return player_stats.iloc[0].to_dict()
            
        except Exception as e:
            logger.exception(f"Error getting player stats for {player_name}")
            return None
    
    async def calculate_edge(self, bet_details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Calculate betting edge based on historical data and current odds.
        """
        try:
            from image_processing import calculate_implied_probability
            
            odds = bet_details.get('odds', '0')
            implied_prob = calculate_implied_probability(odds)
            
            # Get true probability based on bet type
            true_prob = await self._calculate_true_probability(bet_details)
            
            if true_prob is None:
                return None
            
            edge = (true_prob - implied_prob) * 100
            
            return {
                "implied_probability": implied_prob,
                "true_probability": true_prob,
                "edge_percentage": edge,
                "recommendation": "Bet" if edge > 2 else "Pass" if edge < -2 else "Consider"
            }
            
        except Exception as e:
            logger.exception("Error calculating edge")
            return None
    
    async def _get_weather_data(self, venue: str) -> Optional[Dict[str, Any]]:
        """Get weather data for game venue."""
        # This would integrate with a weather API
        # For now, return placeholder
        return {
            "temperature": "72°F",
            "conditions": "Partly Cloudy",
            "wind_speed": "8 mph",
            "wind_direction": "SW"
        }
    
    async def _get_starting_pitchers(self, team1: str, team2: str) -> Optional[Dict[str, Any]]:
        """Get starting pitchers for the game."""
        # This would require MLB Stats API integration
        # For now, return placeholder
        return {
            "team1_pitcher": "TBD",
            "team2_pitcher": "TBD"
        }
    
    async def _calculate_true_probability(self, bet_details: Dict[str, Any]) -> Optional[float]:
        """
        Calculate true probability based on historical data and bet type.
        """
        bet_type = bet_details.get('type', '')
        
        if bet_type == 'moneyline':
            return await self._calculate_moneyline_probability(bet_details)
        elif bet_type == 'player_prop':
            return await self._calculate_prop_probability(bet_details)
        elif bet_type == 'total':
            return await self._calculate_total_probability(bet_details)
        
        return None
    
    async def _calculate_moneyline_probability(self, bet_details: Dict[str, Any]) -> Optional[float]:
        """Calculate true probability for moneyline bets."""
        # This would use team records, recent performance, H2H stats
        # For now, return placeholder
        return 0.52  # 52% win probability
    
    async def _calculate_prop_probability(self, bet_details: Dict[str, Any]) -> Optional[float]:
        """Calculate true probability for player props."""
        # This would use player season stats, recent performance
        # For now, return placeholder
        return 0.48  # 48% hit probability
    
    async def _calculate_total_probability(self, bet_details: Dict[str, Any]) -> Optional[float]:
        """Calculate true probability for over/under totals."""
        # This would use team scoring averages, recent totals
        # For now, return placeholder
        return 0.51  # 51% over probability


async def enrich_bet_analysis(bet_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to enrich bet analysis with dynamic data.
    """
    async with DataEnrichment() as de:
        enriched = bet_details.copy()
        
        # Add game information
        if 'away' in bet_details and 'home' in bet_details:
            game_info = await de.get_game_info(bet_details['away'], bet_details['home'])
            if game_info:
                enriched['game_info'] = game_info
        
        # Add H2H stats for team bets
        if bet_details.get('type') in ['moneyline', 'total']:
            h2h_stats = await de.get_h2h_stats(bet_details.get('away', ''), bet_details.get('home', ''))
            if h2h_stats:
                enriched['h2h_stats'] = h2h_stats
        
        # Add player stats for props
        if bet_details.get('type') == 'player_prop':
            player_stats = await de.get_player_stats(bet_details.get('player', ''))
            if player_stats:
                enriched['player_stats'] = player_stats
        
        # Calculate edge
        edge_analysis = await de.calculate_edge(bet_details)
        if edge_analysis:
            enriched['edge_analysis'] = edge_analysis
        
        return enriched
