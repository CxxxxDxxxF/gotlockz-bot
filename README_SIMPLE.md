# GotLockz Bot - Simplified Version

A **bulletproof, reliable** Discord bot for posting betting picks with OCR integration. This simplified version focuses on **maximum reliability** over complex features.

## 🎯 Key Features

- **OCR Image Processing**: Extract text from betting slip images
- **Simple Bet Parsing**: Parse team names, players, odds, and bet types
- **Channel-Specific Templates**: Different formats for VIP, Free, and Lotto channels
- **Reliable Timeout Handling**: Aggressive timeout protection to prevent Discord timeouts
- **Minimal Dependencies**: Only essential packages for maximum stability

## 🚀 Quick Start

### Prerequisites

1. **Python 3.11+**
2. **Tesseract OCR** (for image processing)
3. **Discord Bot Token**

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo>
   cd gotlockz-bot
   ```

2. **Run the simple deployment script:**
   ```bash
   ./deploy_simple.sh
   ```

3. **Create a `.env` file:**
   ```env
   DISCORD_TOKEN=your_discord_token_here
   VIP_CHANNEL_ID=123456789
   FREE_CHANNEL_ID=987654321
   LOTTO_CHANNEL_ID=555666777
   ```

4. **Start the bot:**
   ```bash
   source venv/bin/activate
   python bot/main.py
   ```

## 📋 Commands

### `/betting postpick`

Post a betting pick with OCR processing.

**Parameters:**
- `channel`: Discord channel to post in
- `image`: Betting slip image
- `unitsize`: Number of units (optional)

**Example:**
```
/betting postpick channel:#vip-picks image:[betting_slip.jpg] unitsize:2
```

## 🔧 How It Works

### 1. Image Processing
- Downloads the uploaded image with 5-second timeout
- Uses Tesseract OCR to extract text with 10-second timeout
- Simple image preprocessing for better results

### 2. Bet Parsing
- Extracts team names using regex patterns
- Identifies player names and bet types
- Parses odds and bet descriptions

### 3. Message Generation
- Creates channel-specific templates
- Includes current date/time
- Adds analysis section
- Updates pick counters

### 4. Posting
- Posts to specified channel with 3-second timeout
- Confirms success to user
- Handles all errors gracefully

## 🛠️ Troubleshooting

### Common Issues

1. **"Tesseract not available"**
   - Install Tesseract: `brew install tesseract` (macOS) or `apt-get install tesseract-ocr` (Ubuntu)

2. **"Image processing timed out"**
   - Use a clearer, higher-resolution image
   - Check image format (JPG, PNG supported)

3. **"Failed to post message"**
   - Check bot permissions in the target channel
   - Verify channel ID is correct

4. **"Command timed out"**
   - The bot has aggressive timeout protection
   - Try again with a simpler image or check network connection

### Logs

Check logs for detailed error information:
```bash
tail -f bot.log
```

## 🐳 Docker Deployment

For production deployment:

```bash
# Build the image
docker build -f Dockerfile.simple -t gotlockz-bot .

# Run the container
docker run --env-file .env gotlockz-bot
```

## 📊 Performance

- **Image Download**: 5-second timeout
- **OCR Processing**: 10-second timeout  
- **Message Generation**: 3-second timeout
- **Message Posting**: 3-second timeout
- **Total Command Time**: ~21 seconds maximum

## 🔒 Reliability Features

- **Immediate Discord Acknowledgment**: Prevents interaction timeouts
- **Step-by-Step Error Handling**: Each step has specific error messages
- **Graceful Degradation**: Continues with partial data if parsing fails
- **Comprehensive Logging**: Detailed logs for debugging
- **Timeout Protection**: Prevents hanging on slow operations

## 📁 File Structure

```
gotlockz-bot/
├── bot/
│   ├── main.py              # Main bot entry point
│   ├── config.py            # Configuration management
│   ├── commands/
│   │   ├── betting.py       # Simplified betting commands
│   │   └── info.py          # Info commands
│   └── utils/
│       └── ocr.py           # Simplified OCR processing
├── requirements_simple.txt  # Minimal dependencies
├── deploy_simple.sh         # Simple deployment script
├── Dockerfile.simple        # Simplified Docker setup
└── test_simple_bot.py       # Component testing
```

## 🎯 Success Metrics

This simplified version prioritizes:
- ✅ **Reliability**: 99%+ uptime
- ✅ **Speed**: Sub-25-second command completion
- ✅ **Simplicity**: Easy to debug and maintain
- ✅ **Stability**: No complex external API dependencies

## 🔄 Migration from Complex Version

If you're migrating from the complex version:

1. **Backup your data:**
   ```bash
   cp bot/data/pick_counters.json bot/data/pick_counters_backup.json
   ```

2. **Use the simplified deployment:**
   ```bash
   ./deploy_simple.sh
   ```

3. **Test with a simple image first**

4. **Monitor logs for any issues**

## 📞 Support

For issues or questions:
1. Check the logs: `tail -f bot.log`
2. Run the test script: `python test_simple_bot.py`
3. Verify your `.env` configuration
4. Check Tesseract installation

---

**This simplified version is designed to be bulletproof and reliable. It sacrifices some advanced features for maximum stability and uptime.** 