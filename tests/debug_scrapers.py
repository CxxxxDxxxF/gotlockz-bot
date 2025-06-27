#!/usr/bin/env python3
"""
Debug script to identify specific issues with weather and stats scrapers
"""
import asyncio
import time
import sys
import os
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def debug_weather_scraper():
    """Debug the weather scraper issues"""
    print("=== Debugging Weather Scraper ===")
    
    try:
        from bot.services.weather import WeatherService
        
        weather_service = WeatherService()
        print(f"Weather service created. Available: {weather_service.weather_available}")
        
        # Test initialization
        success = await weather_service.initialize()
        print(f"Initialization result: {success}")
        
        if success:
            # Test getting weather for a specific station
            print("Testing weather fetch for Angel Stadium...")
            weather_data = await weather_service.get_weather_for_teams(['Los Angeles Angels'])
            print(f"Weather data result: {weather_data}")
            
            await weather_service.close()
        
    except Exception as e:
        print(f"Weather scraper debug error: {e}")
        import traceback
        traceback.print_exc()

async def debug_stats_service():
    """Debug the stats service issues"""
    print("\n=== Debugging Stats Service ===")
    
    try:
        from bot.services.stats import StatsService
        
        stats_service = StatsService()
        
        # Test MLB API directly
        print("Testing MLB API connection...")
        session = await stats_service._get_session()
        
        # Test teams endpoint
        url = f"{stats_service.mlb_base_url}/teams"
        print(f"Testing URL: {url}")
        
        async with session.get(url) as response:
            print(f"Response status: {response.status}")
            if response.status == 200:
                data = await response.json()
                print(f"Teams found: {len(data.get('teams', []))}")
                
                # Look for Angels
                for team in data.get('teams', []):
                    if 'angels' in team.get('name', '').lower():
                        print(f"Found Angels: {team}")
                        break
            else:
                print(f"Error response: {await response.text()}")
        
        await stats_service.close()
        
    except Exception as e:
        print(f"Stats service debug error: {e}")
        import traceback
        traceback.print_exc()

async def debug_statcast_service():
    """Debug the statcast service performance"""
    print("\n=== Debugging Statcast Service ===")
    
    try:
        from bot.services.statcast import StatcastService
        
        statcast_service = StatcastService()
        
        # Test a smaller data fetch
        print("Testing Statcast data fetch...")
        start_time = time.time()
        
        # Test with just one team first
        team_data = await statcast_service._get_team_statcast('LAA', 2024)
        fetch_time = time.time() - start_time
        
        print(f"Statcast fetch time: {fetch_time:.2f}s")
        print(f"Data received: {bool(team_data)}")
        
        if team_data:
            print(f"Batting stats: {bool(team_data.get('batting'))}")
            print(f"Pitching stats: {bool(team_data.get('pitching'))}")
        
        await statcast_service.close()
        
    except Exception as e:
        print(f"Statcast service debug error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all debug tests"""
    print("Starting scraper debug tests...\n")
    
    await debug_weather_scraper()
    await debug_stats_service()
    await debug_statcast_service()
    
    print("\n=== Debug Summary ===")
    print("Debug tests completed.")

if __name__ == "__main__":
    asyncio.run(main()) 