#!/usr/bin/env python3
"""
Comprehensive test to verify stats pulling functionality
"""
import asyncio
import sys
import os
import json

# Add the bot directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'bot'))

from utils.mlb import MLBDataFetcher

async def test_comprehensive_stats():
    """Test all stats pulling methods comprehensively"""
    print("🔍 COMPREHENSIVE STATS TEST")
    print("=" * 50)
    
    fetcher = MLBDataFetcher()
    
    # Test 1: Basic team stats
    print("\n1️⃣ Testing Team Stats (Yankees):")
    try:
        team_stats = await fetcher.get_team_stats("Yankees")
        if team_stats:
            print(f"✅ Team stats found: {len(team_stats)} fields")
            print(f"   Sample data: {list(team_stats.keys())[:5]}")
        else:
            print("❌ No team stats returned")
    except Exception as e:
        print(f"❌ Team stats error: {e}")
    
    # Test 2: Player stats
    print("\n2️⃣ Testing Player Stats (Aaron Judge):")
    try:
        player_stats = await fetcher.get_player_stats("Aaron Judge")
        if player_stats:
            print(f"✅ Player stats found: {len(player_stats)} fields")
            print(f"   Sample data: {list(player_stats.keys())[:5]}")
        else:
            print("❌ No player stats returned")
    except Exception as e:
        print(f"❌ Player stats error: {e}")
    
    # Test 3: Live scores
    print("\n3️⃣ Testing Live Scores:")
    try:
        live_scores = await fetcher.get_live_scores()
        if live_scores and live_scores.get('live_games'):
            print(f"✅ Live games found: {len(live_scores['live_games'])}")
            for game in live_scores['live_games'][:3]:  # Show first 3
                print(f"   {game.get('away_team', '?')} {game.get('away_score', '?')} - {game.get('home_score', '?')} {game.get('home_team', '?')}")
        else:
            print("❌ No live games found (may be off-season)")
    except Exception as e:
        print(f"❌ Live scores error: {e}")
    
    # Test 4: MLB.com scraping
    print("\n4️⃣ Testing MLB.com Scraping:")
    try:
        scraped_data = await fetcher.scrape_mlb_live_stats()
        if scraped_data:
            print(f"✅ Scraped data found:")
            print(f"   Live games: {len(scraped_data.get('live_games', []))}")
            print(f"   Team stats: {len(scraped_data.get('team_stats', []))}")
            print(f"   Player stats: {len(scraped_data.get('player_stats', []))}")
            print(f"   Source: {scraped_data.get('source', 'unknown')}")
            
            # Show sample scraped data
            if scraped_data.get('team_stats'):
                print(f"   Sample team: {scraped_data['team_stats'][0] if scraped_data['team_stats'] else 'None'}")
            if scraped_data.get('player_stats'):
                print(f"   Sample player: {scraped_data['player_stats'][0] if scraped_data['player_stats'] else 'None'}")
        else:
            print("❌ No scraped data returned")
    except Exception as e:
        print(f"❌ Scraping error: {e}")
    
    # Test 5: Fallback method
    print("\n5️⃣ Testing Fallback Method:")
    try:
        fallback_data = await fetcher.get_live_stats_with_fallback("Yankees")
        if fallback_data:
            print(f"✅ Fallback data found:")
            print(f"   Source: {fallback_data.get('source', 'unknown')}")
            print(f"   Live games: {len(fallback_data.get('live_games', []))}")
            if fallback_data.get('live_games'):
                for game in fallback_data['live_games'][:2]:
                    print(f"   {game.get('away_team', '?')} {game.get('away_score', '?')} - {game.get('home_score', '?')} {game.get('home_team', '?')}")
        else:
            print("❌ No fallback data returned")
    except Exception as e:
        print(f"❌ Fallback error: {e}")
    
    # Test 6: Game info
    print("\n6️⃣ Testing Game Info (Yankees vs Red Sox):")
    try:
        game_info = await fetcher.get_game_info("Yankees", "Red Sox")
        if game_info:
            print(f"✅ Game info found: {len(game_info)} fields")
            print(f"   Sample data: {list(game_info.keys())[:5]}")
        else:
            print("❌ No game info returned")
    except Exception as e:
        print(f"❌ Game info error: {e}")
    
    # Test 7: Simulate betting command data fetch
    print("\n7️⃣ Testing Betting Command Data Fetch:")
    try:
        bet_data = {
            'teams': ['Yankees', 'Red Sox'],
            'player': 'Aaron Judge',
            'description': 'Home Run',
            'odds': '+150'
        }
        
        # This simulates what the betting command does
        from commands.betting import BettingCommands
        betting_cmd = BettingCommands(None)  # No bot instance needed for this test
        
        mlb_data = await betting_cmd._fetch_mlb_data(bet_data)
        if mlb_data:
            print(f"✅ Betting command data fetch successful:")
            print(f"   Away team stats: {'Yes' if mlb_data.get('away_team_stats') else 'No'}")
            print(f"   Home team stats: {'Yes' if mlb_data.get('home_team_stats') else 'No'}")
            print(f"   Player stats: {'Yes' if mlb_data.get('player_stats') else 'No'}")
            print(f"   Live data: {'Yes' if mlb_data.get('live_data') else 'No'}")
            print(f"   Game info: {'Yes' if mlb_data.get('game_info') else 'No'}")
        else:
            print("❌ Betting command data fetch failed")
    except Exception as e:
        print(f"❌ Betting command test error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 COMPREHENSIVE TEST COMPLETE")

if __name__ == "__main__":
    asyncio.run(test_comprehensive_stats()) 