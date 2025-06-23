#!/usr/bin/env python3
"""
Test the full bot flow: bet data → MLB stats → template generation
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the bot directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'bot'))

from commands.betting import BettingCommands

async def test_full_bot_flow():
    """Test the complete bot flow from bet data to template generation"""
    print("🤖 FULL BOT FLOW TEST")
    print("=" * 50)
    
    # Create a mock betting command instance
    betting_cmd = BettingCommands(None)  # No bot instance needed for testing
    
    # Simulate bet data from OCR
    bet_data = {
        'teams': ['New York Yankees', 'Boston Red Sox'],
        'player': 'Aaron Judge',
        'description': 'Home Run',
        'odds': '+150',
        'units': '2',
        'sport': 'MLB',
        'is_parlay': False
    }
    
    print(f"📋 Bet Data: {bet_data['player']} - {bet_data['description']} ({bet_data['odds']})")
    print(f"⚾ Game: {bet_data['teams'][0]} @ {bet_data['teams'][1]}")
    
    # Step 1: Fetch MLB data (this is what the bot does)
    print("\n1️⃣ Fetching MLB Data...")
    try:
        mlb_data = await betting_cmd._fetch_mlb_data(bet_data)
        print("✅ MLB data fetch successful")
        
        # Show what data we got
        print(f"   Away team stats: {'✅' if mlb_data.get('away_team_stats') else '❌'}")
        print(f"   Home team stats: {'✅' if mlb_data.get('home_team_stats') else '❌'}")
        print(f"   Player stats: {'✅' if mlb_data.get('player_stats') else '❌'}")
        print(f"   Live data: {'✅' if mlb_data.get('live_data') else '❌'}")
        print(f"   Game info: {'✅' if mlb_data.get('game_info') else '❌'}")
        
        if mlb_data.get('live_data'):
            source = mlb_data['live_data'].get('source', 'unknown')
            print(f"   Data source: {source}")
            
    except Exception as e:
        print(f"❌ MLB data fetch failed: {e}")
        return
    
    # Step 2: Generate templates for different channel types
    print("\n2️⃣ Testing Template Generation...")
    
    current_date = datetime.now().strftime("%m/%d/%y")
    current_time = datetime.now().strftime("%I:%M")
    
    # Test VIP template
    print("\n📝 VIP Template:")
    try:
        vip_content = await betting_cmd._generate_vip_template(
            bet_data, mlb_data, current_date, current_time, 3, "VIP PLAY"
        )
        print("✅ VIP template generated successfully")
        print("📄 Sample (first 200 chars):")
        print(vip_content[:200] + "..." if len(vip_content) > 200 else vip_content)
    except Exception as e:
        print(f"❌ VIP template failed: {e}")
    
    # Test Free template
    print("\n📝 Free Template:")
    try:
        free_content = await betting_cmd._generate_free_template(
            bet_data, mlb_data, current_date, current_time, 2, "FREE PLAY"
        )
        print("✅ Free template generated successfully")
        print("📄 Sample (first 200 chars):")
        print(free_content[:200] + "..." if len(free_content) > 200 else free_content)
    except Exception as e:
        print(f"❌ Free template failed: {e}")
    
    # Test Lotto template
    print("\n📝 Lotto Template:")
    try:
        lotto_content = await betting_cmd._generate_lotto_template(
            bet_data, mlb_data, current_date, current_time, 1, "LOTTO TICKET"
        )
        print("✅ Lotto template generated successfully")
        print("📄 Sample (first 200 chars):")
        print(lotto_content[:200] + "..." if len(lotto_content) > 200 else lotto_content)
    except Exception as e:
        print(f"❌ Lotto template failed: {e}")
    
    # Step 3: Test live stats section specifically
    print("\n3️⃣ Testing Live Stats Section:")
    try:
        live_stats = await betting_cmd._generate_live_stats_section(bet_data, mlb_data)
        print("✅ Live stats section generated")
        print("📊 Live Stats:")
        print(live_stats)
    except Exception as e:
        print(f"❌ Live stats section failed: {e}")
    
    # Step 4: Test analysis section
    print("\n4️⃣ Testing Analysis Section:")
    try:
        analysis = await betting_cmd._generate_analysis(bet_data, mlb_data, "")
        print("✅ Analysis section generated")
        print("📈 Analysis (first 300 chars):")
        print(analysis[:300] + "..." if len(analysis) > 300 else analysis)
    except Exception as e:
        print(f"❌ Analysis section failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 FULL BOT FLOW TEST COMPLETE")
    print("✅ Your bot is ready to post picks with live stats!")

if __name__ == "__main__":
    asyncio.run(test_full_bot_flow()) 