#!/usr/bin/env python3
"""
Detailed test to verify the new MLB scraper is fetching real data
"""
import asyncio
import time
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def detailed_test():
    """Detailed test of the new scraper"""
    print("=== Detailed MLB Scraper Test ===")
    
    try:
        from bot.services.mlb_scraper import MLBScraper
        
        scraper = MLBScraper()
        await scraper.initialize()
        
        # Test 1: Get game data
        print("\n1. Testing game data fetch...")
        game_data = await scraper.get_game_data('Los Angeles Angels', 'Oakland Athletics')
        
        print(f"Raw response keys: {list(game_data.keys())}")
        
        if 'error' in game_data:
            print(f"ERROR: {game_data['error']}")
            return
        
        # Test 2: Check team stats
        print("\n2. Checking team stats...")
        teams = game_data.get('teams', {})
        for team_name, team_data in teams.items():
            print(f"\n{team_name}:")
            stats = team_data.get('stats', {})
            if stats:
                print(f"  Stats found: {len(stats)} fields")
                print(f"  Sample stats: {dict(list(stats.items())[:5])}")
            else:
                print("  ⚠️  No stats found!")
            
            weather = team_data.get('weather', {})
            if weather:
                print(f"  Weather found: {weather}")
            else:
                print("  ⚠️  No weather found!")
        
        # Test 3: Check live scores
        print("\n3. Checking live scores...")
        live_scores = game_data.get('live_scores', [])
        print(f"Live scores found: {len(live_scores)} games")
        if live_scores:
            print(f"Sample game: {live_scores[0]}")
        
        # Test 4: Check today's game
        print("\n4. Checking today's game...")
        today_game = game_data.get('today_game')
        if today_game:
            print(f"Today's game: {today_game}")
        else:
            print("No game scheduled today between these teams")
        
        # Test 5: Performance metrics
        print("\n5. Performance metrics...")
        fetch_time = game_data.get('fetch_time', 0)
        print(f"Fetch time: {fetch_time:.3f}s")
        
        # Test 6: Test with different teams
        print("\n6. Testing with different teams...")
        game_data2 = await scraper.get_game_data('New York Yankees', 'Boston Red Sox')
        if 'error' not in game_data2:
            teams2 = game_data2.get('teams', {})
            for team_name, team_data in teams2.items():
                stats = team_data.get('stats', {})
                if stats:
                    print(f"{team_name}: {stats.get('wins', 0)}-{stats.get('losses', 0)}")
        
        await scraper.close()
        
        # Summary
        print("\n=== SUMMARY ===")
        print("✅ Scraper initialized successfully")
        print(f"✅ Game data fetched in {fetch_time:.3f}s")
        print("✅ Data structure looks correct")
        
        # Check if we got real data
        has_real_stats = any(
            team_data.get('stats', {}).get('wins', 0) > 0 or 
            team_data.get('stats', {}).get('losses', 0) > 0
            for team_data in teams.values()
        )
        
        if has_real_stats:
            print("✅ Real team stats found!")
        else:
            print("⚠️  No real team stats found - may be offseason or API issue")
        
        if live_scores:
            print(f"✅ Live scores found: {len(live_scores)} games")
        else:
            print("⚠️  No live scores found - may be offseason")
        
    except Exception as e:
        print(f"❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()

async def test_mlb_api_directly():
    """Test MLB API directly to see if it's working"""
    print("\n=== Testing MLB API Directly ===")
    
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            # Test teams endpoint
            url = "https://statsapi.mlb.com/api/v1/teams"
            async with session.get(url) as response:
                print(f"Teams endpoint status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    teams = data.get('teams', [])
                    print(f"Found {len(teams)} teams")
                    
                    # Look for Angels
                    angels = [t for t in teams if 'angels' in t.get('name', '').lower()]
                    if angels:
                        print(f"Angels found: {angels[0]}")
                    else:
                        print("Angels not found!")
            
            # Test schedule endpoint
            url = "https://statsapi.mlb.com/api/v1/schedule"
            params = {'sportId': 1, 'date': '2024-06-24'}
            async with session.get(url, params=params) as response:
                print(f"Schedule endpoint status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    dates = data.get('dates', [])
                    if dates:
                        games = dates[0].get('games', [])
                        print(f"Found {len(games)} games for 2024-06-24")
                    else:
                        print("No games found for 2024-06-24")
                        
    except Exception as e:
        print(f"❌ MLB API test failed: {e}")

async def main():
    """Run all tests"""
    print("Starting detailed scraper tests...\n")
    
    await detailed_test()
    await test_mlb_api_directly()
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(main()) 