#!/usr/bin/env python3
"""
Test script to verify the new MLB integrated service works with the pick command
"""
import asyncio
import os
import sys
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


async def test_integrated_service():
    """Test the new integrated service"""
    print("=== Testing MLB Integrated Service ===")

    try:
        from bot.services.mlb_integrated_service import MLBIntegratedService

        start_time = time.time()
        service = MLBIntegratedService()

        # Initialize
        init_start = time.time()
        success = await service.initialize()
        init_time = time.time() - init_start

        print(f"Initialization: {'SUCCESS' if success else 'FAILED'} ({init_time:.2f}s)")

        if success:
            # Test with sample bet data
            bet_data = {
                "teams": ["Los Angeles Angels", "Oakland Athletics"],
                "description": "Over 8.5 runs",
                "odds": -110,
                "stake": 100,
            }

            # Test getting comprehensive data
            data_start = time.time()
            game_data = await service.get_comprehensive_game_data(bet_data)
            data_time = time.time() - data_start

            print(f"Comprehensive data fetch: {'SUCCESS' if game_data else 'FAILED'} ({data_time:.2f}s)")

            if game_data:
                print(f"Summary: {game_data.get('summary', 'No summary')}")
                print(f"Performance: {game_data.get('performance_metrics', {})}")

                # Check team data
                team1_data = game_data.get("team1", {})
                team2_data = game_data.get("team2", {})

                if team1_data:
                    basic_stats = team1_data.get("basic_stats", {})
                    print(
                        f"Team 1 stats: {basic_stats.get('wins', 0)}-{basic_stats.get('losses', 0)} ({basic_stats.get('win_pct', 0):.3f})"
                    )

                if team2_data:
                    basic_stats = team2_data.get("basic_stats", {})
                    print(
                        f"Team 2 stats: {basic_stats.get('wins', 0)}-{basic_stats.get('losses', 0)} ({basic_stats.get('win_pct', 0):.3f})"
                    )

                # Check weather data
                weather = game_data.get("weather", {})
                if weather.get("available"):
                    print(f"Weather: {weather.get('summary', 'No summary')}")
                else:
                    print("Weather: Not available")

            await service.close()

        total_time = time.time() - start_time
        print(f"Total test time: {total_time:.2f}s")

    except Exception as e:
        print(f"Integration test FAILED: {e}")
        import traceback

        traceback.print_exc()


async def test_pick_command_integration():
    """Test the pick command integration"""
    print("\n=== Testing Pick Command Integration ===")

    try:
        from bot.services.mlb_integrated_service import MLBIntegratedService

        # Create sample bet data (like what OCR would extract)
        bet_data = {
            "teams": ["Los Angeles Angels", "Oakland Athletics"],
            "description": "Over 8.5 runs",
            "odds": -110,
            "stake": 100,
            "bet_type": "total",
        }

        # Test the service that the pick command would use
        service = MLBIntegratedService()
        await service.initialize()

        start_time = time.time()
        stats_data = await service.get_comprehensive_game_data(bet_data)
        fetch_time = time.time() - start_time

        print(f"Pick command data fetch: {'SUCCESS' if stats_data else 'FAILED'} ({fetch_time:.2f}s)")

        if stats_data:
            print("✅ Pick command integration successful!")
            print(
                f"Data structure matches expected format: {bool(stats_data.get('team1') and stats_data.get('team2'))}"
            )
            print(f"Performance metrics: {stats_data.get('performance_metrics', {})}")
        else:
            print("❌ Pick command integration failed - no data returned")

        await service.close()

    except Exception as e:
        print(f"Pick command integration test FAILED: {e}")
        import traceback

        traceback.print_exc()


async def main():
    """Run all integration tests"""
    print("Starting MLB integration tests...\n")

    await test_integrated_service()
    await test_pick_command_integration()

    print("\n=== Integration Test Summary ===")
    print("Integration tests completed. Check output above for any issues.")


if __name__ == "__main__":
    asyncio.run(main())
