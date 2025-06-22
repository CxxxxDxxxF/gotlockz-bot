# 🏆 GotLockz Discord Bot

**Professional Discord bot for betting analysis and pick management with OCR integration and live MLB data.**

## 🚀 Features

### Core Betting Commands
- **`/betting vip`** - Post VIP picks with intelligent analysis
- **`/betting free`** - Post free picks with live stats
- **`/lotto-ticket-bets`** - Post lotto ticket picks with multiple selections

### Advanced Features
- **🔍 OCR Integration** - Automatically reads betting slip images
- **📊 Live MLB Data** - Fetches real-time player and team statistics
- **🤖 AI Analysis** - Generates contextual analysis based on live data
- **📱 Plain-Text Templates** - Clean, consistent formatting
- **🔄 Channel Routing** - Automatically posts to appropriate channels
- **📈 Pick Counters** - Tracks and displays pick statistics

### Bot Management
- **`/info ping`** - Test bot responsiveness
- **`/info status`** - Check bot and system status
- **`/info stats`** - View pick statistics and usage
- **`/info force_sync`** - Force sync slash commands (Admin only)

## 🏗️ Architecture

```
gotlockz-bot/
├── bot/                    # Main bot source code
│   ├── main.py            # Bot entry point
│   ├── config.py          # Configuration management
│   ├── commands/          # Command modules
│   │   ├── betting.py     # Betting commands
│   │   └── info.py        # Info/utility commands
│   ├── utils/             # Utility modules
│   │   ├── ocr.py         # OCR processing
│   │   ├── mlb.py         # MLB data integration
│   │   └── ...            # Other utilities
│   ├── services/          # External integrations
│   ├── templates/         # Text templates
│   └── data/              # Persistent data
├── tests/                 # Test suite
├── scripts/               # Deployment scripts
├── dashboard/             # Web dashboard
├── Dockerfile             # Production container
├── docker-compose.yml     # Container orchestration
└── requirements.txt       # Python dependencies
```

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- Discord Bot Token
- Tesseract OCR (for image processing)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd gotlockz-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your Discord token and channel IDs
   ```

4. **Run the bot**
   ```bash
   python bot/main.py
   ```

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Or build manually**
   ```bash
   docker build -t gotlockz-bot .
   docker run -d --env-file .env gotlockz-bot
   ```

## ⚙️ Configuration

### Required Environment Variables

```bash
# Discord Bot Token (Required)
DISCORD_TOKEN=your_discord_bot_token_here

# Channel IDs (Required)
VIP_CHANNEL_ID=1234567890123456789
FREE_CHANNEL_ID=1234567890123456789
LOTTO_CHANNEL_ID=1234567890123456789
```

### Optional Configuration

```bash
# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO

# Advanced Features
OPENAI_API_KEY=sk-your_openai_api_key_here
GUILD_ID=1234567890123456789
OWNER_ID=1234567890123456789
```

## 📋 Usage

### Posting Picks

1. **VIP Pick**
   ```
   /betting vip
   Image: [Upload betting slip]
   Context: [Optional analysis notes]
   ```

2. **Free Pick**
   ```
   /betting free
   Image: [Upload betting slip]
   Context: [Optional analysis notes]
   ```

3. **Lotto Ticket**
   ```
   /lotto-ticket-bets
   Image: [Upload betting slip]
   Context: [Optional analysis notes]
   ```

### Bot Management

- **Check Status**: `/info status`
- **View Statistics**: `/info stats`
- **Test Connection**: `/info ping`
- **Sync Commands**: `/info force_sync` (Admin only)

## 🧪 Testing

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test Suite
```bash
pytest tests/test_betting_commands.py
pytest tests/test_enhanced_commands.py
```

### Test Coverage
```bash
pytest --cov=bot tests/
```

## 🚀 Deployment

### Render (Recommended)
1. Connect your GitHub repository
2. Set environment variables in Render dashboard
3. Build command: `pip install -r requirements.txt`
4. Start command: `python bot/main.py`

### Docker
```bash
# Production
docker-compose -f docker-compose.yml up -d

# Development
docker-compose -f docker-compose.dev.yml up
```

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DISCORD_TOKEN=your_token
export VIP_CHANNEL_ID=your_channel_id

# Run bot
python bot/main.py
```

## 🔧 Development

### Project Structure
- **`bot/commands/`** - Command implementations
- **`bot/utils/`** - Utility functions and helpers
- **`bot/services/`** - External API integrations
- **`tests/`** - Unit and integration tests
- **`scripts/`** - Deployment and utility scripts

### Adding New Commands
1. Create command in `bot/commands/`
2. Add to bot setup in `bot/main.py`
3. Write tests in `tests/`
4. Update documentation

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings
- Write unit tests
- Use async/await for I/O operations

## 📊 Monitoring

### Logs
- Application logs: `bot/data/bot.log`
- Error logs: `bot/data/error_logs.txt`
- Pick counters: `bot/data/pick_counters.json`

### Health Checks
- Bot responsiveness: `/info ping`
- System status: `/info status`
- Docker health check included

## 🔒 Security

- Non-root Docker user
- Environment variable configuration
- Input validation and sanitization
- Error handling and logging
- Rate limiting (Discord enforced)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 Changelog

### v2.0.0 (Current)
- ✅ Professional code structure
- ✅ Enhanced OCR integration
- ✅ Live MLB data fetching
- ✅ Plain-text templates
- ✅ Docker deployment
- ✅ Comprehensive testing
- ✅ Production-ready error handling

### v1.0.0
- Basic Discord bot functionality
- Simple betting commands
- Embed-based responses

## 📞 Support

- **Issues**: Create a GitHub issue
- **Discord**: Join our support server
- **Email**: support@gotlockz.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ by the GotLockz Team**
