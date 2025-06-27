# GotLockz Bot V2 - MLB Betting Bot

A high-performance MLB Discord bot with advanced analytics, real-time updates, and **built-in system protection** to prevent overheating and performance issues.

## 🛡️ System Protection Features

This bot includes comprehensive system monitoring and performance limiting to keep your computer safe:

### 🔍 Real-time Monitoring
- **CPU Usage**: Monitors CPU usage and throttles when it exceeds 80%
- **Memory Usage**: Tracks memory consumption and limits operations at 85%
- **Temperature**: Monitors system temperature (requires iStats on macOS)
- **Disk Usage**: Prevents disk space issues by limiting at 90%

### ⚡ Performance Limiting
- **Rate Limiting**: Maximum 5 concurrent requests with 200ms intervals
- **Adaptive Throttling**: Automatically reduces load when system is stressed
- **Emergency Mode**: Extreme throttling when resources are critically low
- **Smart Caching**: Reduces API calls with intelligent caching

### 🎛️ Performance Profiles
Set `PERFORMANCE_PROFILE` environment variable:
- `conservative`: 3 concurrent requests, 500ms intervals (safest)
- `balanced`: 5 concurrent requests, 200ms intervals (default)
- `performance`: 10 concurrent requests, 100ms intervals (fastest)

## 🚀 Quick Start

### 1. Health Check
Run the health check to verify system protection:
```bash
python health_check.py
```

### 2. Environment Setup
```bash
cp env.example .env
# Edit .env with your Discord bot token and API keys
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Bot
```bash
python main.py
```

## 🔧 Configuration

### System Protection Settings
```bash
# Conservative settings for extra safety
PERFORMANCE_PROFILE=conservative
MAX_CPU_PERCENT=70.0
MAX_MEMORY_PERCENT=80.0
MAX_TEMPERATURE_CELSIUS=80.0

# Monitoring frequency (seconds)
MONITORING_INTERVAL=60
```

### Performance Limits
```bash
# Request limiting
MAX_CONCURRENT_REQUESTS=5
MIN_REQUEST_INTERVAL=0.2
MAX_REQUESTS_PER_MINUTE=60

# Cache timeouts
CACHE_TIMEOUT_STATS=300
CACHE_TIMEOUT_WEATHER=300
CACHE_TIMEOUT_LIVE=60
```

## 📊 Features

### MLB Analytics
- **Real-time Game Updates**: Live scores, game states, and player stats
- **Advanced Player Analytics**: Head-to-head stats, recent performance, matchup analysis
- **Weather Impact Analysis**: Temperature, wind, humidity effects on games
- **Smart Caching**: 300x faster than previous scrapers (0.23s vs 70s)

### Discord Commands
- `!pick <team1> <team2>`: Get comprehensive game analysis
- `!admin status`: Check bot and system status
- Automatic throttling when system resources are low

## 🛠️ Development

### Testing
```bash
# Run system monitoring tests
python test_system_monitoring.py

# Run health check
python health_check.py

# Run scraper tests
python detailed_test_scraper.py
```

### Logging
The bot includes comprehensive logging with performance warnings:
- System resource monitoring
- Request rate limiting
- Cache hit/miss tracking
- Error handling and recovery

## 🔒 Safety Features

### Automatic Protection
- **CPU Overload**: Automatically throttles when CPU > 80%
- **Memory Pressure**: Reduces concurrent operations when memory > 85%
- **Temperature Control**: Emergency throttling when temperature > 85°C
- **Network Flooding**: Rate limits all external API calls

### Manual Override
```bash
# Force conservative mode
PERFORMANCE_PROFILE=conservative

# Disable adaptive throttling
ENABLE_ADAPTIVE_THROTTLING=false

# Emergency mode (extreme throttling)
ENABLE_EMERGENCY_MODE=true
```

## 📈 Performance

### Before (Old Scrapers)
- Weather scraper: 3.5+ seconds, often failed
- Stats service: 0.3s timeout, connection issues
- Statcast service: 66+ seconds (way too slow)
- **Total**: 70+ seconds, unreliable

### After (New System)
- MLB scraper: 0.23 seconds total
- Concurrent requests with caching
- Smart error handling and retries
- **Total**: 300x faster, reliable, and safe

## 🚨 Monitoring

The bot automatically logs system health:
```
INFO - System monitoring started
INFO - CPU usage: 45.2%
INFO - Memory usage: 62.1%
WARNING - System thresholds warning: CPU: 82.1%
CRITICAL - CRITICAL system thresholds exceeded: CPU: 96.5%
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run health checks: `python health_check.py`
4. Test system protection: `python test_system_monitoring.py`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you experience any issues:
1. Run `python health_check.py` to verify system protection
2. Check logs for performance warnings
3. Consider using `PERFORMANCE_PROFILE=conservative`
4. Monitor system resources in Activity Monitor/Task Manager

**Your computer's safety is our priority!** 🛡️

## Features

- **OCR Bet Slip Processing**: Automatically extracts betting data from uploaded images
- **MLB Statistics**: Fetches live team statistics from MLB API
- **AI Analysis**: Generates professional betting analysis using ChatGPT
- **Multiple Channel Support**: Posts to different channels (Free Play, VIP, Lotto Tickets)
- **Template System**: Consistent formatting for each pick type

## Commands

### `/pick post`
Post a betting pick with image analysis and AI.

**Parameters:**
- `channel_type`: Type of pick (Free Play, VIP Pick, Lotto Ticket)
- `image`: Betting slip image attachment
- `description`: Additional notes (optional)

### `/admin ping`
Test bot responsiveness.

### `/admin status`
Check bot status and system information.

### `/admin sync`
Sync slash commands (admin only).

### `/admin uptime`
Get bot uptime.

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Create a `.env` file with:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   OPENAI_API_KEY=your_openai_api_key
   VIP_CHANNEL_ID=your_vip_channel_id
   FREE_CHANNEL_ID=your_free_channel_id
   LOTTO_CHANNEL_ID=your_lotto_channel_id
   ```

3. **Run the Bot**
   ```bash
   python main.py
   ```

## Docker Deployment

```bash
docker build -t gotlockz-bot .
docker run -d --env-file .env gotlockz-bot
```

## Configuration

The bot uses three main channels:
- **Free Play**: General betting picks
- **VIP Pick**: Premium betting picks with unit sizing
- **Lotto Ticket**: High-risk, high-reward picks

Each channel has its own template format and the bot automatically posts to the correct channel based on your selection.

## Requirements

- Python 3.11+
- Discord Bot Token
- OpenAI API Key
- Tesseract OCR (for image processing)

## Support

For issues or questions, check the bot logs or contact your development team.
