#!/usr/bin/env python3
"""
setup_env.py

Environment setup script for GotLockz Bot.
Creates .env file with all required environment variables.
"""
import os
import sys
from pathlib import Path


def create_env_file():
    """Create .env file with environment variables."""

    env_content = """# GotLockz Bot Environment Configuration

# === DISCORD BOT SETUP ===
# Get these from Discord Developer Portal: https://discord.com/developers/applications
DISCORD_TOKEN=your_discord_bot_token_here
GUILD_ID=your_guild_id_here
OWNER_ID=your_user_id_here

# === CHANNEL IDs ===
# Get these by right-clicking channels and selecting "Copy ID" (Developer Mode must be enabled)
ANALYSIS_CHANNEL_ID=your_analysis_channel_id_here
VIP_CHANNEL_ID=your_vip_channel_id_here
LOTTO_CHANNEL_ID=your_lotto_channel_id_here
FREE_CHANNEL_ID=your_free_channel_id_here

# === AI ANALYSIS ===
# Get from OpenAI: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
ANALYSIS_TEMPERATURE=0.7

# === DASHBOARD INTEGRATION ===
# Set to your Hugging Face dashboard URL
DASHBOARD_URL=https://cjruizz99-gotlockz-dashboard.hf.space

# === FILE PATHS ===
COUNTER_FILE=counters.json
LOG_FILE=gotlockz-bot.log

# === GOOGLE SHEETS (Optional) ===
# For advanced pick tracking
GOOGLE_CREDENTIALS_PATH=gcreds.json
GOOGLE_SHEET_NAME=GotLockz Picks

# === DEPLOYMENT ===
# Set to true for production
PRODUCTION_MODE=false
"""

    env_file = Path('.env')

    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("❌ Setup cancelled.")
            return False

    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'discord.py',
        'openai',
        'Pillow',
        'requests',
        'python-dotenv'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall them with: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are installed!")
        return True


def create_directories():
    """Create necessary directories."""
    directories = ['logs', 'data', 'temp']

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

    print("✅ Directories created successfully!")


def main():
    """Main setup function."""
    print("🚀 GotLockz Bot Environment Setup")
    print("=" * 40)

    # Check dependencies
    print("\n1. Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)

    # Create directories
    print("\n2. Creating directories...")
    create_directories()

    # Create .env file
    print("\n3. Creating .env file...")
    if create_env_file():
        print("\n📋 Next Steps:")
        print("1. Edit .env file with your actual values")
        print("2. Set DISCORD_TOKEN from Discord Developer Portal")
        print("3. Set channel IDs (enable Developer Mode in Discord)")
        print("4. Set OPENAI_API_KEY for AI analysis")
        print("5. Set DASHBOARD_URL to your Hugging Face dashboard")
        print("\n6. Run the bot: python3 main.py")
        print("\n🔗 Useful Links:")
        print("- Discord Developer Portal: https://discord.com/developers/applications")
        print("- OpenAI API Keys: https://platform.openai.com/api-keys")
        print("- Your Dashboard: https://cjruizz99-gotlockz-dashboard.hf.space")
    else:
        print("❌ Setup failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
