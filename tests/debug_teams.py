#!/usr/bin/env python3
"""
Debug script to test team data fetching
"""
import asyncio
import logging
from src.bot.services.mlb_scraper import MLBScraper

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_teams():
    """Test team data fetching."""
    scraper = MLBScraper()
    
    # Get all MLB teams
    mlb_teams = scraper.team_mapping.values()
    
    logger.info("MLB Teams (2024):")
    for team in mlb_teams:
        logger.info(f"{team.get('id')}: {team.get('abbr')}")
    logger.info(f"Total MLB teams: {len(mlb_teams)}")

if __name__ == "__main__":
    asyncio.run(test_teams()) 