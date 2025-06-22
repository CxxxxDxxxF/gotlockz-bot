#!/bin/bash

echo "🚀 GotLockz Bot Deployment Script"
echo "=================================="

# Check if DISCORD_TOKEN is set
if [ -z "$DISCORD_TOKEN" ]; then
    echo "❌ DISCORD_TOKEN environment variable not set!"
    echo "Please set your Discord bot token:"
    echo "export DISCORD_TOKEN='your_bot_token_here'"
    echo ""
    echo "For production deployment, also set:"
    echo "export DASHBOARD_URL='https://your-dashboard-url.com'"
    exit 1
fi

echo "✅ Discord token found"

# Check dashboard URL
if [ -z "$DASHBOARD_URL" ]; then
    echo "⚠️ DASHBOARD_URL not set - bot will run in local mode"
    echo "To enable dashboard features, set:"
    echo "export DASHBOARD_URL='https://your-dashboard-url.com'"
else
    echo "✅ Dashboard URL: $DASHBOARD_URL"
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Test bot
echo "🧪 Testing bot..."
python3 -c "import bot; print('✅ Bot module ready')"

echo ""
echo "🎯 Next Steps:"
echo "1. Deploy your bot to your hosting platform (Render, Railway, etc.)"
echo "2. Set environment variables in your hosting platform:"
echo "   - DISCORD_TOKEN=your_bot_token_here"
echo "   - DASHBOARD_URL=https://your-dashboard-url.com (optional)"
echo "3. Once deployed, use /force_sync in Discord to sync new commands"
echo "4. Wait up to 1 hour for Discord to update command cache globally"
echo ""
echo "📋 Available Commands:"
echo "  /ping - Test bot responsiveness"
echo "  /sync - Sync picks to dashboard (if enabled)"
echo "  /status - Check bot status"
echo "  /addpick - Add new pick (if dashboard enabled)"
echo "  /force_sync - Force sync commands"
echo ""
echo "🔧 Troubleshooting:"
echo "  - If commands fail, check DASHBOARD_URL is set correctly"
echo "  - Bot will run in local mode if DASHBOARD_URL is not set"
echo "  - Use /ping to test basic connectivity" 