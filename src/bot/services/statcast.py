"""
Statcast Service - Direct integration with Baseball Savant data
"""
import logging
import asyncio
from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime, timedelta
import aiohttp
from urllib.error import HTTPError
import time

logger = logging.getLogger(__name__)


class StatcastService:
    """Service for fetching Statcast data directly from Baseball Savant."""
    
    def __init__(self):
        self.session = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def get_statcast_data(self, team1: str, team2: str) -> Dict[str, Any]:
        """Get Statcast data for both teams."""
        try:
            # Map team names to MLB team abbreviations
            team_mapping = {
                'Los Angeles Angels': 'LAA',
                'Oakland Athletics': 'OAK',
                'New York Yankees': 'NYY',
                'Boston Red Sox': 'BOS',
                'Houston Astros': 'HOU',
                'Los Angeles Dodgers': 'LAD',
                'San Francisco Giants': 'SF',
                'Colorado Rockies': 'COL',
                'Chicago Cubs': 'CHC',
                'Chicago White Sox': 'CWS',
                'Cleveland Guardians': 'CLE',
                'Detroit Tigers': 'DET',
                'Kansas City Royals': 'KC',
                'Minnesota Twins': 'MIN',
                'Baltimore Orioles': 'BAL',
                'Tampa Bay Rays': 'TB',
                'Toronto Blue Jays': 'TOR',
                'Atlanta Braves': 'ATL',
                'Miami Marlins': 'MIA',
                'New York Mets': 'NYM',
                'Philadelphia Phillies': 'PHI',
                'Washington Nationals': 'WSH',
                'Arizona Diamondbacks': 'ARI',
                'San Diego Padres': 'SD',
                'Seattle Mariners': 'SEA',
                'Texas Rangers': 'TEX',
                'Cincinnati Reds': 'CIN',
                'Milwaukee Brewers': 'MIL',
                'Pittsburgh Pirates': 'PIT',
                'St. Louis Cardinals': 'STL'
            }
            
            team1_abbr = team_mapping.get(team1, team1)
            team2_abbr = team_mapping.get(team2, team2)
            
            # Get current year
            current_year = datetime.now().year
            
            # Get Statcast data for both teams
            team1_data = await self._get_team_statcast(team1_abbr, current_year)
            team2_data = await self._get_team_statcast(team2_abbr, current_year)
            
            return {
                'team1': team1_data,
                'team2': team2_data,
                'summary': f"Statcast data loaded for {team1} vs {team2}"
            }
            
        except Exception as e:
            logger.error(f"Error getting Statcast data: {e}")
            return {}
    
    async def _get_team_statcast(self, team_abbr: str, season: int) -> Dict[str, Any]:
        """Get Statcast data for a specific team."""
        try:
            # Get both home and road data
            home_data = await self._savant_search(season, team_abbr, 'Home')
            road_data = await self._savant_search(season, team_abbr, 'Road')
            
            # Combine the data
            if home_data is not None and road_data is not None:
                combined_data = pd.concat([home_data, road_data], ignore_index=True)
            elif home_data is not None:
                combined_data = home_data
            elif road_data is not None:
                combined_data = road_data
            else:
                return {}
            
            # Process the combined data
            batting_stats = self._process_statcast_batting(combined_data)
            pitching_stats = self._process_statcast_pitching(combined_data)
            
            return {
                'batting': batting_stats,
                'pitching': pitching_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting Statcast data for {team_abbr}: {e}")
            return {}
    
    async def _savant_search(self, season: int, team: str, home_road: str) -> Optional[pd.DataFrame]:
        """Search Baseball Savant for Statcast data."""
        try:
            # Generate the URL to search based on team and year
            url = ("https://baseballsavant.mlb.com/statcast_search/csv?all=true"
                   "&hfPT=&hfAB=&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=&h"
                   f"fC=&hfSea={season}%7C&hfSit=&player_type=pitcher&hfOuts=&opponent"
                   "=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt=&game_date_lt="
                   f"&hfInfield=&team={team}&position=&hfOutfield=&hfRO="
                   f"&home_road={home_road}&hfFlag=&hfPull=&metric_1=&hfInn="
                   "&min_pitches=0&min_results=0&group_by=name&sort_col=pitches"
                   "&player_event_sort=pitch_number_thisgame&sort_order=desc"
                   "&min_pas=0&type=details&")
            
            session = await self._get_session()
            
            # Define the number of times to retry on a connection error
            num_tries = 3
            pause_time = 5
            
            # Attempt to download the file with retries
            for retry in range(num_tries):
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            content = await response.text()
                            if content.strip():  # Check if content is not empty
                                df = pd.read_csv(pd.StringIO(content), low_memory=False)
                                
                                # Drop duplicate and deprecated fields if they exist
                                columns_to_drop = ['pitcher.1', 'fielder_2.1', 'umpire', 'spin_dir',
                                                  'spin_rate_deprecated', 'break_angle_deprecated',
                                                  'break_length_deprecated', 'tfs_deprecated',
                                                  'tfs_zulu_deprecated']
                                
                                existing_columns = [col for col in columns_to_drop if col in df.columns]
                                if existing_columns:
                                    df.drop(existing_columns, axis=1, inplace=True)
                                
                                return df
                            else:
                                logger.warning(f"Empty response for {team} {home_road} {season}")
                                return None
                        else:
                            logger.warning(f"HTTP {response.status} for {team} {home_road} {season}")
                            if retry == num_tries - 1:
                                return None
                            await asyncio.sleep(pause_time)
                            pause_time *= 2
                            
                except Exception as e:
                    logger.error(f"Error downloading Statcast data (attempt {retry + 1}): {e}")
                    if retry == num_tries - 1:
                        return None
                    await asyncio.sleep(pause_time)
                    pause_time *= 2
            
            return None
            
        except Exception as e:
            logger.error(f"Error in savant_search: {e}")
            return None
    
    def _process_statcast_batting(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Process Statcast batting data."""
        try:
            if data.empty:
                return {}
            
            # Filter for batting events (remove pitching events)
            batting_data = data[data['player_type'] == 'batter'] if 'player_type' in data.columns else data
            
            if batting_data.empty:
                return {}
            
            # Calculate advanced metrics
            stats = {}
            
            # Exit velocity metrics
            if 'launch_speed' in batting_data.columns:
                launch_speed = batting_data['launch_speed'].dropna()
                if not launch_speed.empty:
                    stats['avg_exit_velocity'] = round(launch_speed.mean(), 1)
                    stats['hard_hit_pct'] = round((launch_speed >= 95).sum() / len(launch_speed) * 100, 1)
                    stats['barrel_pct'] = round((launch_speed >= 98).sum() / len(launch_speed) * 100, 1)
            
            # Launch angle metrics
            if 'launch_angle' in batting_data.columns:
                launch_angle = batting_data['launch_angle'].dropna()
                if not launch_angle.empty:
                    stats['avg_launch_angle'] = round(launch_angle.mean(), 1)
                    stats['sweet_spot_pct'] = round(((launch_angle >= 8) & (launch_angle <= 32)).sum() / len(launch_angle) * 100, 1)
            
            # Total events
            stats['total_events'] = len(batting_data)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error processing Statcast batting data: {e}")
            return {}
    
    def _process_statcast_pitching(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Process Statcast pitching data."""
        try:
            if data.empty:
                return {}
            
            # Filter for pitching events
            pitching_data = data[data['player_type'] == 'pitcher'] if 'player_type' in data.columns else data
            
            if pitching_data.empty:
                return {}
            
            # Calculate advanced metrics
            stats = {}
            
            # Velocity metrics
            if 'release_speed' in pitching_data.columns:
                release_speed = pitching_data['release_speed'].dropna()
                if not release_speed.empty:
                    stats['avg_velocity'] = round(release_speed.mean(), 1)
            
            # Spin rate metrics
            if 'release_spin_rate' in pitching_data.columns:
                release_spin_rate = pitching_data['release_spin_rate'].dropna()
                if not release_spin_rate.empty:
                    stats['avg_spin_rate'] = round(release_spin_rate.mean(), 0)
            
            # Whiff rate
            if 'description' in pitching_data.columns:
                total_pitches = len(pitching_data)
                whiffs = (pitching_data['description'] == 'swinging_strike').sum()
                stats['whiff_pct'] = round(whiffs / total_pitches * 100, 1) if total_pitches > 0 else 0
            
            # Chase rate (pitches outside zone)
            if 'zone' in pitching_data.columns:
                zone_data = pitching_data['zone'].dropna()
                if not zone_data.empty:
                    chases = (zone_data > 9).sum()
                    stats['chase_pct'] = round(chases / len(zone_data) * 100, 1)
            
            # Total pitches
            stats['total_pitches'] = len(pitching_data)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error processing Statcast pitching data: {e}")
            return {}
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close() 