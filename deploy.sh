#!/bin/bash

echo "🚀 GotLockz Bot Deployment Script"
echo "=================================="

# Check if DISCORD_TOKEN is set
if [ -z "$DISCORD_TOKEN" ]; then
    echo "❌ DISCORD_TOKEN environment variable not set!"
    echo "Please set your Discord bot token:"
    echo "export DISCORD_TOKEN='your_bot_token_here'"
    exit 1
fi

echo "✅ Discord token found"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Test bot
echo "🧪 Testing bot..."
python3 -c "import bot; print('✅ Bot module ready')"

echo ""
echo "🎯 Next Steps:"
echo "1. Deploy your bot to your hosting platform (Render, Railway, etc.)"
echo "2. Set DISCORD_TOKEN environment variable in your hosting platform"
echo "3. Once deployed, use /force_sync in Discord to sync new commands"
echo "4. Wait up to 1 hour for Discord to update command cache globally"
echo ""
echo "📋 Available Commands:"
echo "  /ping - Test bot responsiveness"
echo "  /sync - Sync picks to dashboard"
echo "  /status - Check bot status"
echo "  /addpick - Add new pick"
echo "  /force_sync - Force sync commands"
echo ""
echo "🔗 Dashboard URL: Set DASHBOARD_URL environment variable if using dashboard" 