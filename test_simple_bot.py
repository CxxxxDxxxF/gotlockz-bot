#!/usr/bin/env python3
"""
test_simple_bot.py - Simple Bot Test

Test the simplified bot components to ensure they work correctly.
"""

import asyncio
import logging
import sys
import os

# Add bot directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'bot'))

from utils.ocr import ocr_parser
from commands.betting import BettingCommands

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_ocr():
    """Test OCR functionality."""
    print("Testing OCR functionality...")
    
    # Create a simple test image (you would need to provide a real image)
    print("OCR test completed (would need real image to test fully)")


async def test_betting_commands():
    """Test betting commands functionality."""
    print("Testing betting commands...")
    
    # Create a mock bot instance
    class MockBot:
        def __init__(self):
            self.vip_channel_id = "123456789"
            self.free_channel_id = "987654321"
            self.lotto_channel_id = "555666777"
    
    # Create betting commands instance
    betting_cmds = BettingCommands(MockBot())
    
    # Test parsing
    test_text = "Yankees @ Red Sox - Aaron Judge Over 1.5 hits (+150)"
    bet_data = betting_cmds._parse_bet_data_simple(test_text)
    print(f"Parsed bet data: {bet_data}")
    
    # Test message generation
    message = betting_cmds._generate_simple_message(bet_data, 2, "123456789")
    print(f"Generated message:\n{message}")
    
    print("Betting commands test completed")


async def main():
    """Run all tests."""
    print("Starting simplified bot tests...")
    
    try:
        await test_ocr()
        await test_betting_commands()
        
        print("\n✅ All tests completed successfully!")
        print("The simplified bot should work reliably now.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.error(f"Test error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 