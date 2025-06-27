#!/usr/bin/env python3
"""
Debug script for player analytics service
"""
import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


async def debug_player_analytics():
    """Debug the player analytics service"""
    try:
        from bot.services.player_analytics import PlayerAnalyticsService

        print("Initializing PlayerAnalyticsService...")
        service = PlayerAnalyticsService()

        print("Testing player analytics for 'Mike Trout'...")
        result = await service.get_player_analytics("Mike Trout", "Los Angeles Angels")

        if result:
            print("✅ Player analytics successful!")
            print(f"Player: {result.get('player_name', 'N/A')} ({result.get('team', 'N/A')})")
            print(f"Stats: {result.get('stats', {})}")
        else:
            print("❌ Player analytics failed - returned None or empty dict")

        print("Testing matchup analysis...")
        matchup = await service.get_matchup_analysis("Los Angeles Angels", "Oakland Athletics")

        if matchup:
            print("✅ Matchup analysis successful!")
            print(
                f"Teams: {matchup.get('team1', {}).get('name', 'N/A')} vs {matchup.get('team2', {}).get('name', 'N/A')}"
            )
            print(f"Analysis: {matchup.get('analysis', '')}")
        else:
            print("❌ Matchup analysis failed - returned empty dict")

        await service.close()

    except Exception as e:
        print(f"❌ Error in player analytics: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_player_analytics())
