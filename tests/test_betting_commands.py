#!/usr/bin/env python3
"""
test_betting_commands.py - Unit Tests for Betting Commands

Comprehensive test suite for betting commands including OCR, MLB data,
and template generation.
"""

import pytest
import asyncio
import json
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import discord
from datetime import datetime

# Import the betting commands
from bot.commands.betting import BettingCommands

class TestBettingCommands:
    """Test suite for BettingCommands class."""
    
    @pytest.fixture
    def mock_bot(self):
        """Create a mock bot instance."""
        bot = Mock()
        bot.vip_channel_id = 123456789
        bot.free_channel_id = 987654321
        bot.lotto_channel_id = 555666777
        return bot
    
    @pytest.fixture
    def betting_commands(self, mock_bot):
        """Create BettingCommands instance with mock bot."""
        return BettingCommands(mock_bot)
    
    @pytest.fixture
    def mock_interaction(self):
        """Create a mock Discord interaction."""
        interaction = Mock(spec=discord.Interaction)
        interaction.response.defer = AsyncMock()
        interaction.followup.send = AsyncMock()
        interaction.channel_id = 123456789
        interaction.user = Mock()
        interaction.user.name = "TestUser"
        return interaction
    
    @pytest.fixture
    def mock_image(self):
        """Create a mock image attachment."""
        image = Mock(spec=discord.Attachment)
        image.content_type = "image/png"
        image.read = AsyncMock(return_value=b"fake_image_data")
        image.to_file = AsyncMock(return_value=Mock())
        return image
    
    def test_load_counters_new_file(self, betting_commands, tmp_path):
        """Test loading counters when file doesn't exist."""
        # Mock the file path to use a temporary directory
        with patch.object(betting_commands, '_load_counters') as mock_load:
            betting_commands._load_counters()
            assert betting_commands.pick_counters == {"vip": 0, "free": 0, "lotto": 0}
    
    def test_save_counters(self, betting_commands, tmp_path):
        """Test saving counters to file."""
        # Set some test counters
        betting_commands.pick_counters = {"vip": 5, "free": 3, "lotto": 2}
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            betting_commands._save_counters()
            
            # Verify file was opened and data was written
            mock_open.assert_called_once()
            mock_file.write.assert_called()
    
    @pytest.mark.asyncio
    async def test_analyze_betting_slip_success(self, betting_commands, mock_image):
        """Test successful betting slip analysis."""
        with patch.object(betting_commands, '_extract_text_from_image') as mock_extract:
            with patch.object(betting_commands, '_parse_bet_details') as mock_parse:
                mock_extract.return_value = "Yankees vs Red Sox - Aaron Judge - Over 1.5 hits -110"
                mock_parse.return_value = {
                    'teams': ['Yankees', 'Red Sox'],
                    'player': 'Aaron Judge',
                    'description': 'Over 1.5 hits',
                    'odds': '-110',
                    'units': '2'
                }
                
                result = await betting_commands._analyze_betting_slip(mock_image)
                
                assert result['teams'] == ['Yankees', 'Red Sox']
                assert result['player'] == 'Aaron Judge'
                assert result['odds'] == '-110'
    
    @pytest.mark.asyncio
    async def test_analyze_betting_slip_failure(self, betting_commands, mock_image):
        """Test betting slip analysis with error handling."""
        with patch.object(betting_commands, '_extract_text_from_image') as mock_extract:
            mock_extract.side_effect = Exception("OCR failed")
            
            result = await betting_commands._analyze_betting_slip(mock_image)
            
            # Should return default values
            assert result['teams'] == ['TBD', 'TBD']
            assert result['player'] == 'TBD'
            assert result['odds'] == 'TBD'
    
    @pytest.mark.asyncio
    async def test_fetch_mlb_data_success(self, betting_commands):
        """Test successful MLB data fetching."""
        bet_data = {
            'teams': ['Yankees', 'Red Sox'],
            'player': 'Aaron Judge'
        }
        
        with patch('bot.utils.mlb.mlb_fetcher.get_team_stats') as mock_team:
            with patch('bot.utils.mlb.mlb_fetcher.get_player_stats') as mock_player:
                with patch('bot.utils.mlb.mlb_fetcher.get_game_info') as mock_game:
                    mock_team.return_value = {'wins': 45, 'losses': 35, 'win_pct': 0.563}
                    mock_player.return_value = {'avg': '.285', 'hr': 25, 'rbi': 78}
                    mock_game.return_value = {
                        'away_pitcher': 'Gerrit Cole',
                        'home_pitcher': 'Chris Sale',
                        'weather': 'Clear, 72°F',
                        'venue': 'Fenway Park'
                    }
                    
                    result = await betting_commands._fetch_mlb_data(bet_data)
                    
                    assert result['away_team'] == 'Yankees'
                    assert result['home_team'] == 'Red Sox'
                    assert result['player_stats']['avg'] == '.285'
                    assert result['weather'] == 'Clear, 72°F'
    
    @pytest.mark.asyncio
    async def test_generate_pick_content_vip(self, betting_commands):
        """Test VIP pick content generation."""
        bet_data = {
            'teams': ['Yankees', 'Red Sox'],
            'player': 'Aaron Judge',
            'description': 'Over 1.5 hits',
            'odds': '-110',
            'units': '2'
        }
        
        mlb_data = {
            'away_team': 'Yankees',
            'home_team': 'Red Sox',
            'player_stats': {'avg': '.285', 'hr': 25, 'rbi': 78},
            'current_trends': 'Yankees is 0.563 this season',
            'weather': 'Clear, 72°F'
        }
        
        with patch.object(betting_commands, '_generate_analysis') as mock_analysis:
            mock_analysis.return_value = "Player Aaron Judge is hitting .285 this season..."
            
            content = await betting_commands._generate_pick_content(
                "vip", bet_data, mlb_data, "12/25/23", "7:05", "Strong analysis"
            )
            
            assert "VIP PLAY" in content
            assert "Yankees @ Red Sox" in content
            assert "Aaron Judge" in content
            assert "7:05 PM EST" in content
    
    @pytest.mark.asyncio
    async def test_generate_pick_content_free(self, betting_commands):
        """Test free pick content generation."""
        bet_data = {
            'teams': ['Yankees', 'Red Sox'],
            'player': 'Aaron Judge',
            'description': 'Over 1.5 hits',
            'odds': '-110'
        }
        
        mlb_data = {
            'away_team': 'Yankees',
            'home_team': 'Red Sox',
            'player_stats': {'avg': '.285', 'hr': 25, 'rbi': 78}
        }
        
        with patch.object(betting_commands, '_generate_analysis') as mock_analysis:
            mock_analysis.return_value = "Player Aaron Judge is hitting .285 this season..."
            
            content = await betting_commands._generate_pick_content(
                "free", bet_data, mlb_data, "12/25/23", "7:05", "Strong analysis"
            )
            
            assert "FREE PLAY" in content
            assert "LOCK IT" in content
            assert "7:05 PM EST" in content
    
    @pytest.mark.asyncio
    async def test_generate_pick_content_lotto(self, betting_commands):
        """Test lotto pick content generation."""
        bet_data = {
            'teams': ['Yankees', 'Red Sox'],
            'player': 'Aaron Judge',
            'description': 'Over 1.5 hits',
            'odds': '-110'
        }
        
        mlb_data = {
            'away_team': 'Yankees',
            'home_team': 'Red Sox'
        }
        
        content = await betting_commands._generate_pick_content(
            "lotto", bet_data, mlb_data, "12/25/23", "7:05", "Strong analysis"
        )
        
        assert "LOTTO TICKET" in content
        assert "Pick 1:" in content
        assert "Pick 2:" in content
        assert "Pick 3:" in content
        assert "Pick 4:" in content
        assert "GOOD LUCK TO ALL TAILING" in content
    
    @pytest.mark.asyncio
    async def test_generate_analysis_with_data(self, betting_commands):
        """Test analysis generation with complete data."""
        bet_data = {
            'player': 'Aaron Judge'
        }
        
        mlb_data = {
            'player_stats': {'avg': '.285', 'hr': 25, 'rbi': 78},
            'current_trends': 'Yankees is 0.563 this season',
            'weather': 'Clear, 72°F'
        }
        
        analysis = await betting_commands._generate_analysis(
            bet_data, mlb_data, "Strong matchup analysis"
        )
        
        assert "Aaron Judge" in analysis
        assert ".285" in analysis
        assert "25 HRs" in analysis
        assert "78 RBIs" in analysis
        assert "0.563" in analysis
        assert "Clear, 72°F" in analysis
        assert "Strong matchup analysis" in analysis
    
    @pytest.mark.asyncio
    async def test_generate_analysis_fallback(self, betting_commands):
        """Test analysis generation with missing data."""
        bet_data = {'player': 'TBD'}
        mlb_data = {'player_stats': {}, 'current_trends': '', 'weather': 'TBD'}
        
        analysis = await betting_commands._generate_analysis(
            bet_data, mlb_data, ""
        )
        
        assert "Based on current form and matchup analysis" in analysis
    
    def test_get_target_channel_id(self, betting_commands):
        """Test channel ID retrieval."""
        vip_id = betting_commands._get_target_channel_id("vip")
        free_id = betting_commands._get_target_channel_id("free")
        lotto_id = betting_commands._get_target_channel_id("lotto")
        
        assert vip_id == 123456789
        assert free_id == 987654321
        assert lotto_id == 555666777
    
    @pytest.mark.asyncio
    async def test_post_pick_success(self, betting_commands, mock_interaction, mock_image):
        """Test successful pick posting."""
        with patch.object(betting_commands, '_analyze_betting_slip') as mock_analyze:
            with patch.object(betting_commands, '_fetch_mlb_data') as mock_mlb:
                with patch.object(betting_commands, '_generate_pick_content') as mock_content:
                    mock_analyze.return_value = {
                        'teams': ['Yankees', 'Red Sox'],
                        'player': 'Aaron Judge',
                        'description': 'Over 1.5 hits',
                        'odds': '-110'
                    }
                    mock_mlb.return_value = {
                        'away_team': 'Yankees',
                        'home_team': 'Red Sox',
                        'player_stats': {'avg': '.285'}
                    }
                    mock_content.return_value = "🔒 | VIP PLAY #1 🏆 – 12/25/23"
                    
                    await betting_commands._post_pick(
                        mock_interaction, mock_image, "Test context", "vip"
                    )
                    
                    # Verify interaction was handled
                    mock_interaction.response.defer.assert_called_once()
                    mock_interaction.followup.send.assert_called()
    
    @pytest.mark.asyncio
    async def test_post_pick_invalid_image(self, betting_commands, mock_interaction):
        """Test pick posting with invalid image."""
        # Create invalid image
        invalid_image = Mock(spec=discord.Attachment)
        invalid_image.content_type = "text/plain"
        
        await betting_commands._post_pick(
            mock_interaction, invalid_image, "Test context", "vip"
        )
        
        # Should send error message
        mock_interaction.followup.send.assert_called_with(
            "❌ Please upload a valid image file!", ephemeral=True
        )

if __name__ == "__main__":
    pytest.main([__file__]) 