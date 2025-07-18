# Quick Start Guide - Get Your Discord Bot Running NOW! 🚀

## 🎯 What We're Doing Right Now

This guide will get your Discord bot connected and responding in **under 30 minutes**.

## ⚡ Step 1: Discord Bot Setup (5 minutes)

### 1.1 Create Discord Application
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"**
3. Name: `GotLockz Bot`
4. Description: `MLB Betting Analysis Bot`
5. Click **"Create"**

### 1.2 Create Bot User
1. In your application, go to **"Bot"** section
2. Click **"Add Bot"**
3. Username: `GotLockz Bot`
4. **IMPORTANT**: Enable **"Message Content Intent"**
5. Click **"Save Changes"**
6. **COPY THE BOT TOKEN** (click "Reset Token" if needed)

### 1.3 Get Application ID
1. Go to **"General Information"** section
2. **COPY THE APPLICATION ID**

### 1.4 Invite Bot to Your Server
1. Go to **"OAuth2"** → **"URL Generator"**
2. Scopes: Check `bot` and `applications.commands`
3. Bot Permissions: Check these:
   - ✅ Send Messages
   - ✅ Use Slash Commands
   - ✅ Embed Links
   - ✅ Read Message History
4. **COPY THE GENERATED URL**
5. Open the URL in a new tab
6. Select your server and authorize

## ⚡ Step 2: Environment Setup (2 minutes)

### 2.1 Create .env file
```bash
cd discord
cp env.example .env
```

### 2.2 Add Your Credentials
Edit `.env` file and add:
```bash
DISCORD_TOKEN=your_bot_token_here
DISCORD_CLIENT_ID=your_application_id_here
DISCORD_GUILD_ID=your_server_id_here
NODE_ENV=development
LOG_LEVEL=debug
```

**To get your Guild ID:**
1. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
2. Right-click your server name
3. Click "Copy Server ID"

## ⚡ Step 3: Install & Deploy (3 minutes)

### 3.1 Install Dependencies
```bash
npm install
```

### 3.2 Deploy Commands
```bash
npm run deploy
```

### 3.3 Start the Bot
```bash
npm run dev
```

## ⚡ Step 4: Test Your Bot (2 minutes)

### 4.1 Check Bot Status
1. Go to your Discord server
2. You should see "GotLockz Bot" online
3. Try typing `/help`
4. You should see a help message with commands

### 4.2 Test Basic Commands
- Type `/ping` - Should show bot status
- Type `/help` - Should show command list

## 🎉 Success! Your Bot is Working!

If you see the bot responding to commands, **CONGRATULATIONS!** 🎉

## 🔧 Troubleshooting

### Bot Not Responding?
1. Check if bot is online in your server
2. Verify bot token in `.env` file
3. Check console for error messages
4. Make sure "Message Content Intent" is enabled

### Commands Not Working?
1. Run `npm run deploy` again
2. Wait 1-2 minutes for Discord to register commands
3. Check if bot has proper permissions

### Permission Errors?
1. Make sure bot has these permissions:
   - Send Messages
   - Use Slash Commands
   - Embed Links
2. Re-invite bot with correct permissions

## 🚀 Next Steps

Once your bot is working:

1. **Test JSON Processing** - Send this to your Discord channel:
```json
{
  "teams": {
    "away": "Yankees",
    "home": "Red Sox"
  },
  "pick": "Yankees ML -150",
  "odds": "-150",
  "confidence": "85%",
  "analysis": "The Yankees are looking strong today!",
  "venue": "Fenway Park",
  "gameTime": "2024-01-15T19:00:00Z",
  "broadcast": "ESPN"
}
```

2. **Add More Commands** - Follow the full implementation plan
3. **Integrate with OCR** - When Windows developer is ready

## 📞 Need Help?

- Check the console output for error messages
- Verify all environment variables are set
- Make sure bot has proper Discord permissions
- Check the full implementation plan for detailed steps

---

**GotLockz Family** - Let's get this money! 💰

*21+ Only • Please bet responsibly* 