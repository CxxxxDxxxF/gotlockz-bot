# GotLockz Dashboard

A Flask web dashboard for tracking betting picks and performance analytics.

## Features

- 📊 Real-time pick tracking
- 📈 Performance analytics
- 🔄 Discord bot integration
- 📱 Responsive design
- 🎯 Pick management

## API Endpoints

- `GET /api/ping` - Health check
- `GET /api/bot-status` - Bot status
- `GET /api/picks` - Get all picks
- `POST /api/picks/add` - Add new pick
- `POST /api/sync-discord` - Sync from Discord
- `GET /api/stats` - Performance statistics

## Environment Variables

- `PORT` - Server port (default: 7860 for Hugging Face)

## Deployment

This dashboard is deployed on Hugging Face Spaces for free hosting and automatic HTTPS. 