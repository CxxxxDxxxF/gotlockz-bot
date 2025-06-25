#!/usr/bin/env python3
"""
Test script for the new improved MLB scraper
"""
import asyncio
import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_new_scraper():
    """Test the new MLB scraper"""
    print("=== Testing New MLB Scraper ===")
    
    try:
        from bot.services.mlb_scraper import MLBScraper
        
        start_time = time.time()
        scraper = MLBScraper()
        
        # Initialize
        init_start = time.time()
        success = await scraper.initialize()
        init_time = time.time() - init_start
        
        print(f"Initialization: {'SUCCESS' if success else 'FAILED'} ({init_time:.2f}s)")
        
        if success:
            # Test getting game data
            data_start = time.time()
            game_data = await scraper.get_game_data('Los Angeles Angels', 'Oakland Athletics')
            data_time = time.time() - data_start
            
            print(f"Game data fetch: {'SUCCESS' if 'error' not in game_data else 'FAILED'} ({data_time:.2f}s)")
            
            if 'error' not in game_data:
                print(f"Summary: {game_data.get('summary', 'No summary')}")
                print(f"Fetch time: {game_data.get('fetch_time', 0):.2f}s")
                
                # Show team stats
                teams = game_data.get('teams', {})
                for team_name, team_data in teams.items():
                    stats = team_data.get('stats', {})
                    if stats:
                        print(f"{team_name}: {stats.get('wins', 0)}-{stats.get('losses', 0)} ({stats.get('win_pct', 0):.3f})")
                
                # Show today's game if exists
                today_game = game_data.get('today_game')
                if today_game:
                    print(f"Today's game: {today_game.get('away_team')} @ {today_game.get('home_team')} - {today_game.get('status')}")
                else:
                    print("No game scheduled today between these teams")
            
            await scraper.close()
        
        total_time = time.time() - start_time
        print(f"Total test time: {total_time:.2f}s")
        
    except Exception as e:
        print(f"New scraper test FAILED: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run the test"""
    print("Starting new MLB scraper test...\n")
    
    await test_new_scraper()
    
    print("\n=== Test Summary ===")
    print("New scraper test completed.")

if __name__ == "__main__":
    asyncio.run(main()) 