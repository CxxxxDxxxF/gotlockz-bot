#!/usr/bin/env python3
"""
Test script for Advanced Stats Service
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bot.services.advanced_stats import AdvancedStatsService
from bot.services.analysis import AnalysisService


async def test_advanced_stats():
    """Test the advanced stats service."""
    print("🧪 Testing Advanced Stats Service...")
    
    # Initialize services
    advanced_stats = AdvancedStatsService()
    analysis = AnalysisService()
    
    try:
        # Test data
        bet_data = {
            'teams': ['Los Angeles Angels', 'Oakland Athletics'],
            'description': 'Over 8.5 Total Runs',
            'odds': '-110',
            'is_parlay': False
        }
        
        print(f"📊 Testing with bet data: {bet_data}")
        
        # Get advanced stats
        print("🔍 Fetching advanced stats...")
        stats_data = await advanced_stats.get_advanced_stats(bet_data)
        
        if stats_data:
            print("✅ Advanced stats fetched successfully!")
            print(f"📈 Team 1 stats: {stats_data.get('team1', {})}")
            print(f"📈 Team 2 stats: {stats_data.get('team2', {})}")
            print(f"🏟️ Park factors: {stats_data.get('park_factors', {})}")
            print(f"🌤️ Weather: {stats_data.get('weather', {})}")
            
            # Test AI analysis with advanced stats
            print("\n🤖 Testing AI analysis with advanced stats...")
            analysis_result = await analysis.generate_analysis(bet_data, stats_data)
            print(f"✅ AI Analysis generated: {len(analysis_result)} characters")
            print(f"📝 Preview: {analysis_result[:200]}...")
            
        else:
            print("⚠️ No advanced stats returned")
            
            # Test basic stats as fallback
            print("🔄 Testing basic stats fallback...")
            from bot.services.stats import StatsService
            basic_stats = StatsService()
            basic_stats_data = await basic_stats.get_live_stats(bet_data)
            
            if basic_stats_data:
                print("✅ Basic stats fetched successfully!")
                print(f"📈 Basic stats: {basic_stats_data}")
            else:
                print("❌ No basic stats available either")
        
    except Exception as e:
        print(f"❌ Error testing advanced stats: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        await advanced_stats.close()
        print("🧹 Cleanup completed")


if __name__ == "__main__":
    asyncio.run(test_advanced_stats()) 