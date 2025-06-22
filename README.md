# GotLockz Bot - Discord Betting Analysis Bot

A sophisticated Discord bot for betting slip analysis using OCR, AI, and real-time data enrichment with integrated dashboard analytics.

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone the repository
git clone <your-repo-url>
cd gotlockz-bot

# Run setup script
python3 setup_env.py

# Edit .env file with your credentials
nano .env

# Install dependencies
pip3 install -r requirements.txt

# Run the bot
python3 main.py
```

### 2. Environment Configuration
The setup script creates a `.env` file with all required variables:

```env
# Discord Bot Setup
DISCORD_TOKEN=your_discord_bot_token_here
GUILD_ID=your_guild_id_here
OWNER_ID=your_user_id_here

# Channel IDs
ANALYSIS_CHANNEL_ID=your_analysis_channel_id_here
VIP_CHANNEL_ID=your_vip_channel_id_here
LOTTO_CHANNEL_ID=your_lotto_channel_id_here
FREE_CHANNEL_ID=your_free_channel_id_here

# AI Analysis
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
ANALYSIS_TEMPERATURE=0.7

# Dashboard Integration
DASHBOARD_URL=https://cjruizz99-gotlockz-dashboard.hf.space
```

## 🎯 Available Commands

### Core Betting Commands
- **`/analyze`** - Analyze betting slip images with OCR and AI
- **`/vip`** - Post VIP picks with image analysis
- **`/lotto`** - Post lotto picks with image analysis  
- **`/free`** - Post free picks with image analysis

### Analytics Commands
- **`/history`** - View pick history by type
- **`/stats`** - View bot statistics and performance

### Utility Commands
- **`/ping`** - Test bot responsiveness
- **`/sync`** - Sync picks to dashboard
- **`/status`** - Check bot and dashboard status
- **`/addpick`** - Manually add picks to dashboard
- **`/force_sync`** - Force sync all Discord commands

## 📊 Dashboard Integration

Your bot automatically syncs with the web dashboard at:
**https://cjruizz99-gotlockz-dashboard.hf.space**

### Dashboard Features:
- 📈 Real-time statistics and analytics
- 📋 Pick history and tracking
- ➕ Manual pick entry
- 📝 Result updates
- 🔄 Discord sync interface

## 🔧 Features

### Core Functionality
- **OCR Analysis**: Parse betting slips from images using advanced OCR
- **AI Analysis**: GPT-powered betting analysis with confidence scoring
- **Real-time Data**: Live sports statistics and odds enrichment
- **Dashboard Integration**: Web dashboard for analytics and management
- **Pick Tracking**: Comprehensive pick tracking with results
- **Channel Management**: Automatic posting to designated channels

### Advanced Features
- **Image Processing**: Advanced OCR with bet detail extraction
- **AI Validation**: Quality validation for analysis results
- **Counter Management**: Automatic pick numbering by type
- **Error Handling**: Graceful error handling and logging
- **Type Safety**: Full type checking and validation

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

# Run dashboard (separate terminal)
python3 run_dashboard.py
```

### Project Structure
```
gotlockz-bot/
├── bot.py              # Main bot logic with all commands
├── main.py             # Bot entry point
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
├── setup_env.py        # Environment setup script
├── deploy.sh          # Deployment script
├── image_processing.py # OCR and image analysis
├── ai_analysis.py      # AI-powered analysis
├── data_enrichment.py  # Data enrichment utilities
├── utils/              # Utility modules
│   ├── gpt_analysis.py
│   ├── mlb_stats.py
│   └── ocr_parser.py
├── dashboard/          # Local dashboard
└── gotlockz-dashboard/ # Hugging Face dashboard
```

## 🚀 Deployment

### Render Deployment
```bash
# Deploy to Render
./deploy.sh

# Set environment variables in Render dashboard
DISCORD_TOKEN=your_token
DASHBOARD_URL=https://cjruizz99-gotlockz-dashboard.hf.space
```

### Docker Deployment
```bash
# Build and run with Docker
docker build -t gotlockz-bot .
docker run -e DISCORD_TOKEN=your_token gotlockz-bot
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

### Analysis Not Working
1. Check `OPENAI_API_KEY` is set correctly
2. Verify image quality and format
3. Check OCR dependencies are installed
4. Review error logs for specific issues

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
5. Check the dashboard for real-time status

## 🎯 Next Steps

1. **Complete Setup**: Run `python3 setup_env.py` and configure your `.env` file
2. **Test Commands**: Use `/ping` to verify bot is responsive
3. **Post Picks**: Try `/vip`, `/lotto`, or `/free` with betting slip images
4. **Check Dashboard**: Visit your Hugging Face dashboard to see analytics
5. **Monitor Performance**: Use `/stats` and `/history` to track performance

## 🔗 Useful Links

- **Discord Developer Portal**: https://discord.com/developers/applications
- **OpenAI API Keys**: https://platform.openai.com/api-keys
- **Your Dashboard**: https://cjruizz99-gotlockz-dashboard.hf.space
- **Hugging Face Spaces**: https://huggingface.co/spaces

---

**GotLockz Bot** - Professional betting analysis and tracking platform 🏆
