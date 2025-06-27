#!/usr/bin/env python3
"""
Test script to check the performance of weather and stats scrapers
"""
import asyncio
import time
import sys
import os
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_weather_scraper():
    """Test the weather scraper performance"""
    print("=== Testing Weather Scraper ===")
    
    try:
        from bot.services.weather import WeatherService
        
        start_time = time.time()
        weather_service = WeatherService()
        
        # Test initialization
        init_start = time.time()
        success = await weather_service.initialize()
        init_time = time.time() - init_start
        
        print(f"Initialization: {'SUCCESS' if success else 'FAILED'} ({init_time:.2f}s)")
        
        if success:
            # Test getting weather for a team
            weather_start = time.time()
            weather_data = await weather_service.get_weather_for_teams(['Los Angeles Angels'])
            weather_time = time.time() - weather_start
            
            print(f"Weather data fetch: {'SUCCESS' if weather_data else 'FAILED'} ({weather_time:.2f}s)")
            if weather_data:
                print(f"Data received: {weather_data}")
            
            await weather_service.close()
        
        total_time = time.time() - start_time
        print(f"Total weather test time: {total_time:.2f}s")
        
    except Exception as e:
        print(f"Weather scraper test FAILED: {e}")
        import traceback
        traceback.print_exc()

async def test_stats_service():
    """Test the stats service performance"""
    print("\n=== Testing Stats Service ===")
    
    try:
        from bot.services.stats import StatsService
        
        start_time = time.time()
        stats_service = StatsService()
        
        # Test getting team stats
        stats_start = time.time()
        team_stats = await stats_service.get_team_stats('Los Angeles Angels')
        stats_time = time.time() - stats_start
        
        print(f"Team stats fetch: {'SUCCESS' if team_stats else 'FAILED'} ({stats_time:.2f}s)")
        if team_stats:
            print(f"Stats received: {team_stats}")
        
        # Test getting live scores
        scores_start = time.time()
        live_scores = await stats_service.get_live_scores()
        scores_time = time.time() - scores_start
        
        print(f"Live scores fetch: {'SUCCESS' if live_scores else 'FAILED'} ({scores_time:.2f}s)")
        if live_scores:
            print(f"Scores received: {len(live_scores)} games")
        
        await stats_service.close()
        
        total_time = time.time() - start_time
        print(f"Total stats test time: {total_time:.2f}s")
        
    except Exception as e:
        print(f"Stats service test FAILED: {e}")
        import traceback
        traceback.print_exc()

async def test_statcast_service():
    """Test the statcast service performance"""
    print("\n=== Testing Statcast Service ===")
    
    try:
        from bot.services.statcast import StatcastService
        
        start_time = time.time()
        statcast_service = StatcastService()
        
        # Test getting statcast data
        data_start = time.time()
        statcast_data = await statcast_service.get_statcast_data('Los Angeles Angels', 'Oakland Athletics')
        data_time = time.time() - data_start
        
        print(f"Statcast data fetch: {'SUCCESS' if statcast_data else 'FAILED'} ({data_time:.2f}s)")
        if statcast_data:
            print(f"Data received: {statcast_data.get('summary', 'No summary')}")
        
        await statcast_service.close()
        
        total_time = time.time() - start_time
        print(f"Total statcast test time: {total_time:.2f}s")
        
    except Exception as e:
        print(f"Statcast service test FAILED: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all scraper tests"""
    print("Starting scraper performance tests...\n")
    
    await test_weather_scraper()
    await test_stats_service()
    await test_statcast_service()
    
    print("\n=== Test Summary ===")
    print("All tests completed. Check output above for performance issues.")

if __name__ == "__main__":
    asyncio.run(main()) 