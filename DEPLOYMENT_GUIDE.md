# 🚀 GotLockz Bot - Deployment Guide

## Overview
This guide will walk you through deploying the AI-accelerated MLB Discord bot to Render.

## Prerequisites
- GitHub repository with the bot code
- Discord Bot Token
- Render account (free tier available)

## Step 1: Discord Bot Setup

### 1.1 Create Discord Application
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Name it "GotLockz Bot" or your preferred name
4. Save the **Application ID** (you'll need this later)

### 1.2 Create Bot
1. Go to "Bot" section in your application
2. Click "Add Bot"
3. Under "Token", click "Reset Token" and copy the **Bot Token**
4. Enable these Privileged Gateway Intents:
   - Message Content Intent
   - Server Members Intent
   - Presence Intent

### 1.3 Invite Bot to Server
1. Go to "OAuth2" → "URL Generator"
2. Select scopes: `bot`, `applications.commands`
3. Select permissions:
   - Send Messages
   - Use Slash Commands
   - Attach Files
   - Read Message History
   - Add Reactions
4. Copy the generated URL and open it in a browser
5. Select your server and authorize the bot

## Step 2: Render Deployment

### 2.1 Connect Repository
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Select the repository: `gotlockz-bot`

### 2.2 Configure Service
- **Name**: `gotlockz-bot` (or your preferred name)
- **Environment**: `Node`
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Build Command**: Leave empty (uses Dockerfile)
- **Start Command**: Leave empty (uses Dockerfile)

### 2.3 Environment Variables
Add these environment variables in Render:

#### Required Variables:
```
DISCORD_TOKEN=your_discord_bot_token_here
CLIENT_ID=your_discord_application_id_here
OWNER_ID=your_discord_user_id_here
```

#### Optional Variables:
```
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
GUILD_ID=your_discord_server_id_here
NODE_ENV=production
LOG_LEVEL=info
```

### 2.4 Advanced Settings
- **Health Check Path**: `/health`
- **Auto-Deploy**: Enable
- **Plan**: Starter (free) or higher

## Step 3: Deploy

### 3.1 Initial Deployment
1. Click "Create Web Service"
2. Render will automatically:
   - Build the Docker image
   - Install dependencies
   - Deploy the bot
   - Register Discord commands

### 3.2 Monitor Deployment
1. Watch the build logs for any errors
2. Check the "Logs" tab for runtime information
3. Verify the bot appears online in Discord

## Step 4: Testing

### 4.1 Basic Commands
Test these commands in your Discord server:
- `/pick` - Main betting analysis command
- `/admin status` - Check bot status

### 4.2 Health Check
Visit your Render URL + `/health` to see bot status:
```
https://your-app-name.onrender.com/health
```

## Step 5: Troubleshooting

### Common Issues

#### Bot Not Responding
1. Check if bot is online in Discord
2. Verify environment variables are set correctly
3. Check Render logs for errors

#### Commands Not Working
1. Ensure bot has proper permissions
2. Check if commands were deployed successfully
3. Verify `CLIENT_ID` is correct

#### Build Failures
1. Check Docker build logs
2. Verify all files are committed to GitHub
3. Ensure `package-lock.json` exists

### Debug Commands
```bash
# Check bot status
npm run status

# Test setup
npm run setup

# Health check
npm run health
```

## Step 6: Monitoring

### Render Dashboard
- Monitor uptime and performance
- Check logs for errors
- View resource usage

### Discord Bot
- Monitor command usage
- Check for error messages
- Verify bot responsiveness

## Step 7: Updates

### Automatic Updates
- Render auto-deploys when you push to `main`
- Bot will restart automatically
- Commands are re-registered on each deploy

### Manual Updates
1. Make changes to your code
2. Commit and push to GitHub
3. Render will automatically redeploy

## Security Notes

### Environment Variables
- Never commit tokens to GitHub
- Use Render's environment variable system
- Rotate tokens regularly

### Bot Permissions
- Only grant necessary permissions
- Monitor bot activity
- Use guild-specific commands for testing

## Support

### Documentation
- [Discord.js Documentation](https://discord.js.org/)
- [Render Documentation](https://render.com/docs)
- [Project README](./README_AI.md)

### Community
- Check GitHub Issues for known problems
- Review troubleshooting guide
- Monitor bot logs for errors

## Success Checklist

- [ ] Bot appears online in Discord
- [ ] `/pick` command responds
- [ ] `/admin status` works
- [ ] Health endpoint returns 200
- [ ] No errors in Render logs
- [ ] Environment variables set correctly
- [ ] Bot has proper permissions

🎉 **Congratulations! Your AI-accelerated MLB Discord bot is now live!** 