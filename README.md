# GotLockz Bot - Discord Betting Analysis Bot

A sophisticated Discord bot for betting slip analysis using OCR, AI, and real-time data enrichment.

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone the repository
git clone <your-repo-url>
cd gotlockz-bot

# Set your Discord bot token
export DISCORD_TOKEN='your_bot_token_here'

# Run deployment script
./deploy.sh
```

### 2. Deploy to Hosting Platform
- **Render**: Upload code and set `DISCORD_TOKEN` environment variable
- **Railway**: Connect repo and set environment variables
- **Heroku**: Deploy and configure environment variables

### 3. Sync Commands with Discord
Once deployed, use these commands in Discord:

```
/force_sync  # Force sync all commands (may take up to 1 hour)
/ping        # Test bot responsiveness
/status      # Check bot status
```

## 🔧 Discord Command Sync Issue

### Problem
Your bot shows old slash commands (`/analyze_bet`, `/postpick`) instead of new features.

### Solution
1. **Deploy Updated Code**: Make sure your hosting platform has the latest code
2. **Use Force Sync**: Run `/force_sync` in Discord (admin only)
3. **Wait for Cache**: Discord can take up to 1 hour to update command cache globally
4. **Check Bot Permissions**: Ensure bot has "applications.commands" scope

### Available Commands
- `/ping` - Test bot responsiveness
- `/sync` - Sync picks to dashboard
- `/status` - Check bot and dashboard status
- `/addpick` - Add new pick to dashboard
- `/force_sync` - Force sync all commands

## 📋 Features

### Core Functionality
- **OCR Analysis**: Parse betting slips from images
- **AI Analysis**: GPT-powered betting analysis
- **Real-time Data**: Live sports statistics and odds
- **Dashboard Integration**: Web dashboard for analytics
- **Pick Tracking**: Track and analyze betting picks

### Commands
- `!ping` / `/ping` - Test bot responsiveness
- `!sync` / `/sync` - Sync picks to dashboard
- `!status` / `/status` - Check bot status
- `!addpick` / `/addpick` - Add new pick
- `!force_sync` / `/force_sync` - Force sync commands

## 🛠️ Development

### Local Development
```bash
# Install dependencies
pip3 install -r requirements.txt

# Set environment variables
export DISCORD_TOKEN='your_bot_token_here'
export DASHBOARD_URL='http://localhost:8080'

# Run bot
python3 main.py

# Run dashboard (in separate terminal)
python3 dashboard/app.py
```

### Environment Variables
- `DISCORD_TOKEN` - Your Discord bot token (required)
- `DASHBOARD_URL` - Dashboard URL for API calls (optional)

## 📁 Project Structure
```
gotlockz-bot/
├── bot.py              # Main bot logic
├── main.py             # Bot entry point
├── requirements.txt    # Python dependencies
├── deploy.sh          # Deployment script
├── dashboard/         # Web dashboard
│   ├── app.py
│   ├── static/
│   └── templates/
└── utils/             # Utility modules
    ├── gpt_analysis.py
    ├── mlb_stats.py
    └── ocr_parser.py
```

## 🔍 Troubleshooting

### Bot Not Responding
1. Check if bot is online in Discord
2. Verify `DISCORD_TOKEN` is set correctly
3. Check bot permissions in Discord Developer Portal
4. Review hosting platform logs

### Commands Not Syncing
1. Run `/force_sync` in Discord
2. Wait up to 1 hour for global cache update
3. Check bot has "applications.commands" scope
4. Verify code is deployed to hosting platform

### Dashboard Connection Issues
1. Check `DASHBOARD_URL` environment variable
2. Verify dashboard is running and accessible
3. Check network connectivity between bot and dashboard

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review hosting platform logs
3. Verify environment variables are set correctly
4. Test commands with `/ping` and `/status`

## 🎯 Next Steps

1. **Deploy Updated Code**: Upload the new bot.py to your hosting platform
2. **Set Environment Variables**: Ensure DISCORD_TOKEN is set
3. **Test Commands**: Use `/ping` to verify bot is responsive
4. **Force Sync**: Use `/force_sync` to update command cache
5. **Wait for Update**: Allow up to 1 hour for Discord to update globally
