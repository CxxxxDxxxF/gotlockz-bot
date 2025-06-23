#!/usr/bin/env python3
"""
Test MLB scraping functionality
"""
import asyncio
import sys
import os

# Add the bot directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'bot'))

from utils.mlb import MLBDataFetcher

async def test_mlb_scraping():
    """Test the MLB scraping functionality"""
    print("Testing MLB scraping functionality...")
    
    fetcher = MLBDataFetcher()
    
    try:
        # Test scraping live stats
        print("1. Testing MLB.com live stats scraping...")
        scraped_data = await fetcher.scrape_mlb_live_stats()
        
        if scraped_data:
            print(f"✅ Successfully scraped data from MLB.com")
            print(f"   Source: {scraped_data.get('source', 'unknown')}")
            print(f"   Live games found: {len(scraped_data.get('live_games', []))}")
            print(f"   Team stats found: {len(scraped_data.get('team_stats', []))}")
            print(f"   Player stats found: {len(scraped_data.get('player_stats', []))}")
            
            # Show sample data
            if scraped_data.get('live_games'):
                print(f"   Sample live game: {scraped_data['live_games'][0]}")
        else:
            print("❌ No data scraped from MLB.com")
        
        # Test fallback method
        print("\n2. Testing fallback method...")
        fallback_data = await fetcher.get_live_stats_with_fallback()
        
        if fallback_data:
            print(f"✅ Fallback method returned data")
            print(f"   Source: {fallback_data.get('source', 'unknown')}")
            print(f"   Live games: {len(fallback_data.get('live_games', []))}")
        else:
            print("❌ Fallback method failed")
        
        # Test team-specific scraping
        print("\n3. Testing team-specific scraping...")
        team_data = await fetcher.scrape_mlb_live_stats("Yankees")
        
        if team_data:
            print(f"✅ Team-specific scraping successful")
            print(f"   Team stats: {len(team_data.get('team_stats', []))}")
            print(f"   Player stats: {len(team_data.get('player_stats', []))}")
        else:
            print("❌ Team-specific scraping failed")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mlb_scraping()) 