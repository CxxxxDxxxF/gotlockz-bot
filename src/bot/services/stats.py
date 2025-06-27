"""
Stats Service - MLB statistics and data fetching
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


class StatsService:
    """Service for fetching MLB statistics and data."""

    def __init__(self):
        self.session = None
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
            teams = bet_data.get("teams", [])
            if len(teams) < 2:
                return None

            # Fetch team stats
            team1_stats = await self.get_team_stats(teams[0])
            team2_stats = await self.get_team_stats(teams[1])

            if not team1_stats or not team2_stats:
                return None

            # Combine stats
            combined_stats = {
                "team1": team1_stats,
                "team2": team2_stats,
                "summary": f"{teams[0]} vs {teams[1]} stats loaded",
            }

            return combined_stats

        except Exception as e:
            logger.error(f"Error getting live stats: {e}")
            return None

    async def get_team_stats(self, team_name: str) -> Optional[Dict[str, Any]]:
        """Get team statistics from MLB API."""
        try:
            session = await self._get_session()
            stats = await self._get_mlb_team_stats(session, team_name)
            return stats

        except Exception as e:
            logger.error(f"Error getting team stats for {team_name}: {e}")
            return None

    async def get_live_scores(self) -> List[Dict[str, Any]]:
        """Get live game scores from MLB API."""
        try:
            session = await self._get_session()
            games = await self._get_mlb_live_scores(session)
            return games

        except Exception as e:
            logger.error(f"Error getting live scores: {e}")
            return []

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
                for team in data.get("teams", []):
                    if team_name.lower() in team.get("name", "").lower():
                        team_id = team.get("id")
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

    async def _get_mlb_live_scores(self, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """Get live scores from MLB API."""
        try:
            url = f"{self.mlb_base_url}/schedule"
            params = {
                "sportId": 1,  # MLB
                "date": "today",
                "fields": "dates,games,gamePk,teams,away,home,team,abbreviation,score,status,detailedState",
            }

            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return []

                data = await response.json()
                return self._parse_mlb_live_scores(data)

        except Exception as e:
            logger.error(f"Error getting MLB live scores: {e}")
            return []

    def _parse_mlb_team_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse MLB team stats from API response."""
        try:
            stats = data.get("stats", [])
            if not stats:
                return {}

            # Get the most recent stats
            stat = stats[0]
            splits = stat.get("splits", [])
            if not splits:
                return {}

            split = splits[0]
            stat_data = split.get("stat", {})

            return {
                "wins": stat_data.get("wins", 0),
                "losses": stat_data.get("losses", 0),
                "win_pct": stat_data.get("winPct", 0.0),
                "runs_scored": stat_data.get("runs", 0),
                "runs_allowed": stat_data.get("runsAllowed", 0),
                "run_diff": stat_data.get("runDifferential", 0),
                "games_played": stat_data.get("gamesPlayed", 0),
            }

        except Exception as e:
            logger.error(f"Error parsing MLB team stats: {e}")
            return {}

    def _parse_mlb_live_scores(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse MLB live scores from API response."""
        try:
            games = []
            dates = data.get("dates", [])

            for date in dates:
                for game in date.get("games", []):
                    away_team = game.get("teams", {}).get("away", {})
                    home_team = game.get("teams", {}).get("home", {})

                    games.append(
                        {
                            "away_team": away_team.get("team", {}).get("abbreviation", "TBD"),
                            "home_team": home_team.get("team", {}).get("abbreviation", "TBD"),
                            "away_score": away_team.get("score", 0),
                            "home_score": home_team.get("score", 0),
                            "status": game.get("status", {}).get("detailedState", "Unknown"),
                        }
                    )

            return games

        except Exception as e:
            logger.error(f"Error parsing MLB live scores: {e}")
            return []

    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
