#!/usr/bin/env python3
"""
Test suite for GotLockz bot commands.
Tests all command functionality, permissions, error handling, and async operations.
"""

import os
os.environ['DISCORD_TOKEN'] = 'test'
os.environ['GUILD_ID'] = '1'
os.environ['ANALYSIS_CHANNEL_ID'] = '1'
os.environ['VIP_CHANNEL_ID'] = '1'
os.environ['LOTTO_CHANNEL_ID'] = '1'
os.environ['FREE_CHANNEL_ID'] = '1'
os.environ['OWNER_ID'] = '1'
os.environ['OPENAI_API_KEY'] = 'test'

# Now import the rest
import sys
import json
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from commands import (
    GotLockzCommands, 
    BettingCommands, 
    PermissionsManager, 
    BotLogger,
    require_vip,
    require_admin,
    validate_input
)


class TestPermissionsManager:
    """Test the PermissionsManager class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.bot = Mock()
        self.permissions = PermissionsManager(self.bot)
        
        # Mock environment variables
        with patch.dict(os.environ, {
            'VIP_ROLE_IDS': '123,456,789',
            'ADMIN_ROLE_IDS': '111,222,333',
            'BLOCKED_USER_IDS': '999,888'
        }):
            self.permissions = PermissionsManager(self.bot)
    
    def test_load_vip_roles(self):
        """Test loading VIP roles from environment."""
        assert self.permissions.vip_roles == [123, 456, 789]
    
    def test_load_admin_roles(self):
        """Test loading admin roles from environment."""
        assert self.permissions.admin_roles == [111, 222, 333]
    
    def test_load_blocked_users(self):
        """Test loading blocked users from environment."""
        assert self.permissions.blocked_users == [999, 888]
    
    def test_has_vip_role(self):
        """Test VIP role checking."""
        member = Mock()
        member.id = 12345
        member.roles = [Mock(id=123), Mock(id=456)]
        
        assert self.permissions.has_vip_role(member) is True
        
        member.roles = [Mock(id=999), Mock(id=888)]
        assert self.permissions.has_vip_role(member) is False
    
    def test_has_admin_role(self):
        """Test admin role checking."""
        member = Mock()
        member.id = 12345
        member.roles = [Mock(id=111), Mock(id=222)]
        
        assert self.permissions.has_admin_role(member) is True
        
        member.roles = [Mock(id=999), Mock(id=888)]
        assert self.permissions.has_admin_role(member) is False
    
    def test_is_blocked(self):
        """Test blocked user checking."""
        assert self.permissions.is_blocked(999) is True
        assert self.permissions.is_blocked(123) is False
    
    def test_cooldown_management(self):
        """Test cooldown functionality."""
        user_id = 12345
        command = "test_command"
        
        # Should allow first use
        assert self.permissions.check_cooldown(user_id, command, 30) is True
        
        # Set cooldown
        self.permissions.set_cooldown(user_id, command)
        
        # Should block immediate reuse
        assert self.permissions.check_cooldown(user_id, command, 30) is False


class TestBotLogger:
    """Test the BotLogger class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.bot = Mock()
        self.bot.log_channel_id = 123456
        self.logger = BotLogger(self.bot)
    
    @pytest.mark.asyncio
    async def test_log_event(self):
        """Test logging events to Discord."""
        with patch.object(self.logger, 'log_event') as mock_log:
            await self.logger.log_event('INFO', 'Test', 'Test message')
            mock_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_log_command(self):
        """Test logging command usage."""
        interaction = Mock()
        interaction.user.id = 12345
        interaction.user.name = "TestUser"
        interaction.guild.id = 67890
        interaction.guild.name = "TestGuild"
        interaction.channel_id = 11111
        interaction.channel.name = "test-channel"
        
        with patch.object(self.logger, 'log_command') as mock_log:
            await self.logger.log_command(interaction, "test_command", success=True)
            mock_log.assert_called_once()


class TestGotLockzCommands:
    """Test the GotLockzCommands class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.bot = Mock()
        self.bot.start_time = datetime.now()
        self.bot.latency = 0.1
        self.bot.guilds = [Mock(), Mock()]
        self.bot.users = [Mock(), Mock(), Mock()]
        self.bot.dashboard_enabled = True
        self.bot.dashboard_url = "http://test.com"
        self.bot.log_channel_id = 123456
        self.bot.channels_configured = True
        self.bot.ANALYSIS_ENABLED = True
        
        self.commands = GotLockzCommands(self.bot)
    
    @pytest.mark.asyncio
    async def test_ping_command(self):
        """Test the ping command."""
        interaction = Mock()
        interaction.response = AsyncMock()
        
        await self.commands.ping.callback(self.commands, interaction)
        
        interaction.response.send_message.assert_called_once_with("🏓 Pong! Bot is online!")
    
    @pytest.mark.asyncio
    async def test_status_command(self):
        """Test the status command."""
        interaction = Mock()
        interaction.response = AsyncMock()
        interaction.followup = AsyncMock()
        
        with patch('psutil.cpu_percent', return_value=50.0), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_memory.return_value.percent = 75.0
            mock_memory.return_value.used = 4 * 1024**3
            mock_memory.return_value.total = 8 * 1024**3
            mock_disk.return_value.percent = 60.0
            
            await self.commands.status_command.callback(self.commands, interaction)
            
            interaction.response.defer.assert_called_once()
            interaction.followup.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_help_command(self):
        """Test the help command."""
        interaction = Mock()
        interaction.response = AsyncMock()
        interaction.followup = AsyncMock()
        
        await self.commands.help_command.callback(self.commands, interaction)
        
        interaction.response.defer.assert_called_once()
        interaction.followup.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_about_command(self):
        """Test the about command."""
        interaction = Mock()
        interaction.response = AsyncMock()
        interaction.followup = AsyncMock()
        
        await self.commands.about_command.callback(self.commands, interaction)
        
        interaction.response.defer.assert_called_once()
        interaction.followup.send.assert_called_once()


class TestBettingCommands:
    """Test the BettingCommands class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.bot = Mock()
        self.bot.vip_channel_id = 111111
        self.bot.lotto_channel_id = 222222
        self.bot.free_channel_id = 333333
        self.bot.analysis_channel_id = 444444
        self.bot.channels_configured = False
        self.bot.ANALYSIS_ENABLED = True
        self.bot.dashboard_enabled = True
        self.bot.dashboard_url = "http://test.com"
        
        self.commands = BettingCommands(self.bot)
    
    @pytest.mark.asyncio
    async def test_load_counters_async(self):
        """Test async counter loading."""
        with patch('aiofiles.open') as mock_open:
            mock_file = AsyncMock()
            mock_file.read.return_value = '{"vip": 5, "lotto": 3, "free": 10}'
            mock_open.return_value.__aenter__.return_value = mock_file
            
            await self.commands._load_counters_async()
            
            assert self.commands.pick_counters == {"vip": 5, "lotto": 3, "free": 10}
    
    @pytest.mark.asyncio
    async def test_save_counters_async(self):
        """Test async counter saving."""
        self.commands.pick_counters = {"vip": 5, "lotto": 3, "free": 10}
        
        with patch('aiofiles.open') as mock_open:
            mock_file = AsyncMock()
            mock_open.return_value.__aenter__.return_value = mock_file
            
            await self.commands._save_counters()
            
            mock_file.write.assert_called_once()
            written_data = json.loads(mock_file.write.call_args[0][0])
            assert written_data == {"vip": 5, "lotto": 3, "free": 10}
    
    @pytest.mark.asyncio
    async def test_analyze_command_success(self):
        """Test successful analyze command."""
        interaction = Mock()
        interaction.channel_id = 444444
        interaction.response = AsyncMock()
        interaction.followup = AsyncMock()
        interaction.user = Mock()
        
        image = Mock()
        image.content_type = "image/png"
        image.read = AsyncMock(return_value=b"fake_image_data")
        
        with patch('commands.extract_text_from_image', return_value="test text"), \
             patch('commands.parse_bet_details', return_value={"team": "Test"}), \
             patch('commands.analyze_bet_slip', return_value={"recommendation": {"action": "bet", "reasoning": "test reason"}}), \
             patch('commands.validate_analysis_quality', return_value={"is_valid": True}):
            
            await self.commands._load_counters_async()
            await self.commands.analyze_command.callback(self.commands, interaction, image, "test context")
            
            interaction.response.defer.assert_called_once()
            interaction.followup.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_command_invalid_image(self):
        """Test analyze command with invalid image."""
        interaction = Mock()
        interaction.channel_id = 444444
        interaction.response = AsyncMock()
        interaction.followup = AsyncMock()
        
        image = Mock()
        image.content_type = "text/plain"  # Invalid type
        
        await self.commands._load_counters_async()
        await self.commands.analyze_command.callback(self.commands, interaction, image, "test context")
        
        interaction.followup.send.assert_called_once()
        assert "valid image file" in interaction.followup.send.call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_vip_command(self):
        """Test VIP command."""
        interaction = Mock()
        interaction.channel_id = 111111
        interaction.response = AsyncMock()
        interaction.followup = AsyncMock()
        interaction.user = Mock()
        interaction.user.id = 12345
        interaction.user.display_name = "TestUser"
        interaction.user.display_avatar.url = "http://test.com/avatar.png"
        interaction.guild = Mock()
        interaction.guild.get_member.return_value = Mock()
        
        image = Mock()
        image.content_type = "image/png"
        image.read = AsyncMock(return_value=b"fake_image_data")
        image.url = "http://test.com/image.png"
        
        # Patch permissions to allow VIP access
        with patch.object(self.bot.permissions, 'is_blocked', return_value=False), \
             patch.object(self.bot.permissions, 'has_vip_role', return_value=True), \
             patch.object(self.bot.permissions, 'check_cooldown', return_value=True), \
             patch.object(self.commands, '_post_pick') as mock_post:
            
            await self.commands._load_counters_async()
            await self.commands.vip_command.callback(self.commands, interaction, image, "test context")
            
            mock_post.assert_called_once_with(interaction, image, "test context", "vip", 111111)
    
    @pytest.mark.asyncio
    async def test_history_command(self):
        """Test history command."""
        interaction = Mock()
        interaction.response = AsyncMock()
        interaction.followup = AsyncMock()
        interaction.channel_id = 123456
        interaction.user = Mock()
        interaction.guild = Mock()
        interaction.guild.id = 654321
        interaction.guild.name = "TestGuild"
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"picks": []}
            mock_get.return_value = mock_response
            
            await self.commands._load_counters_async()
            await self.commands.history_command.callback(self.commands, interaction, "vip", 10)
            
            interaction.response.defer.assert_called_once()
            interaction.followup.send.assert_called_once()


class TestDecorators:
    """Test the permission and validation decorators."""
    
    def setup_method(self):
        """Set up test environment."""
        self.bot = Mock()
        self.bot.permissions = PermissionsManager(self.bot)
        self.bot.logger = BotLogger(self.bot)
        
        # Mock environment variables
        with patch.dict(os.environ, {
            'VIP_ROLE_IDS': '123,456',
            'ADMIN_ROLE_IDS': '111,222',
            'BLOCKED_USER_IDS': '999'
        }):
            self.bot.permissions = PermissionsManager(self.bot)
    
    @pytest.mark.asyncio
    async def test_require_vip_success(self):
        """Test VIP decorator with valid VIP user."""
        interaction = Mock()
        interaction.user.id = 12345
        interaction.guild = Mock()
        interaction.guild.get_member.return_value = Mock()
        interaction.response = AsyncMock()
        
        # Mock VIP role check
        with patch.object(self.bot.permissions, 'has_vip_role', return_value=True), \
             patch.object(self.bot.permissions, 'is_blocked', return_value=False), \
             patch.object(self.bot.permissions, 'check_cooldown', return_value=True):
            
            @require_vip()
            async def test_command(self, interaction):
                return "success"
            
            result = await test_command(self, interaction)
            assert result == "success"
    
    @pytest.mark.asyncio
    async def test_require_vip_blocked_user(self):
        """Test VIP decorator with blocked user."""
        interaction = Mock()
        interaction.user.id = 999  # Blocked user
        interaction.response = AsyncMock()
        
        with patch.object(self.bot.permissions, 'is_blocked', return_value=True):
            @require_vip()
            async def test_command(self, interaction):
                return "success"
            
            await test_command(self, interaction)
            
            interaction.response.send_message.assert_called_once()
            assert "blocked" in interaction.response.send_message.call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_require_admin_success(self):
        """Test admin decorator with valid admin user."""
        interaction = Mock()
        interaction.user.id = 12345
        interaction.guild = Mock()
        interaction.guild.get_member.return_value = Mock()
        interaction.response = AsyncMock()
        
        with patch.object(self.bot.permissions, 'has_admin_role', return_value=True), \
             patch.object(self.bot.permissions, 'is_blocked', return_value=False):
            
            @require_admin()
            async def test_command(self, interaction):
                return "success"
            
            result = await test_command(self, interaction)
            assert result == "success"
    
    @pytest.mark.asyncio
    async def test_validate_input_success(self):
        """Test input validation decorator with valid input."""
        interaction = Mock()
        interaction.user = Mock()
        interaction.response = AsyncMock()
        
        @validate_input
        async def test_command(self, interaction):
            return "success"
        
        result = await test_command(self, interaction)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_validate_input_invalid_interaction(self):
        """Test input validation decorator with invalid interaction."""
        interaction = None

        @validate_input
        async def test_command(self, interaction):
            return "success"

        # Should handle None interaction gracefully
        with pytest.raises(AttributeError):
            await test_command(self, interaction)

        # Now test with interaction missing user
        interaction2 = Mock()
        interaction2.user = None
        interaction2.response = AsyncMock()
        
        await test_command(self, interaction2)
        
        # Should send error message
        interaction2.response.send_message.assert_called_once()
        assert "Invalid input" in interaction2.response.send_message.call_args[0][0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 