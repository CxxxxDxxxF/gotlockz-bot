# 🚀 GotLockz Bot Deployment Guide

This guide covers the complete deployment pipeline for the GotLockz Bot, including CI/CD setup, monitoring, and maintenance.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [CI/CD Pipeline](#cicd-pipeline)
4. [Deployment Platforms](#deployment-platforms)
5. [Monitoring & Health Checks](#monitoring--health-checks)
6. [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### Required Accounts
- [GitHub](https://github.com) - Source code and CI/CD
- [Discord Developer Portal](https://discord.com/developers/applications) - Bot application
- [Render](https://render.com) - Bot hosting
- [Hugging Face](https://huggingface.co) - Dashboard hosting
- [OpenAI](https://openai.com) - AI analysis

### Required Tools
- Git
- Python 3.9+
- Docker (optional)

## 🌍 Environment Setup

### 1. Bot Environment Variables

Create a `.env` file or set these in your deployment platform:

```bash
# Discord Bot
DISCORD_TOKEN=your_discord_bot_token
GUILD_ID=your_guild_id

# Channel IDs (optional - can be set via commands)
VIP_CHANNEL_ID=channel_id_for_vip_picks
LOTTO_CHANNEL_ID=channel_id_for_lotto_picks
FREE_CHANNEL_ID=channel_id_for_free_picks
ANALYSIS_CHANNEL_ID=channel_id_for_analysis
LOG_CHANNEL_ID=channel_id_for_logging

# AI Analysis
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
ANALYSIS_TEMPERATURE=0.7

# Dashboard
DASHBOARD_URL=https://your-username-gotlockz-dashboard.hf.space

# Owner
OWNER_ID=your_discord_user_id
```

### 2. GitHub Secrets Setup

Go to your GitHub repository → Settings → Secrets and variables → Actions, and add:

```bash
# Bot Secrets
DISCORD_TOKEN=your_discord_bot_token
OPENAI_API_KEY=your_openai_api_key

# Deployment Secrets
RENDER_SERVICE_ID=your_render_service_id
RENDER_API_KEY=your_render_api_key
HF_USERNAME=your_huggingface_username
HF_TOKEN=your_huggingface_token

# Monitoring Secrets
DISCORD_WEBHOOK_URL=your_discord_webhook_url
BOT_HEALTH_URL=your_bot_health_endpoint
DASHBOARD_URL=your_dashboard_url
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflows

The project includes three automated workflows:

#### 1. **Deploy Workflow** (`.github/workflows/deploy.yml`)
- **Triggers**: Push to main/master branch
- **Actions**:
  - Run tests
  - Code linting
  - Deploy to Render
  - Deploy dashboard to Hugging Face

#### 2. **Development Workflow** (`.github/workflows/development.yml`)
- **Triggers**: Push to feature branches, pull requests
- **Actions**:
  - Code quality checks
  - Test coverage
  - Security scans
  - Dependency checks

#### 3. **Monitor Workflow** (`.github/workflows/monitor.yml`)
- **Triggers**: Every 6 hours, manual dispatch
- **Actions**:
  - Health checks
  - Dependency updates
  - Discord notifications

### Setting Up CI/CD

1. **Fork/Clone the Repository**
   ```bash
   git clone https://github.com/your-username/gotlockz-bot.git
   cd gotlockz-bot
   ```

2. **Set Up GitHub Secrets** (see above)

3. **Enable GitHub Actions**
   - Go to repository Settings → Actions → General
   - Enable "Allow all actions and reusable workflows"

4. **Push to Main Branch**
   ```bash
   git add .
   git commit -m "Initial setup with CI/CD"
   git push origin main
   ```

## 🚀 Deployment Platforms

### 1. Bot Deployment (Render)

#### Manual Setup
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `gotlockz-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: Free or Paid

#### Environment Variables
Add all required environment variables in Render dashboard.

#### Auto-Deploy
The CI/CD pipeline will automatically deploy to Render when you push to main.

### 2. Dashboard Deployment (Hugging Face)

#### Manual Setup
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Configure:
   - **Owner**: Your username
   - **Space name**: `gotlockz-dashboard`
   - **Space SDK**: `Gradio`
   - **License**: MIT

#### Auto-Deploy
The CI/CD pipeline will automatically update the dashboard.

## 📊 Monitoring & Health Checks

### 1. Bot Health Monitoring

The bot includes built-in health monitoring:

```python
# Check bot status
/status

# Debug information
/debug

# Bot statistics
/stats
```

### 2. Logging System

Set up logging channel:
```bash
/setup_logging #channel
```

The bot will log:
- Command usage
- Pick postings
- Errors and warnings
- Bot status changes

### 3. Automated Health Checks

The GitHub Actions monitor workflow runs every 6 hours and:
- Checks bot responsiveness
- Verifies dashboard status
- Monitors Discord API
- Sends notifications on failures

### 4. Dashboard Monitoring

The dashboard includes:
- Real-time bot status
- Pick tracking
- Analytics
- Error reporting

## 🔧 Troubleshooting

### Common Issues

#### 1. Bot Not Responding
```bash
# Check logs
/debug

# Verify token
echo $DISCORD_TOKEN

# Check permissions
# Ensure bot has required permissions in Discord
```

#### 2. Commands Not Showing
```bash
# Force sync commands
/force_sync

# Check command registration
/debug
```

#### 3. Analysis Not Working
```bash
# Check OpenAI API key
echo $OPENAI_API_KEY

# Verify analysis is enabled
/debug
```

#### 4. Dashboard Connection Issues
```bash
# Check dashboard URL
echo $DASHBOARD_URL

# Test connection
/status
```

### Log Analysis

#### Render Logs
1. Go to Render Dashboard
2. Select your service
3. Click "Logs" tab
4. Look for errors and warnings

#### Discord Logs
Check the configured logging channel for:
- Command errors
- Pick posting issues
- Bot status changes

### Performance Optimization

#### 1. Memory Usage
- Monitor memory usage in Render dashboard
- Consider upgrading plan if needed

#### 2. Response Times
- Use `/ping` to test latency
- Check `/debug` for performance metrics

#### 3. API Rate Limits
- Monitor OpenAI API usage
- Implement rate limiting if needed

## 🔄 Maintenance

### Regular Tasks

#### Weekly
- Review bot logs
- Check for dependency updates
- Monitor performance metrics

#### Monthly
- Update dependencies
- Review security settings
- Backup configuration

#### Quarterly
- Review and update documentation
- Performance optimization
- Feature planning

### Updates

#### Automatic Updates
The CI/CD pipeline handles:
- Code deployments
- Dependency updates
- Security patches

#### Manual Updates
For major changes:
1. Create feature branch
2. Test locally
3. Create pull request
4. Review and merge

## 📞 Support

### Getting Help
1. Check this documentation
2. Review GitHub Issues
3. Check Discord logs
4. Contact maintainers

### Contributing
1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

---

**Last Updated**: December 2024
**Version**: 2.0.0 