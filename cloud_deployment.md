# ☁️ Cloud-Only Deployment Guide

## 🚫 **No Local Hosting Policy**

This guide ensures **ZERO** code or data is hosted locally. Everything runs in the cloud for security, scalability, and accessibility.

## 🏗️ **Cloud Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Discord Bot   │    │   Dashboard     │    │   Database      │
│   (Render)      │◄──►│   (Hugging Face)│◄──►│   (Cloud DB)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Monitoring    │    │   File Storage  │    │   Logs & Analytics│
│   (UptimeRobot) │    │   (Cloudflare)  │    │   (Cloud Logs)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 **Deployment Platforms**

### 1. **Bot Hosting: Render (Free Tier)**
- **Service**: Web Service
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`
- **Environment**: Python 3.9
- **Auto-deploy**: On Git push

### 2. **Dashboard: Hugging Face Spaces (Free)**
- **Framework**: Gradio + Flask
- **URL**: `https://username-gotlockz-dashboard.hf.space`
- **Auto-deploy**: On Git push
- **HTTPS**: Automatic

### 3. **Database: Supabase (Free Tier)**
- **Type**: PostgreSQL
- **Backup**: Automatic
- **API**: REST + Real-time
- **Auth**: Built-in

### 4. **File Storage: Cloudflare R2 (Free Tier)**
- **Purpose**: Image storage for betting slips
- **CDN**: Global
- **Cost**: Free up to 10GB

### 5. **Monitoring: UptimeRobot (Free)**
- **Checks**: Bot and dashboard health
- **Alerts**: Discord notifications
- **Uptime**: 99.9%+ monitoring

## 📋 **Setup Steps**

### Step 1: Prepare Repository
```bash
# Remove local hosting files
rm -rf dashboard/
rm -rf gotlockz-dashboard/
rm -rf hf_deploy/
rm jarvis_dashboard.py
rm run_dashboard.py
rm start_dashboard.sh
rm temp_monitor.sh
rm jarvis.py
rm start_jarvis.sh

# Keep only cloud deployment files
# - main.py (bot entry point)
# - bot.py (bot logic)
# - commands.py (commands)
# - requirements.txt
# - Dockerfile
# - .github/workflows/ (CI/CD)
```

### Step 2: Set Up Supabase Database
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Get connection string
4. Create tables:

```sql
-- Picks table
CREATE TABLE picks (
    id SERIAL PRIMARY KEY,
    pick_number INTEGER NOT NULL,
    pick_type TEXT NOT NULL,
    bet_details JSONB NOT NULL,
    odds TEXT,
    analysis JSONB,
    confidence_score INTEGER,
    edge_percentage REAL,
    result TEXT,
    profit_loss REAL,
    image_url TEXT,
    user_id BIGINT,
    user_name TEXT,
    posted_at TIMESTAMP DEFAULT NOW()
);

-- Bot logs table
CREATE TABLE bot_logs (
    id SERIAL PRIMARY KEY,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- User permissions table
CREATE TABLE user_permissions (
    user_id BIGINT PRIMARY KEY,
    vip_roles TEXT[],
    admin_roles TEXT[],
    blocked BOOLEAN DEFAULT FALSE,
    cooldowns JSONB,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Step 3: Deploy Bot to Render
1. Go to [render.com](https://render.com)
2. Connect GitHub repository
3. Create new Web Service
4. Configure:
   ```
   Name: gotlockz-bot
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python main.py
   ```

5. Set environment variables:
   ```
   DISCORD_TOKEN=your_bot_token
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   OPENAI_API_KEY=your_openai_key
   CLOUDFLARE_R2_URL=your_r2_url
   CLOUDFLARE_R2_KEY=your_r2_key
   CLOUDFLARE_R2_SECRET=your_r2_secret
   DASHBOARD_URL=https://username-gotlockz-dashboard.hf.space
   ```

### Step 4: Deploy Dashboard to Hugging Face
1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Create new Space:
   - **Owner**: Your username
   - **Space name**: `gotlockz-dashboard`
   - **SDK**: Gradio
   - **License**: MIT

3. Upload dashboard files:
   ```bash
   # Create dashboard package
   mkdir dashboard-deploy
   cd dashboard-deploy
   
   # Create app.py
   cat > app.py << 'EOF'
   import gradio as gr
   import requests
   import json
   from datetime import datetime
   
   def get_picks():
       try:
           response = requests.get(f"{DASHBOARD_URL}/api/picks")
           return response.json()
       except:
           return []
   
   def create_dashboard():
       with gr.Blocks(title="GotLockz Dashboard") as demo:
           gr.HTML("<h1>🏆 GotLockz Dashboard</h1>")
           
           with gr.Row():
               with gr.Column():
                   gr.HTML("<h3>📊 Live Picks</h3>")
                   picks_table = gr.Dataframe(headers=["ID", "Type", "Details", "Posted"])
                   
                   def refresh_picks():
                       picks = get_picks()
                       return [[p['id'], p['pick_type'], p['bet_details'], p['posted_at']] for p in picks]
                   
                   refresh_btn = gr.Button("🔄 Refresh")
                   refresh_btn.click(refresh_picks, outputs=picks_table)
                   
               with gr.Column():
                   gr.HTML("<h3>📈 Statistics</h3>")
                   stats_text = gr.Textbox(label="Bot Status", interactive=False)
                   
                   def get_stats():
                       try:
                           response = requests.get(f"{DASHBOARD_URL}/api/stats")
                           return response.json()
                       except:
                           return {"status": "Dashboard offline"}
                   
                   stats_btn = gr.Button("📊 Get Stats")
                   stats_btn.click(get_stats, outputs=stats_text)
       
       return demo
   
   demo = create_dashboard()
   demo.launch()
   EOF
   
   # Create requirements.txt
   cat > requirements.txt << 'EOF'
   gradio>=4.0.0
   requests>=2.28.0
   EOF
   
   # Upload to Hugging Face
   git clone https://huggingface.co/spaces/YOUR_USERNAME/gotlockz-dashboard
   cp app.py requirements.txt gotlockz-dashboard/
   cd gotlockz-dashboard
   git add .
   git commit -m "Initial dashboard deployment"
   git push
   ```

### Step 5: Set Up Cloudflare R2 for Images
1. Go to [cloudflare.com](https://cloudflare.com)
2. Create R2 bucket: `gotlockz-images`
3. Get API credentials
4. Configure CORS for web access

### Step 6: Set Up Monitoring
1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Create monitors:
   - Bot health: `https://your-bot.onrender.com/health`
   - Dashboard: `https://username-gotlockz-dashboard.hf.space`
3. Set up Discord webhook for alerts

## 🔧 **Updated Code Structure**

### main.py (Bot Entry Point)
```python
import os
import asyncio
from bot import GotLockzBot

async def main():
    bot = GotLockzBot()
    await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    asyncio.run(main())
```

### config.py (Cloud Configuration)
```python
import os
from supabase import create_client, Client

# Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Cloudflare R2
R2_URL = os.getenv('CLOUDFLARE_R2_URL')
R2_KEY = os.getenv('CLOUDFLARE_R2_KEY')
R2_SECRET = os.getenv('CLOUDFLARE_R2_SECRET')

# Dashboard
DASHBOARD_URL = os.getenv('DASHBOARD_URL')
```

### requirements.txt (Cloud Dependencies)
```
discord.py>=2.3.0
supabase>=1.0.0
cloudflare>=2.19.0
openai>=1.0.0
pillow>=9.0.0
pytesseract>=0.3.10
requests>=2.28.0
python-dotenv>=1.0.0
```

## 🛡️ **Security Benefits**

### ✅ **No Local Data**
- All data stored in cloud databases
- No local file storage
- Automatic backups
- GDPR compliant

### ✅ **No Local Code Execution**
- All processing in cloud
- No local development environment needed
- Automatic scaling
- Zero maintenance

### ✅ **Secure Access**
- HTTPS everywhere
- API key authentication
- Role-based permissions
- Audit logging

## 📊 **Cost Analysis**

| Service | Free Tier | Paid Tier | Monthly Cost |
|---------|-----------|-----------|--------------|
| Render | 750 hours | $7/month | $0-7 |
| Hugging Face | Unlimited | $9/month | $0-9 |
| Supabase | 500MB | $25/month | $0-25 |
| Cloudflare R2 | 10GB | $0.015/GB | $0-1 |
| UptimeRobot | 50 monitors | $7/month | $0-7 |

**Total**: $0-49/month (typically $0-15 for most users)

## 🚀 **Deployment Commands**

```bash
# Deploy everything to cloud
./deploy_cloud.sh

# This script will:
# 1. Remove local hosting files
# 2. Deploy bot to Render
# 3. Deploy dashboard to Hugging Face
# 4. Set up monitoring
# 5. Configure environment variables
```

## 🎯 **Next Steps**

1. **Remove Local Files**: Delete all local hosting components
2. **Set Up Cloud Services**: Configure Render, Hugging Face, Supabase
3. **Deploy**: Use automated deployment scripts
4. **Test**: Verify everything works in cloud
5. **Monitor**: Set up health checks and alerts

Your bot will now be **100% cloud-hosted** with zero local dependencies! 🎉 