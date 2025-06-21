# 🔧 Discord Command Sync Troubleshooting Guide

## 🚨 **Your Issue: Old Commands Still Showing**

You're seeing old slash commands (`/analyze_bet`, `/postpick`) instead of the new features we built.

## ✅ **Step-by-Step Solution**

### 1. **Deploy Updated Code**
```bash
# Make sure your hosting platform (Render, Railway, etc.) has the latest code
# Upload the new bot.py file we just created
```

### 2. **Set Environment Variables**
```bash
# In your hosting platform, set:
DISCORD_TOKEN=your_bot_token_here
DASHBOARD_URL=http://your-dashboard-url.com  # Optional
```

### 3. **Force Sync Commands**
Once your bot is deployed and online:
```
/force_sync
```
**Note**: This may take up to 1 hour to update globally due to Discord's caching.

### 4. **Test New Commands**
Try these commands to verify they work:
```
/ping        # Should respond with "🏓 Pong! Bot is online!"
/status      # Should show bot status
/sync        # Should sync picks to dashboard
```

## 🔍 **Why This Happens**

### Discord Command Caching
- Discord caches slash commands globally
- Old commands remain visible until cache expires
- New commands need to be explicitly synced
- Global cache can take up to 1 hour to update

### Bot Permissions
- Bot needs "applications.commands" scope
- Bot must be in the server to sync commands
- Admin permissions may be required for force sync

## 🛠️ **Advanced Troubleshooting**

### Check Bot Permissions
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your bot application
3. Go to "OAuth2" → "URL Generator"
4. Ensure "applications.commands" is selected
5. Re-invite bot with new permissions

### Verify Code Deployment
1. Check hosting platform logs
2. Ensure bot.py is the latest version
3. Verify environment variables are set
4. Test bot connectivity with `/ping`

### Manual Command Sync
If `/force_sync` doesn't work:
1. Remove bot from server
2. Re-invite with proper permissions
3. Wait for commands to sync automatically
4. Or use Discord API to sync manually

## 📋 **Available Commands**

### Slash Commands (New)
- `/ping` - Test bot responsiveness
- `/sync` - Sync picks to dashboard
- `/status` - Check bot and dashboard status
- `/addpick` - Add new pick to dashboard
- `/force_sync` - Force sync all commands

### Prefix Commands (Legacy)
- `!ping` - Test bot responsiveness
- `!sync` - Sync picks to dashboard
- `!status` - Check bot status
- `!addpick` - Add new pick

## ⏰ **Timeline Expectations**

1. **Immediate**: Bot should respond to `/ping`
2. **1-5 minutes**: Commands should sync to your server
3. **Up to 1 hour**: Commands update globally across all servers
4. **24 hours**: Old commands completely removed from cache

## 🆘 **Still Having Issues?**

### Check These:
1. **Bot Online**: Is the bot showing as online in Discord?
2. **Code Deployed**: Is the latest bot.py on your hosting platform?
3. **Environment Variables**: Is DISCORD_TOKEN set correctly?
4. **Permissions**: Does bot have "applications.commands" scope?
5. **Server Access**: Is bot in the server where you're testing?

### Get Help:
1. Check hosting platform logs for errors
2. Test with `/ping` to verify bot responsiveness
3. Try removing and re-adding bot to server
4. Wait 1 hour for global cache to update

## 🎯 **Success Indicators**

You'll know it's working when:
- ✅ `/ping` responds with "🏓 Pong! Bot is online!"
- ✅ `/status` shows bot status
- ✅ `/force_sync` confirms command sync
- ✅ New commands appear in Discord (may take up to 1 hour)
- ✅ Old commands disappear (may take up to 1 hour) 