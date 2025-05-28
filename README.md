# Gotlockz MLB Discord Bot

A Discord bot for the Gotlockz server that automates posting MLB betting picks with OCR, real-time stats, and AI-generated analysis.

## Features
- `/postpick` slash command to post MLB bet slips
- OCR extraction of bet details from images
- Integration with mlbstatsapi for live MLB data
- OpenAI GPT analysis for hype-driven write-ups
- Auto-incrementing play numbers (VIP vs Free)
- Docker-ready for Render deployment

## Setup

1. **Clone the repo**  
   ```bash
   git clone <repo-url>
   cd gotlockz_bot
   ```

2. **Configure secrets**  
   Copy `.env.example` to `.env` and fill in your keys:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   OPENAI_API_KEY=your_openai_api_key
   ```

3. **Build Docker image**  
   ```bash
   docker build -t gotlockz-bot .
   ```

4. **Run locally**  
   ```bash
   docker run --env-file .env gotlockz-bot
   ```

5. **Deploy on Render**  
   - Connect GitHub repository to Render as a Background Worker.
   - Ensure the Dockerfile is selected and environment variables are set.

## Folder Structure
```
gotlockz_bot/
├── bot.py
├── Dockerfile
├── requirements.txt
├── .env.example
├── README.md
└── utils/
    ├── ocr_parser.py
    ├── mlb_stats.py
    └── gpt_analysis.py
```
