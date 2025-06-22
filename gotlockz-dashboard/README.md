---
title: GotLockz Dashboard
emoji: 🏆
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: false
---

# 🏆 GotLockz Dashboard

A professional betting picks tracking and analytics dashboard for the GotLockz Discord bot.

## Features

- 📊 **Real-time Analytics** - Track pick performance and win rates
- 📋 **Pick Management** - Add, view, and manage betting picks
- 🔄 **Discord Integration** - Sync picks from your Discord bot
- 📈 **Performance Tracking** - Monitor ROI and success rates
- 🎯 **Multiple Pick Types** - VIP, Free, and Lotto picks

## How to Use

1. **Dashboard Overview** - View statistics and quick actions
2. **View Picks** - See all your recent betting picks
3. **Add Pick** - Manually add new picks to the database
4. **Sync Discord** - Import picks from your Discord bot

## API Endpoints

Your dashboard provides these API endpoints for bot integration:

- `GET /api/ping` - Health check
- `GET /api/picks` - Get all picks
- `POST /api/sync-discord` - Sync picks from Discord
- `GET /api/bot-status` - Bot status

## Discord Bot Integration

Set your bot's `DASHBOARD_URL` environment variable to:
```
https://cjruizz99-gotlockz-dashboard.hf.space
```

## Technologies

- **Gradio** - Web interface framework
- **SQLite** - Local database storage
- **Python** - Backend logic

---

*Built for the GotLockz betting community* 🎯 