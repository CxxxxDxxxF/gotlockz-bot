# GotLockz Bot V2 - MLB Betting Bot

A Discord bot designed to help your team post daily MLB betting picks with automated analysis and statistics.

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
