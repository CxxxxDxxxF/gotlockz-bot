#!/usr/bin/env python3
"""
Debug script to test the exact team lookup function
"""
import asyncio
import os
import sys

import aiohttp

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


async def test_team_lookup():
    """Test the exact team lookup function from the analytics service"""
    try:
        from bot.services.player_analytics import PlayerAnalyticsService

        print("Initializing PlayerAnalyticsService...")
        service = PlayerAnalyticsService()

        print("Testing team lookup for 'Los Angeles Angels'...")
        session = await service._get_session()
        team_id = await service._get_mlb_team_id(session, "Los Angeles Angels")
        print(f"Result: {team_id}")

        print("Testing team lookup for 'Oakland Athletics'...")
        team_id2 = await service._get_mlb_team_id(session, "Oakland Athletics")
        print(f"Result: {team_id2}")

        await service.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_team_lookup())
