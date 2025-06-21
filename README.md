<<<<<<< HEAD
# GotLockz Discord Bot 🤖

A sophisticated Discord bot for automated betting slip analysis using OCR, AI, and real-time data enrichment.

## Features

### 🎯 Core Functionality
- **Advanced OCR**: Enhanced image processing for betting slip text extraction
- **AI Analysis**: GPT-4 powered betting analysis with edge calculations
- **Dynamic Data Enrichment**: Real-time game info, weather, H2H stats
- **Automated Pick Posting**: VIP, Lotto, and Free pick channels
- **Pick History**: Track and display betting performance

### 📊 Analysis Capabilities
- **Risk Assessment**: Low/Medium/High risk evaluation
- **Edge Calculation**: Implied vs true probability analysis
- **Confidence Scoring**: 1-10 confidence ratings with reasoning
- **Stake Recommendations**: Optimal bet sizing suggestions
- **Market Analysis**: Current betting market conditions

### 🔧 Technical Features
- **Structured Logging**: Comprehensive error tracking and monitoring
- **Health Monitoring**: Real-time bot status and performance metrics
- **Owner Notifications**: Critical error alerts via DM
- **Command Validation**: Robust error handling and user feedback
- **Caching System**: Optimized performance with intelligent caching

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/gotlockz-bot.git
cd gotlockz-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### 4. Configure Discord Bot
1. Create a Discord application at [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a bot and get your token
3. Invite the bot to your server with appropriate permissions
4. Get your server (guild) ID and channel IDs

### 5. Set Up OpenAI
1. Get an OpenAI API key from [OpenAI Platform](https://platform.openai.com/)
2. Add it to your `.env` file

### 6. Run the Bot
```bash
python main.py
```

## Environment Variables

Create a `.env` file with the following variables:

```env
# Bot Credentials
DISCORD_TOKEN=your_discord_bot_token
GUILD_ID=your_discord_server_id
OWNER_ID=your_discord_user_id

# Channel IDs
ANALYSIS_CHANNEL_ID=channel_id_for_analysis
VIP_CHANNEL_ID=channel_id_for_vip_picks
LOTTO_CHANNEL_ID=channel_id_for_lotto_picks
FREE_CHANNEL_ID=channel_id_for_free_picks

# API Keys
OPENAI_API_KEY=your_openai_api_key

# Configuration
OPENAI_MODEL=gpt-4
ANALYSIS_TEMPERATURE=0.7
```

## Commands

### `/analyze`
Analyze a betting slip image with AI-powered insights.
- **Usage**: Upload an image and optionally add context
- **Channel**: Analysis channel only
- **Output**: Detailed analysis with recommendations

### `/vip`, `/lotto`, `/free`
Post picks to respective channels with automatic numbering.
- **Usage**: Upload betting slip image
- **Permissions**: Manage Messages required
- **Output**: Formatted pick summary posted to target channel

### `/history`
View pick history and performance statistics.
- **Usage**: Specify pick type and limit
- **Output**: Historical data and performance metrics

### `/stats`
View bot statistics and health status.
- **Usage**: No parameters required
- **Output**: Bot performance and system health

## Project Structure

```
gotlockz-bot/
├── main.py                 # Main entry point
├── bot.py                  # Discord bot core
├── commands.py             # Slash command definitions
├── config.py               # Configuration management
├── image_processing.py     # OCR and image processing
├── ai_analysis.py          # AI-powered analysis
├── data_enrichment.py      # Real-time data enrichment
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── .gitignore             # Git ignore rules
├── tests/                 # Test suite
│   ├── test_image_processing.py
│   ├── test_ai_analysis.py
│   └── test_data_enrichment.py
└── README.md              # This file
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black .
isort .
```

### Type Checking
```bash
mypy .
```

## Deployment

### Local Development
```bash
python main.py
```

### Production (Docker)
```bash
docker build -t gotlockz-bot .
docker run --env-file .env gotlockz-bot
```

### Render.com
1. Connect your GitHub repository
2. Set environment variables in Render dashboard
3. Deploy automatically on push to main branch

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Join our Discord server
- Check the documentation

---

**Disclaimer**: This bot is for educational and entertainment purposes. Always gamble responsibly and within your means.
=======
# Gotlockz MLB Discord Bot

A Discord bot for the Gotlockz server that automates posting MLB betting picks with OCR, real-time stats, and AI-generated analysis.

## Features
- `/postpick` slash command to post MLB bet slips
- OCR extraction of bet details from images
- Integration with mlbstatsapi for live MLB data
- OpenAI GPT analysis for hype-driven write-ups
- Auto-incrementing play numbers (VIP vs Free)
- Docker-ready for Render deployment

## Setup

1. **Clone the repo**  
   ```bash
   git clone <repo-url>
   cd gotlockz_bot
   ```

2. **Configure secrets**  
   Copy `.env.example` to `.env` and fill in your keys:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   OPENAI_API_KEY=your_openai_api_key
   ```

3. **Build Docker image**  
   ```bash
   docker build -t gotlockz-bot .
   ```

4. **Run locally**  
   ```bash
   docker run --env-file .env gotlockz-bot
   ```

5. **Deploy on Render**  
   - Connect GitHub repository to Render as a Background Worker.
   - Ensure the Dockerfile is selected and environment variables are set.

## Folder Structure
```
gotlockz_bot/
├── bot.py
├── Dockerfile
├── requirements.txt
├── .env.example
├── README.md
└── utils/
    ├── ocr_parser.py
    ├── mlb_stats.py
    └── gpt_analysis.py
```
>>>>>>> cceffda894c274128b92ea45ab52674f56d45a11
