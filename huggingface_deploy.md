# 🚀 Deploy Dashboard to Hugging Face Spaces

## Quick Setup

### 1. Create Hugging Face Space
1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Choose:
   - **Owner**: Your username
   - **Space name**: `gotlockz-dashboard`
   - **Space SDK**: **Gradio** (best for Flask apps)
   - **License**: MIT

### 2. Upload Your Dashboard
```bash
# Clone the space
git clone https://huggingface.co/spaces/YOUR_USERNAME/gotlockz-dashboard
cd gotlockz-dashboard

# Copy dashboard files
cp -r ../gotlockz-bot/dashboard/* .
cp ../gotlockz-bot/requirements.txt .

# Commit and push
git add .
git commit -m "Initial dashboard deployment"
git push
```

### 3. Configure Environment Variables
In your Hugging Face Space settings:
- Go to Settings → Repository secrets
- Add:
  - `DISCORD_TOKEN` (if needed)
  - Any other environment variables

### 4. Update Bot Configuration
Once deployed, update your bot's `DASHBOARD_URL`:
```bash
export DASHBOARD_URL="https://YOUR_USERNAME-gotlockz-dashboard.hf.space"
```

## Benefits
- ✅ Free hosting
- ✅ Automatic HTTPS
- ✅ Git-based deployment
- ✅ No local disk space usage
- ✅ Professional URL

## Alternative: Render/Railway
If you prefer other platforms:
- **Render**: Free tier, easy deployment
- **Railway**: Good free tier, simple setup
- **Heroku**: Paid but reliable

## Next Steps
1. Deploy dashboard to Hugging Face
2. Update bot's `DASHBOARD_URL` environment variable
3. Test `/sync` and `/status` commands
4. Enjoy free hosting! 🎉 