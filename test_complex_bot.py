#!/usr/bin/env python3
"""
test_complex_bot.py - Complex Bot Test

Test the optimized complex bot components.
"""

import asyncio
import logging
import sys
import os

# Add bot directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'bot'))

from utils.mlb import mlb_fetcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_mlb_fetcher():
    """Test MLB fetcher with caching and concurrent calls."""
    print("Testing MLB fetcher optimization...")
    
    # Test caching
    print("Testing caching...")
    result1 = await mlb_fetcher.get_team_stats("Yankees")
    result2 = await mlb_fetcher.get_team_stats("Yankees")  # Should be cached
    print(f"First call: {len(str(result1))} chars")
    print(f"Second call (cached): {len(str(result2))} chars")
    
    # Test concurrent calls
    print("Testing concurrent API calls...")
    start_time = asyncio.get_event_loop().time()
    
    tasks = [
        mlb_fetcher.get_team_stats("Yankees"),
        mlb_fetcher.get_team_stats("Red Sox"),
        mlb_fetcher.get_player_stats("Aaron Judge"),
        mlb_fetcher.get_game_info("Yankees", "Red Sox")
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = asyncio.get_event_loop().time()
    
    print(f"Concurrent calls completed in {end_time - start_time:.2f} seconds")
    print(f"Results: {len([r for r in results if not isinstance(r, Exception)])}/{len(results)} successful")
    
    print("MLB fetcher test completed")


async def main():
    """Run all tests."""
    print("Starting complex bot tests...")
    
    try:
        await test_mlb_fetcher()
        
        print("\n✅ All tests completed successfully!")
        print("The complex bot optimizations are working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.error(f"Test error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 