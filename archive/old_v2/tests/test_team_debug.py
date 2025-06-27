#!/usr/bin/env python3
"""
Test script with proper logging to debug team lookup
"""
import asyncio
import logging
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


async def test_team_debug():
    """Test team lookup with proper logging"""
    try:
        from bot.services.player_analytics import PlayerAnalyticsService

        print("Initializing PlayerAnalyticsService...")
        service = PlayerAnalyticsService()

        print("Testing team lookup for 'Oakland Athletics'...")
        session = await service._get_session()
        team_id = await service._get_mlb_team_id(session, "Oakland Athletics")
        print(f"Final result: {team_id}")

        await service.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_team_debug())
