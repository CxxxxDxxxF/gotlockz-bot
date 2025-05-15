# gotlockz-bot Version 3

## Overview
A Discord bot to fetch MLB data and auto-post betting picks via OCR.

## Files and Functions

### gotlockz_bot.py
- **TOKEN**: Discord token from `DISCORD_TOKEN` env var.
- **CHANNEL_MAP**: Maps command keys to channel names.
- **intents**: Discord gateway intents.
- **bot**: `commands.Bot` instance.
- **on_ready()**: Initialize Google Sheets.
- **fetch_player()**: Fetch player info via MLB-StatsAPI and PyBaseball.
- **fetch_schedule()**: Fetch team schedule from MLB-StatsAPI.
- **postpick()**: Download attached slip image, OCR text, parse pick, log to Sheets, post to target channel, and acknowledge.

### utils/ocr.py
- **extract_text(image_path)**: Load image, convert to grayscale, run Tesseract OCR, return text.

### utils/sheets.py
- **init_sheets()**: Authenticate with Google Sheets API.
- **get_play_number()**: Return next play number by counting rows.
- **log_pick(pick)**: Append pick string to sheet.

### main.py
- Entry point: imports `bot` and `TOKEN` and runs the bot.

### Aptfile
- Installs system package `tesseract-ocr`.

### requirements.txt
- Python dependencies for the bot.
