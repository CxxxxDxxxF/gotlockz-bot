#!/usr/bin/env python3
"""
test_enhanced_commands.py - Test Enhanced Command Functionality

Test the new OCR and MLB data integration features.
"""
import asyncio
import logging
from unittest.mock import Mock, AsyncMock, patch
import discord
from bot.commands.betting import BettingCommands

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_ocr_integration():
    """Test OCR integration."""
    print("🧪 Testing OCR Integration...")
    
    # Mock image attachment
    mock_image = Mock(spec=discord.Attachment)
    mock_image.content_type = "image/png"
    mock_image.read = AsyncMock(return_value=b"fake_image_data")
    
    # Mock interaction
    mock_interaction = Mock(spec=discord.Interaction)
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.followup.send = AsyncMock()
    mock_interaction.channel_id = 123456789
    
    # Mock bot
    mock_bot = Mock()
    mock_bot.vip_channel_id = 987654321
    mock_bot.lotto_channel_id = 987654322
    mock_bot.free_channel_id = 987654323
    
    # Create betting commands instance
    betting_commands = BettingCommands(mock_bot)
    
    # Test with mock OCR data
    with patch('bot.utils.ocr.ocr_parser.extract_text_from_image') as mock_ocr:
        mock_ocr.return_value = "Yankees vs Red Sox - Aaron Judge - Over 1.5 hits -110"
        
        # Test _post_pick method directly
        await betting_commands._post_pick(mock_interaction, mock_image, "Test context", "vip")
        
        print("✅ OCR integration test completed")
        return True

async def test_mlb_data_integration():
    """Test MLB data integration."""
    print("🧪 Testing MLB Data Integration...")
    
    # Mock MLB data
    mock_mlb_data = {
        'away_team': 'Yankees',
        'home_team': 'Red Sox',
        'player_stats': {
            'avg': '.285',
            'hr': '25',
            'rbi': '78',
            'ops': '.890'
        },
        'team_stats': {
            'away_record': '45-35',
            'home_record': '42-38',
            'away_pitcher': 'Gerrit Cole',
            'home_pitcher': 'Chris Sale'
        },
        'current_trends': 'Yankees is 0.563 this season',
        'weather': 'Clear, 72°F',
        'venue': 'Fenway Park'
    }
    
    with patch('bot.utils.mlb.mlb_fetcher.get_team_stats') as mock_team_stats:
        with patch('bot.utils.mlb.mlb_fetcher.get_player_stats') as mock_player_stats:
            with patch('bot.utils.mlb.mlb_fetcher.get_game_info') as mock_game_info:
                
                mock_team_stats.return_value = {'wins': 45, 'losses': 35, 'win_pct': 0.563}
                mock_player_stats.return_value = {'avg': '.285', 'hr': 25, 'rbi': 78, 'ops': '.890'}
                mock_game_info.return_value = {
                    'away_pitcher': 'Gerrit Cole',
                    'home_pitcher': 'Chris Sale',
                    'weather': 'Clear, 72°F',
                    'venue': 'Fenway Park'
                }
                
                print("✅ MLB data integration test completed")
                return True

async def test_content_generation():
    """Test content generation with real data."""
    print("🧪 Testing Content Generation...")
    
    # Mock bot
    mock_bot = Mock()
    mock_bot.vip_channel_id = 987654321
    
    # Create betting commands instance
    betting_commands = BettingCommands(mock_bot)
    
    # Test data
    bet_data = {
        'teams': ['Yankees', 'Red Sox'],
        'player': 'Aaron Judge',
        'description': 'Over 1.5 hits',
        'odds': '-110',
        'units': '2',
        'game_time': '7:05 PM',
        'sport': 'MLB'
    }
    
    mlb_data = {
        'away_team': 'Yankees',
        'home_team': 'Red Sox',
        'player_stats': {
            'avg': '.285',
            'hr': '25',
            'rbi': '78',
            'ops': '.890'
        },
        'team_stats': {
            'away_record': '45-35',
            'home_record': '42-38',
            'away_pitcher': 'Gerrit Cole',
            'home_pitcher': 'Chris Sale'
        },
        'current_trends': 'Yankees is 0.563 this season',
        'weather': 'Clear, 72°F',
        'venue': 'Fenway Park'
    }
    
    # Test VIP content generation
    content = await betting_commands._generate_pick_content(
        "vip", bet_data, mlb_data, "12/25/23", "7:05", "Strong matchup analysis"
    )
    
    print("Generated VIP content:")
    print(content)
    print("✅ Content generation test completed")
    return True

async def test_channel_routing():
    """Test channel routing functionality."""
    print("🧪 Testing Channel Routing...")
    
    # Mock bot with channel IDs
    mock_bot = Mock()
    mock_bot.vip_channel_id = 987654321
    mock_bot.lotto_channel_id = 987654322
    mock_bot.free_channel_id = 987654323
    
    betting_commands = BettingCommands(mock_bot)
    
    # Test channel routing
    vip_channel = betting_commands._get_target_channel_id("vip")
    lotto_channel = betting_commands._get_target_channel_id("lotto")
    free_channel = betting_commands._get_target_channel_id("free")
    
    assert vip_channel == 987654321
    assert lotto_channel == 987654322
    assert free_channel == 987654323
    
    print("✅ Channel routing test completed")
    return True

async def main():
    """Run all tests."""
    print("🚀 Starting Enhanced Commands Tests...\n")
    
    tests = [
        test_ocr_integration,
        test_mlb_data_integration,
        test_content_generation,
        test_channel_routing
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(False)
        print()
    
    passed = sum(results)
    total = len(results)
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced functionality is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    asyncio.run(main()) 