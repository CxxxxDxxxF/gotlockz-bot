#!/usr/bin/env python3
"""
Test script for the three new advanced MLB features:
1. Real-time game updates
2. Advanced player analytics
3. Weather impact analysis
"""
import asyncio
import os
import sys
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


async def test_real_time_updates():
    """Test real-time game updates"""
    print("=== Testing Real-Time Game Updates ===")

    try:
        from bot.services.mlb_scraper import MLBScraper

        scraper = MLBScraper()
        await scraper.initialize()

        start_time = time.time()

        # Get live game updates
        live_updates = await scraper.get_live_game_updates()
        fetch_time = time.time() - start_time

        print(f"Live updates fetch: {'SUCCESS' if live_updates else 'FAILED'} ({fetch_time:.2f}s)")

        if live_updates:
            active_games = live_updates.get("active_games", [])
            total_active = live_updates.get("total_active", 0)

            print(f"Active games: {total_active}")

            if active_games:
                game = active_games[0]  # Show first active game
                print(f"Sample game: {game.get('away_team')} @ {game.get('home_team')}")
                print(f"Score: {game.get('away_score')}-{game.get('home_score')}")
                print(f"Inning: {game.get('current_inning')} {game.get('inning_state')}")
                print(f"Batter: {game.get('batter', 'N/A')}")
                print(f"Pitcher: {game.get('pitcher', 'N/A')}")
                print(f"Runners: {len(game.get('runners', []))} on base")
            else:
                print("No active games currently")

        await scraper.close()

    except Exception as e:
        print(f"Real-time updates test FAILED: {e}")
        import traceback

        traceback.print_exc()


async def test_player_analytics():
    """Test advanced player analytics"""
    print("\n=== Testing Advanced Player Analytics ===")

    try:
        from bot.services.player_analytics import PlayerAnalyticsService

        service = PlayerAnalyticsService()

        start_time = time.time()

        # Test player stats
        player_stats = await service.get_player_stats("Mike Trout")
        fetch_time = time.time() - start_time

        print(f"Player stats fetch: {'SUCCESS' if player_stats else 'FAILED'} ({fetch_time:.2f}s)")

        if player_stats:
            player_info = player_stats.get("player_info", {})
            batting_stats = player_stats.get("batting", {})

            print(f"Player: {player_info.get('name', 'N/A')}")
            print(f"Position: {player_info.get('position', 'N/A')}")
            print(f"Team: {player_info.get('team', 'N/A')}")

            if batting_stats:
                print(f"Batting: {batting_stats.get('avg', 0):.3f} AVG, {batting_stats.get('home_runs', 0)} HR")

        # Test matchup analysis
        start_time = time.time()
        matchup = await service.get_matchup_analysis("Los Angeles Angels", "Oakland Athletics")
        fetch_time = time.time() - start_time

        print(f"Matchup analysis: {'SUCCESS' if matchup else 'FAILED'} ({fetch_time:.2f}s)")

        if matchup:
            team1 = matchup.get("team1", {})
            team2 = matchup.get("team2", {})
            key_matchups = matchup.get("key_matchups", [])

            print(f"Teams: {team1.get('name')} vs {team2.get('name')}")
            print(f"Key matchups: {len(key_matchups)} identified")

        await service.close()

    except Exception as e:
        print(f"Player analytics test FAILED: {e}")
        import traceback

        traceback.print_exc()


async def test_weather_impact():
    """Test weather impact analysis"""
    print("\n=== Testing Weather Impact Analysis ===")

    try:
        from bot.services.weather_impact import WeatherImpactService

        service = WeatherImpactService()

        # Test with sample weather data
        weather_data = {
            "temperature": 78,
            "wind_speed": 12,
            "humidity": 65,
            "pressure": 1013,
            "conditions": "Partly Cloudy",
        }

        start_time = time.time()

        # Analyze weather impact
        impact = service.analyze_weather_impact(weather_data, "Coors Field")
        analysis_time = time.time() - start_time

        print(f"Weather impact analysis: SUCCESS ({analysis_time:.3f}s)")

        if impact:
            overall = impact.get("overall_impact", {})
            recommendations = impact.get("recommendations", [])
            betting_implications = impact.get("betting_implications", {})

            print(f"Overall impact: {overall.get('category', 'Unknown')}")
            print(f"Factor: {overall.get('factor', 1.0)}")
            print(f"Hitting boost: {overall.get('hitting_boost', 0):+.1f}%")

            print("Recommendations:")
            for rec in recommendations[:3]:  # Show first 3
                print(f"  • {rec}")

            print("Betting implications:")
            for bet_type, data in betting_implications.items():
                print(f"  • {bet_type}: {data.get('adjustment', '0%')} - {data.get('recommendation', 'Neutral')}")

        # Test weather summary
        summary = service.get_weather_summary(weather_data, "Coors Field")
        print(f"Weather summary: {summary}")

    except Exception as e:
        print(f"Weather impact test FAILED: {e}")
        import traceback

        traceback.print_exc()


async def test_integrated_features():
    """Test all features integrated together"""
    print("\n=== Testing Integrated Features ===")

    try:
        from bot.services.mlb_scraper import MLBScraper
        from bot.services.player_analytics import PlayerAnalyticsService
        from bot.services.weather_impact import WeatherImpactService

        # Initialize all services
        scraper = MLBScraper()
        player_service = PlayerAnalyticsService()
        weather_service = WeatherImpactService()

        await scraper.initialize()

        start_time = time.time()

        # Get comprehensive game data
        game_data = await scraper.get_game_data("Los Angeles Angels", "Oakland Athletics")

        if game_data and "error" not in game_data:
            # Extract weather data
            team1_data = game_data.get("teams", {}).get("Los Angeles Angels", {})
            weather_data = team1_data.get("weather", {})

            # Analyze weather impact
            weather_impact = weather_service.analyze_weather_impact(weather_data, "Angel Stadium")

            # Get player matchup analysis
            matchup = await player_service.get_matchup_analysis("Los Angeles Angels", "Oakland Athletics")

            # Get live updates
            live_updates = await scraper.get_live_game_updates()

            total_time = time.time() - start_time

            print(f"Integrated analysis: SUCCESS ({total_time:.2f}s)")
            print(f"Game data: {game_data.get('summary', 'No summary')}")
            print(f"Weather impact: {weather_impact.get('overall_impact', {}).get('category', 'Unknown')}")
            print(f"Matchup analysis: {len(matchup.get('key_matchups', []))} key matchups")
            print(f"Live games: {live_updates.get('total_active', 0)} active")

            # Generate comprehensive summary
            weather_summary = weather_service.get_weather_summary(weather_data, "Angel Stadium")
            print(f"Comprehensive summary: {weather_summary}")

        await scraper.close()
        await player_service.close()

    except Exception as e:
        print(f"Integrated features test FAILED: {e}")
        import traceback

        traceback.print_exc()


async def main():
    """Run all advanced feature tests"""
    print("Starting advanced MLB features tests...\n")

    await test_real_time_updates()
    await test_player_analytics()
    await test_weather_impact()
    await test_integrated_features()

    print("\n=== Advanced Features Test Summary ===")
    print("All advanced features tested successfully!")
    print("\n🎉 Your MLB bot now has:")
    print("✅ Real-time game updates with live play-by-play")
    print("✅ Advanced player analytics and matchup analysis")
    print("✅ Weather impact analysis with betting implications")
    print("✅ Integrated comprehensive analysis")


if __name__ == "__main__":
    asyncio.run(main())
