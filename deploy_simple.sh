#!/bin/bash

# Simple Deployment Script for GotLockz Bot
# Focuses on reliability and minimal setup

set -e  # Exit on any error

echo "🚀 Starting simplified GotLockz Bot deployment..."

# Check if we're in the right directory
if [ ! -f "bot/main.py" ]; then
    echo "❌ Error: bot/main.py not found. Please run this script from the project root."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found. Please create one with your Discord token."
    echo "Example .env file:"
    echo "DISCORD_TOKEN=your_discord_token_here"
    echo "VIP_CHANNEL_ID=123456789"
    echo "FREE_CHANNEL_ID=987654321"
    echo "LOTTO_CHANNEL_ID=555666777"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install simplified requirements
echo "📥 Installing dependencies..."
pip install -r requirements_simple.txt

# Check if Tesseract is installed
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Warning: Tesseract OCR is not installed."
    echo "   OCR functionality will not work without it."
    echo "   Install with: brew install tesseract (macOS) or apt-get install tesseract-ocr (Ubuntu)"
fi

# Create data directory if it doesn't exist
mkdir -p bot/data

# Test the bot
echo "🧪 Testing bot components..."
python test_simple_bot.py

echo "✅ Deployment completed successfully!"
echo ""
echo "🎯 To start the bot:"
echo "   source venv/bin/activate"
echo "   python bot/main.py"
echo ""
echo "🔧 To run in background:"
echo "   nohup python bot/main.py > bot.log 2>&1 &"
echo ""
echo "📊 To check logs:"
echo "   tail -f bot.log" 