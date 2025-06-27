# GotLockz Bot

A high-performance MLB Discord bot with advanced analytics, real-time updates, and AI-powered betting analysis.

## 🚀 Quick Start

### Environment Variables

The bot requires the following environment variables:

- `DISCORD_BOT_TOKEN` - Your Discord bot token
- `DISCORD_CLIENT_ID` - Your Discord application client ID  
- `DISCORD_GUILD_ID` - Your Discord server ID (optional, for guild-specific commands)
- `OPENAI_API_KEY` - Your OpenAI API key for GPT analysis

### Installation

1. Clone the repository
2. Install dependencies: `npm install`
3. Set up environment variables
4. Run the bot: `npm start`

## 🎯 Features

- **Image Analysis**: OCR-powered betting slip analysis using Tesseract.js
- **GPT Integration**: AI-powered betting analysis and insights using OpenAI
- **Weather Context**: Weather data integration for enhanced analysis
- **Rate Limiting**: Built-in protection against spam (12-second cooldown)
- **Health Monitoring**: HTTP health endpoint for uptime checks
- **Caching**: Intelligent caching to reduce API costs

## 📋 Commands

### `/pick`
Post a betting pick with image analysis and AI.

**Parameters:**
- `channel_type`: Type of pick (Free Play, VIP Pick, Lotto Ticket)
- `image`: Betting slip image attachment
- `description`: Additional notes (optional)

### `/admin`
Admin commands for bot management.

**Subcommands:**
- `purge <amount>`: Delete a number of messages
- `stats`: Show bot uptime and version

## 🛠️ Development

### Scripts
- Build: `npm run build`
- Test: `npm test`
- Type check: `npm run type-check`
- Start: `npm start`
- Dev: `npm run dev`

### Testing
All tests pass with comprehensive coverage:
- Environment variable validation
- Command registration
- Service integration
- Analysis service with OpenAI mocking

## 🏗️ Architecture

### Services
- **OCR Service**: Image text extraction
- **MLB Service**: Game statistics and data
- **Weather Service**: Weather forecasts and conditions
- **Betting Service**: Edge calculations and analysis
- **Analysis Service**: GPT-powered betting insights

### Rate Limiting & Caching
- Per-user rate limiting (12-second cooldown)
- 1-minute cache for analysis results
- Intelligent API cost management

## 🚀 Deployment

### Render Deployment
The bot is configured for automatic deployment on Render:

1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. Deploy automatically on pushes to `main`

### Health Endpoint
The bot exposes a health endpoint at `/health`:
```bash
curl https://your-service-url/health
# Returns: { "status": "ok", "uptime": 123.45 }
```

## 📊 Monitoring

### Startup Logs
Look for these messages in Render logs:
```
Bot is ready and analysis service is up!
Health endpoint listening on port 3000
```

### Environment Verification
Ensure these environment variables are set in Render:
- `DISCORD_BOT_TOKEN`
- `DISCORD_CLIENT_ID` 
- `DISCORD_GUILD_ID`
- `OPENAI_API_KEY`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests: `npm test`
4. Submit a pull request

## 📄 License

MIT License
