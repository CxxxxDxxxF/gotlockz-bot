# GotLockz Discord Bot - M4 Mac Edition

A modern Discord bot for MLB betting analysis, optimized for ARM64 architecture and M4 Mac development.

## 🏗️ Architecture Overview

This Discord bot is designed to work alongside the OCR processing module, consuming preprocessed JSON data and formatting it into beautiful Discord posts for the 21+ betting community.

### Directory Structure

```
discord/
├── commands/           # Discord slash commands
├── handlers/           # Event and interaction handlers
├── services/           # Business logic services
├── utils/              # Utility functions and helpers
├── config/             # Configuration and setup
├── formatters/         # Data formatting utilities
├── validators/         # Input validation
├── middleware/         # Request middleware
├── types/              # TypeScript type definitions
├── interfaces/         # Interface definitions
├── scripts/            # Deployment and utility scripts
└── logs/               # Application logs
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ (ARM64 compatible)
- Discord Bot Token
- Discord Application ID
- Discord Guild ID (for development)

### Installation

1. **Clone and navigate to the Discord directory:**
   ```bash
   cd discord
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your Discord credentials
   ```

4. **Deploy commands:**
   ```bash
   npm run deploy
   ```

5. **Start the bot:**
   ```bash
   npm start
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DISCORD_TOKEN` | Discord bot token | ✅ |
| `DISCORD_CLIENT_ID` | Discord application ID | ✅ |
| `DISCORD_GUILD_ID` | Discord server ID | ❌ (dev only) |
| `NODE_ENV` | Environment (development/production) | ❌ |
| `LOG_LEVEL` | Logging level (debug/info/warn/error) | ❌ |

### Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token to your `.env` file
5. Go to "OAuth2" → "URL Generator"
6. Select scopes: `bot`, `applications.commands`
7. Select bot permissions: `Send Messages`, `Use Slash Commands`, `Embed Links`
8. Use the generated URL to invite the bot to your server

## 📋 Available Commands

### Core Commands

- `/help` - Show available commands
- `/ping` - Check bot status and latency
- `/pick` - Get today's betting pick
- `/stats` - View team/player statistics
- `/odds` - Check current betting odds
- `/weather` - Get weather impact analysis

### Development Commands

- `/status` - Detailed bot status
- `/debug` - Debug information (admin only)

## 🔄 Data Flow

### OCR Integration

The bot is designed to consume JSON data from the OCR processing module:

```json
{
  "teams": {
    "away": "Yankees",
    "home": "Red Sox"
  },
  "pick": "Yankees ML -150",
  "odds": "-150",
  "confidence": "85%",
  "analysis": "Detailed betting analysis...",
  "venue": "Fenway Park",
  "gameTime": "2024-01-15T19:00:00Z",
  "broadcast": "ESPN"
}
```

### Post Generation

The bot automatically formats this data into rich Discord embeds with:
- Team logos and colors
- Formatted odds and confidence levels
- Interactive buttons
- Weather and venue information
- Professional betting analysis

## 🛠️ Development

### Adding New Commands

1. Create a new file in `commands/`
2. Export `data` (SlashCommandBuilder) and `execute` function
3. Deploy commands: `npm run deploy`

Example:
```javascript
import { SlashCommandBuilder } from 'discord.js';

export const data = new SlashCommandBuilder()
  .setName('example')
  .setDescription('Example command');

export async function execute(interaction) {
  await interaction.reply('Hello!');
}
```

### Adding New Services

1. Create a new file in `services/`
2. Export a class or singleton instance
3. Import and use in your commands

### Testing

```bash
# Run tests
npm test

# Run with nodemon for development
npm run dev

# Check bot health
npm run health
```

## 📊 Monitoring

### Health Checks

The bot includes comprehensive health monitoring:
- Memory usage tracking
- API latency monitoring
- Custom health checks
- Performance metrics

### Logging

Logs are stored in `logs/` directory:
- `error.log` - Error messages
- `combined.log` - All logs
- `discord.log` - Discord-specific events

## 🔒 Security

### Rate Limiting

Built-in rate limiting prevents abuse:
- 5 messages per minute per user
- 10 commands per minute per user
- 3 betting requests per 5 minutes per user

### Input Validation

All inputs are validated for:
- Spam patterns
- Forbidden words
- JSON structure (for OCR data)
- Message length limits

## 🚀 Deployment

### Local Development

```bash
npm run dev
```

### Production

```bash
npm start
```

### Docker (Optional)

```bash
docker build -t gotlockz-discord .
docker run -d --env-file .env gotlockz-discord
```

## 🤝 Collaboration

### Branch Strategy

- `feature/discord-m4` - Your development branch
- `main` - Production-ready code
- `develop` - Integration branch

### Code Style

- Use ES6 modules (import/export)
- Follow Discord.js v14 patterns
- Implement proper error handling
- Add comprehensive logging
- Use async/await over Promises

## 📝 Notes for M4 Mac Development

- All dependencies are ARM64 compatible
- No x86-specific packages included
- Optimized for Apple Silicon performance
- Cross-platform compatibility maintained

## 🆘 Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check Discord token in `.env`
   - Verify bot has proper permissions
   - Check bot is online in Discord

2. **Commands not working**
   - Run `npm run deploy` to register commands
   - Check command deployment status
   - Verify guild ID for development

3. **High memory usage**
   - Check for memory leaks in custom code
   - Monitor with `/ping` command
   - Restart bot if needed

### Getting Help

- Check logs in `logs/` directory
- Use `/ping` for bot status
- Review Discord.js documentation
- Check environment variables

## 📄 License

MIT License - See main project license

---

**GotLockz Family** - 21+ Only • Please bet responsibly 