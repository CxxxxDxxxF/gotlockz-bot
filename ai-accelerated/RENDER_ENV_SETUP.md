# Render Environment Setup for Command Deployment

## 🎯 **To Update Discord Commands, Set This in Render:**

### **Required Environment Variables:**
```
DISCORD_TOKEN=your_bot_token
DISCORD_CLIENT_ID=your_client_id
DISCORD_GUILD_ID=your_server_id
NODE_ENV=production
```

### **Step-by-Step Instructions:**

1. **Go to your Render Dashboard**
2. **Select your bot service**
3. **Go to "Environment" tab**
4. **Add/Update these variables:**

   | Variable | Value | Description |
   |----------|-------|-------------|
   | `DISCORD_TOKEN` | `your_bot_token` | Your Discord bot token |
   | `DISCORD_CLIENT_ID` | `your_client_id` | Your bot's client ID |
   | `DISCORD_GUILD_ID` | `your_server_id` | Your Discord server ID |
   | `NODE_ENV` | `production` | **This triggers command deployment** |

5. **Click "Save Changes"**
6. **Redeploy your service**

### **What Happens:**
- Setting `NODE_ENV=production` triggers automatic command deployment
- Bot will deploy updated commands to Discord on startup
- Discord cache will be updated with new "units" option

### **Alternative: Manual Deployment**
If you want to deploy commands manually, you can also:
1. Go to Render dashboard
2. Open your service logs
3. Run: `node render-deploy-commands.js`

## 🎯 **Expected Result:**
After deployment, when you type `/pick` and select "VIP Play", you should see:
- ✅ `channel_type: VIP Play`
- ✅ `image: [attachment]`
- ✅ `units: [text]` ← **NEW OPTION!**
- ✅ `debug: [boolean]`

**The "notes" option should be gone and replaced with "units"!** 