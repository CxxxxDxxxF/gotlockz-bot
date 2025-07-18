# Support Guide

## 🆘 Getting Help

We're here to help! Here are the best ways to get support for GotLockz Bot.

## 📚 Documentation

### Quick Start
- [README.md](../README.md) - Project overview and quick start
- [AI-Accelerated README](../ai-accelerated/README_AI.md) - Detailed bot documentation
- [Deployment Guide](../ai-accelerated/DEPLOYMENT_GUIDE.md) - Render deployment instructions
- [Troubleshooting Guide](../ai-accelerated/TROUBLESHOOTING.md) - Common issues and solutions

### Configuration
- [Environment Variables](../ai-accelerated/env.example) - All available configuration options
- [Commands Reference](../ai-accelerated/src/config/commands.json) - Available Discord commands
- [Features Configuration](../ai-accelerated/src/config/features.json) - Bot feature settings

## 🐛 Common Issues

### Bot Not Starting
1. Check your `DISCORD_TOKEN` is correct
2. Verify your `CLIENT_ID` matches your bot
3. Ensure all required environment variables are set
4. Check the logs for specific error messages

### Commands Not Working
1. Run `npm run deploy` to register commands
2. Check bot permissions in Discord
3. Verify the bot is online
4. Test with `/admin ping`

### OCR/AI Issues
1. Check API keys are set correctly
2. Verify image quality (clear, readable text)
3. Check API rate limits
4. Enable debug mode for detailed analysis

### Deployment Problems
1. Check Render logs for build errors
2. Verify environment variables in Render dashboard
3. Ensure Docker build completes successfully
4. Test health endpoint: `https://your-app.onrender.com/health`

## 💬 Community Support

### Discord Server
Join our Discord server for real-time support:
- **Server**: [GotLockz Community](https://discord.gg/gotlockz)
- **Channel**: `#bot-support`
- **Response Time**: Usually within 1-2 hours

### GitHub Issues
For bugs and feature requests:
1. Search [existing issues](../../issues) first
2. Use the appropriate template:
   - [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md)
   - [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md)
3. Provide detailed information and logs

### GitHub Discussions
For general questions and community help:
- [Q&A](../../discussions/categories/q-a)
- [Show and Tell](../../discussions/categories/show-and-tell)
- [Ideas](../../discussions/categories/ideas)

## 🔧 Development Support

### Local Development
```bash
# Clone the repository
git clone https://github.com/CxxxxDxxxF/gotlockz-bot.git
cd gotlockz-bot/ai-accelerated

# Install dependencies
npm install

# Set up environment
cp env.example .env
# Edit .env with your credentials

# Test setup
npm run setup

# Start development
npm run dev
```

### Testing
```bash
# Run all tests
npm test

# Check deployment status
npm run status

# Test health endpoint
npm run health
```

### Debugging
1. Enable debug mode in commands
2. Check logs in `logs/` directory
3. Use `/admin status` for system info
4. Monitor Render logs for deployment issues

## 📞 Direct Support

### Email Support
For urgent issues or private matters:
- **Email**: [support@gotlockz.com](mailto:support@gotlockz.com)
- **Response Time**: Within 24 hours
- **Subject**: Include `[SUPPORT]` in subject line

### Security Issues
For security vulnerabilities:
- **Email**: [security@gotlockz.com](mailto:security@gotlockz.com)
- **Subject**: `[SECURITY] Vulnerability Report`
- **DO NOT** create public issues for security problems

## 🎯 Before Asking for Help

1. **Search** existing issues and discussions
2. **Check** the troubleshooting guide
3. **Test** with the latest version
4. **Provide** detailed information:
   - Error messages and logs
   - Steps to reproduce
   - Environment details
   - What you've already tried

## 📋 Information to Include

When asking for help, please include:

### For Bot Issues
- Bot version and Discord.js version
- Error messages from logs
- Steps to reproduce the issue
- Screenshots if relevant

### For Deployment Issues
- Render service URL
- Build logs from Render
- Environment variables (without sensitive values)
- Docker build output

### For Feature Requests
- Detailed description of the feature
- Use cases and examples
- Priority level
- Any mockups or screenshots

## 🤝 Contributing

Want to help improve GotLockz Bot?

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.

## 📈 Status

- **Bot Status**: [Check here](https://status.gotlockz.com)
- **API Status**: [Discord API](https://status.discord.com)
- **Render Status**: [Render Status](https://status.render.com)

---

**Thank you for using GotLockz Bot! 🚀** 