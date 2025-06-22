#!/usr/bin/env python3
"""
test_syntax.py

Test script to verify commands.py syntax is correct.
"""
import sys
import os
from datetime import datetime

def test_imports():
    """Test if all imports work correctly."""
    print("🔍 Testing imports...")
    
    try:
        import discord
        print("✅ discord imported successfully")
    except ImportError as e:
        print(f"❌ discord import failed: {e}")
        return False
    
    try:
        from discord import app_commands
        print("✅ app_commands imported successfully")
    except ImportError as e:
        print(f"❌ app_commands import failed: {e}")
        return False
    
    try:
        from discord.ext import commands
        print("✅ commands imported successfully")
    except ImportError as e:
        print(f"❌ commands import failed: {e}")
        return False
    
    return True

def test_commands_syntax():
    """Test if commands.py can be imported without syntax errors."""
    print("\n🔍 Testing commands.py syntax...")
    
    try:
        import commands
        print("✅ commands.py imported successfully")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in commands.py: {e}")
        return False
    except ImportError as e:
        print(f"❌ Import error in commands.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing commands.py: {e}")
        return False

def test_command_classes():
    """Test if command classes can be instantiated."""
    print("\n🔍 Testing command classes...")
    
    try:
        import commands
        
        # Test BettingCommands
        class MockBot:
            def __init__(self):
                self.guilds = []
                self.users = []
                self.latency = 0.1
                self.pick_counters = {"vip": 0, "lotto": 0, "free": 0}
                self.dashboard_enabled = False
                self.channels_configured = False
                self.start_time = datetime.now()
            
            def get_uptime(self):
                return "1h 30m"
        
        mock_bot = MockBot()
        betting_commands = commands.BettingCommands(mock_bot)
        print("✅ BettingCommands instantiated successfully")
        
        # Test InfoCommands
        info_commands = commands.InfoCommands(mock_bot)
        print("✅ InfoCommands instantiated successfully")
        
        return True
    except Exception as e:
        print(f"❌ Error testing command classes: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Starting syntax tests...\n")
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed!")
        return False
    
    # Test commands.py syntax
    if not test_commands_syntax():
        print("\n❌ Commands syntax test failed!")
        return False
    
    # Test command classes
    if not test_command_classes():
        print("\n❌ Command classes test failed!")
        return False
    
    print("\n✅ All tests passed! Commands should work correctly.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 