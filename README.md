# GotLockz Bot

## Overview

GotLockz is a Discord bot that logs sports bet picks into a Google Sheet via the Sheets API. It supports OCR extraction from images and assigns sequential play numbers for VIP vs Free plays.

## Project Structure

```
.
├── .gitignore
├── .env.example
├── Dockerfile
├── README.md
├── config.py
├── main.py
├── gotlockz_bot.py
├── requirements.txt
├── utils
│   ├── ocr.py
│   └── sheets.py
└── .github
    └── workflows
        └── ci.yml
```

## Setup

1. **Clone** or download this project.
2. **Copy** `.env.example` to `.env` and fill in:
   ```
   DISCORD_TOKEN=your_bot_token
   SHEET_ID=your_google_sheet_id
   # Either:
   GOOGLE_SHEETS_CREDS="<raw JSON>"
   # Or:
   GOOGLE_SHEETS_CREDS_B64="<base64 JSON>"
   ```
3. **Install** dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. **Install Tesseract** (for OCR):
   ```bash
   sudo apt-get install tesseract-ocr
   ```
5. **Share** your Google Sheet with the service account email.
6. **Run** locally:
   ```bash
   python main.py
   ```

## Docker

Build and run the Docker image:

```bash
docker build -t gotlockz-bot .
docker run -e DISCORD_TOKEN=... -e SHEET_ID=... -e GOOGLE_SHEETS_CREDS_B64=... gotlockz-bot
```

## CI

A GitHub Actions workflow (`.github/workflows/ci.yml`) is included to lint code:

```yaml
name: CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt flake8
      - name: Lint code
        run: flake8 .
```
