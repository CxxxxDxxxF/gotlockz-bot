#!/usr/bin/env python3
"""
Debug script to test team name matching
"""
import asyncio
import logging

from bot.services.mlb_scraper import MLBScraper

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_team_names():
    """Test team name matching functionality."""
    scraper = MLBScraper()

    # Get all MLB teams
    mlb_teams = scraper.team_mapping.keys()

    logger.info("All MLB teams:")
    for team in scraper.team_mapping.values():
        logger.info(f"  {team.get('id')}: '{team.get('abbr')}'")

    logger.info("\nTesting our search terms:")

    # Test some common search terms
    test_terms = ["Yankees", "Red Sox", "Dodgers", "Giants", "Cubs", "White Sox"]

    for test_team in test_terms:
        team = scraper.team_mapping.get(test_team)
        if team:
            logger.info(f"  ✓ Found '{test_team}' -> ID {team.get('id')}")
        else:
            # Find similar names
            similar = [name for name in mlb_teams if test_team.lower() in name.lower()]
            logger.warning(f"  ✗ NOT FOUND: '{test_team}'")
            logger.info(f"    Similar names: {similar}")


if __name__ == "__main__":
    asyncio.run(test_team_names())
