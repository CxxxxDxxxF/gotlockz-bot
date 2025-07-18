#!/bin/bash

echo "🚀 Starting AI-Accelerated GotLockz Bot Deployment..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Make sure you're in the ai-accelerated directory."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm ci --omit=dev || {
    echo "❌ npm ci failed, trying npm install..."
    npm install --omit=dev
}

# Create logs directory if it doesn't exist
echo "📁 Creating logs directory..."
mkdir -p logs

# Deploy Discord commands
echo "🤖 Deploying Discord commands..."
npm run deploy

# Start the bot
echo "🚀 Starting bot..."
npm start 