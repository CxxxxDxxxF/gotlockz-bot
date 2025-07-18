# 🚀 GotLockz Bot Deployment Guide

## Prerequisites

- Discord Bot Token
- Discord Application Client ID
- Discord Guild ID (for development)
- OpenAI API Key
- HuggingFace API Key (optional)
- Render account

## Environment Variables Setup

### Required Environment Variables

You **MUST** set these environment variables in your Render dashboard:

1. **DISCORD_TOKEN** - Your Discord bot token
2. **CLIENT_ID** - Your Discord application client ID
3. **GUILD_ID** - Your Discord server ID (for development)

### Optional Environment Variables

- **OPENAI_API_KEY** - For AI analysis features
- **HUGGINGFACE_API_KEY** - For additional AI models
- **MLB_API_KEY** - For MLB data (optional)
- **OPENWEATHER_API_KEY** - For weather data (optional)
- **REDIS_URL** - For caching (optional)
- **LOG_LEVEL** - Logging level (default: info)
- **RATE_LIMIT_COOLDOWN** - Rate limiting (default: 12000ms)
- **NODE_ENV** - Environment (default: production)
- **DEBUG** - Debug mode (default: false)

## Render Deployment Steps

### 1. Connect Your Repository

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the `ai-accelerated` directory

### 2. Configure Build Settings

- **Name**: `gotlockz-bot` (or your preferred name)
- **Environment**: `Node`
- **Build Command**: `npm ci`
- **Start Command**: `npm start`
- **Root Directory**: `ai-accelerated`

### 3. Set Environment Variables

In the Render dashboard, go to your service → Environment → Add Environment Variable:

```
DISCORD_TOKEN=your_discord_bot_token_here
CLIENT_ID=your_discord_client_id_here
GUILD_ID=your_discord_guild_id_here
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

### 4. Deploy

Click "Create Web Service" and wait for the deployment to complete.

## Discord Bot Setup

### 1. Create Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Give it a name (e.g., "GotLockz Bot")
4. Go to "Bot" section and create a bot
5. Copy the bot token and client ID

### 2. Invite Bot to Server

1. Go to "OAuth2" → "URL Generator"
2. Select scopes: `bot`, `applications.commands`
3. Select permissions: `Send Messages`, `Use Slash Commands`, `Attach Files`
4. Copy the generated URL and open it in a browser
5. Select your server and authorize

### 3. Get Guild ID

1. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
2. Right-click your server name
3. Click "Copy Server ID"

## Troubleshooting

### Common Issues

1. **"Cannot find module './env'"**
   - This is a TypeScript import error. The project uses JavaScript, not TypeScript.
   - Ensure all files are `.js` not `.ts`

2. **"CLIENT_ID is undefined"**
   - Make sure you've set the `CLIENT_ID` environment variable in Render
   - Check that the value is correct (no extra spaces)

3. **"Invalid Form Body" error**
   - Verify all required environment variables are set
   - Check that your Discord bot token is valid
   - Ensure the bot has proper permissions

4. **Commands not appearing**
   - Check the deployment logs for command registration errors
   - Verify the bot is in your server with proper permissions
   - Wait a few minutes for global commands to propagate

### Health Check

The bot includes a health check endpoint at `/health` that returns:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "uptime": 123.456,
  "version": "1.0.0"
}
```

### Logs

Check the Render logs for detailed error information:

1. Go to your service in Render dashboard
2. Click "Logs" tab
3. Look for error messages and stack traces

## Development

### Local Development

1. Copy `env.example` to `.env`
2. Fill in your environment variables
3. Run `npm install`
4. Run `npm run dev`

### Testing

```bash
npm test          # Run tests
npm run lint      # Run linting
npm run status    # Check deployment status
```

## Support

If you encounter issues:

1. Check the logs in Render dashboard
2. Verify all environment variables are set correctly
3. Ensure your Discord bot has proper permissions
4. Check that all dependencies are installed correctly

## Security Notes

- Never commit your `.env` file to version control
- Keep your Discord bot token secure
- Use environment variables for all sensitive data
- Regularly rotate your API keys 