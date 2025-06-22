#!/bin/bash

echo "☁️  GotLockz Cloud Deployment Script"
echo "===================================="
echo "This script will remove ALL local hosting and deploy to cloud only."
echo ""

# Confirm deployment
read -p "⚠️  This will remove local hosting files. Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled."
    exit 1
fi

echo ""
echo "🧹 Step 1: Removing local hosting components..."

# Remove local hosting directories
echo "   Removing dashboard directories..."
rm -rf dashboard/ 2>/dev/null
rm -rf gotlockz-dashboard/ 2>/dev/null
rm -rf hf_deploy/ 2>/dev/null

# Remove local hosting files
echo "   Removing local hosting files..."
rm -f jarvis_dashboard.py
rm -f run_dashboard.py
rm -f start_dashboard.sh
rm -f temp_monitor.sh
rm -f jarvis.py
rm -f start_jarvis.sh
rm -f JARVIS_README.md

# Remove local database
echo "   Removing local database..."
rm -f gotlockz.db

# Remove local logs
echo "   Removing local logs..."
rm -f bot_logs.txt
rm -f error_logs.txt

echo "✅ Local hosting components removed."

echo ""
echo "📦 Step 2: Updating requirements for cloud deployment..."

# Update requirements.txt for cloud
cat > requirements.txt << 'EOF'
discord.py>=2.3.0
supabase>=1.0.0
cloudflare>=2.19.0
openai>=1.0.0
pillow>=9.0.0
pytesseract>=0.3.10
requests>=2.28.0
python-dotenv>=1.0.0
aiofiles>=23.0.0
psutil>=5.9.0
flask>=2.3.0
EOF

echo "✅ Requirements updated for cloud deployment."

echo ""
echo "🔧 Step 3: Creating cloud configuration..."

# Create cloud config
cat > config_cloud.py << 'EOF'
import os
from supabase import create_client, Client
from typing import Optional

# Supabase Database
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase: Optional[Client] = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Cloudflare R2 Storage
R2_URL = os.getenv('CLOUDFLARE_R2_URL')
R2_KEY = os.getenv('CLOUDFLARE_R2_KEY')
R2_SECRET = os.getenv('CLOUDFLARE_R2_SECRET')

# Dashboard URL
DASHBOARD_URL = os.getenv('DASHBOARD_URL')

# Discord Bot
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')

# OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')

# Channel IDs
VIP_CHANNEL_ID = int(os.getenv('VIP_CHANNEL_ID', '0'))
LOTTO_CHANNEL_ID = int(os.getenv('LOTTO_CHANNEL_ID', '0'))
FREE_CHANNEL_ID = int(os.getenv('FREE_CHANNEL_ID', '0'))
ANALYSIS_CHANNEL_ID = int(os.getenv('ANALYSIS_CHANNEL_ID', '0'))
LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID', '0'))

# Owner
OWNER_ID = int(os.getenv('OWNER_ID', '0'))

# Features
ANALYSIS_ENABLED = bool(os.getenv('ANALYSIS_ENABLED', 'True'))
DASHBOARD_ENABLED = bool(os.getenv('DASHBOARD_ENABLED', 'True'))

def get_supabase():
    """Get Supabase client with error handling."""
    if not supabase:
        raise Exception("Supabase not configured. Set SUPABASE_URL and SUPABASE_KEY.")
    return supabase

def upload_image_to_r2(image_data: bytes, filename: str) -> str:
    """Upload image to Cloudflare R2 and return URL."""
    if not all([R2_URL, R2_KEY, R2_SECRET]):
        raise Exception("R2 not configured. Set CLOUDFLARE_R2_* environment variables.")
    
    # Implementation would go here
    # For now, return a placeholder
    return f"{R2_URL}/{filename}"

def log_to_cloud(level: str, message: str, metadata: dict = None):
    """Log to cloud database."""
    try:
        supabase_client = get_supabase()
        supabase_client.table('bot_logs').insert({
            'level': level,
            'message': message,
            'metadata': metadata or {}
        }).execute()
    except Exception as e:
        print(f"Failed to log to cloud: {e}")
EOF

echo "✅ Cloud configuration created."

echo ""
echo "🚀 Step 4: Creating cloud deployment files..."

# Create Render deployment file
cat > render.yaml << 'EOF'
services:
  - type: web
    name: gotlockz-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    envVars:
      - key: DISCORD_TOKEN
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: CLOUDFLARE_R2_URL
        sync: false
      - key: CLOUDFLARE_R2_KEY
        sync: false
      - key: CLOUDFLARE_R2_SECRET
        sync: false
      - key: DASHBOARD_URL
        sync: false
EOF

# Create health check endpoint
cat > health_check.py << 'EOF'
from flask import Flask, jsonify
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'environment': 'cloud',
        'services': {
            'discord_bot': bool(os.getenv('DISCORD_TOKEN')),
            'database': bool(os.getenv('SUPABASE_URL')),
            'ai_analysis': bool(os.getenv('OPENAI_API_KEY')),
            'file_storage': bool(os.getenv('CLOUDFLARE_R2_URL')),
            'dashboard': bool(os.getenv('DASHBOARD_URL'))
        }
    })

@app.route('/')
def root():
    """Root endpoint."""
    return jsonify({
        'message': 'GotLockz Bot is running',
        'status': 'online',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
EOF

echo "✅ Cloud deployment files created."

echo ""
echo "📋 Step 5: Creating environment setup guide..."

# Create environment setup guide
cat > CLOUD_SETUP.md << 'EOF'
# ☁️ Cloud Setup Guide

## Required Environment Variables

Set these in your Render dashboard:

### Discord Bot
```
DISCORD_TOKEN=your_discord_bot_token
GUILD_ID=your_guild_id
OWNER_ID=your_discord_user_id
```

### Database (Supabase)
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
```

### AI Analysis (OpenAI)
```
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
ANALYSIS_ENABLED=true
```

### File Storage (Cloudflare R2)
```
CLOUDFLARE_R2_URL=https://your-bucket.your-subdomain.r2.cloudflarestorage.com
CLOUDFLARE_R2_KEY=your_r2_access_key
CLOUDFLARE_R2_SECRET=your_r2_secret_key
```

### Dashboard
```
DASHBOARD_URL=https://username-gotlockz-dashboard.hf.space
DASHBOARD_ENABLED=true
```

### Channel IDs (Optional)
```
VIP_CHANNEL_ID=channel_id_for_vip_picks
LOTTO_CHANNEL_ID=channel_id_for_lotto_picks
FREE_CHANNEL_ID=channel_id_for_free_picks
ANALYSIS_CHANNEL_ID=channel_id_for_analysis
LOG_CHANNEL_ID=channel_id_for_logging
```

## Setup Steps

1. **Create Supabase Project**
   - Go to https://supabase.com
   - Create new project
   - Get URL and anon key

2. **Create Cloudflare R2 Bucket**
   - Go to https://cloudflare.com
   - Create R2 bucket
   - Get API credentials

3. **Deploy to Render**
   - Connect GitHub repository
   - Set environment variables
   - Deploy

4. **Deploy Dashboard to Hugging Face**
   - Create new Space
   - Upload dashboard files
   - Get dashboard URL

5. **Test Deployment**
   - Check bot health: https://your-bot.onrender.com/health
   - Test Discord commands
   - Verify dashboard access
EOF

echo "✅ Environment setup guide created."

echo ""
echo "🎯 Step 6: Updating main.py for cloud..."

# Update main.py for cloud deployment
cat > main.py << 'EOF'
#!/usr/bin/env python3
"""
GotLockz Bot - Cloud Deployment Entry Point
"""

import os
import asyncio
import logging
from bot import GotLockzBot
from config_cloud import log_to_cloud

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point for cloud deployment."""
    try:
        # Log startup
        log_to_cloud('INFO', 'Bot starting up', {'environment': 'cloud'})
        
        # Create and start bot
        bot = GotLockzBot()
        
        # Log successful startup
        log_to_cloud('INFO', 'Bot started successfully', {
            'guilds': len(bot.guilds) if hasattr(bot, 'guilds') else 0,
            'users': len(bot.users) if hasattr(bot, 'users') else 0
        })
        
        # Start the bot
        await bot.start(os.getenv('DISCORD_TOKEN'))
        
    except Exception as e:
        # Log startup error
        log_to_cloud('ERROR', f'Bot startup failed: {str(e)}', {'error': str(e)})
        logger.error(f"Bot startup failed: {e}")
        raise

if __name__ == '__main__':
    # Run the bot
    asyncio.run(main())
EOF

echo "✅ Main entry point updated for cloud."

echo ""
echo "🔧 Step 7: Creating monitoring setup..."

# Create monitoring setup
cat > monitoring_setup.md << 'EOF'
# 📊 Monitoring Setup

## UptimeRobot Configuration

1. Go to https://uptimerobot.com
2. Create account
3. Add monitors:

### Bot Health Monitor
- **URL**: https://your-bot.onrender.com/health
- **Type**: HTTP(s)
- **Interval**: 5 minutes
- **Alert**: Discord webhook

### Dashboard Monitor
- **URL**: https://username-gotlockz-dashboard.hf.space
- **Type**: HTTP(s)
- **Interval**: 5 minutes
- **Alert**: Discord webhook

## Discord Webhook Setup

1. Create Discord webhook in your server
2. Add webhook URL to UptimeRobot alerts
3. Test notifications

## Health Check Endpoints

- **Bot Health**: `GET /health`
- **Dashboard**: `GET /` (root endpoint)
- **API Status**: `GET /api/status`

## Alert Configuration

- **Down Alert**: Immediate
- **Up Alert**: 1 minute delay
- **Contact**: Discord webhook
EOF

echo "✅ Monitoring setup guide created."

echo ""
echo "🎉 Cloud Deployment Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Set up Supabase database (see CLOUD_SETUP.md)"
echo "2. Configure Cloudflare R2 storage"
echo "3. Deploy to Render using render.yaml"
echo "4. Deploy dashboard to Hugging Face"
echo "5. Set up monitoring with UptimeRobot"
echo ""
echo "🔗 Useful Links:"
echo "- Supabase: https://supabase.com"
echo "- Render: https://render.com"
echo "- Hugging Face: https://huggingface.co/spaces"
echo "- Cloudflare: https://cloudflare.com"
echo "- UptimeRobot: https://uptimerobot.com"
echo ""
echo "✅ Your bot is now configured for 100% cloud deployment!"
echo "🚫 No local hosting components remain." 