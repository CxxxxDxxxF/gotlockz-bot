# 🔧 Deployment Troubleshooting Guide

## 🚨 **Common Issues & Solutions**

### **1. npm ci Error - No package-lock.json**

**Error:**
```
npm error The `npm ci` command can only install with an existing package-lock.json
```

**Solution:**
- ✅ **Fixed**: Updated build command to use correct directory
- ✅ **Fixed**: Added deployment script for proper setup
- ✅ **Fixed**: Updated Render configuration

**Current Configuration:**
```yaml
buildCommand: cd ai-accelerated && npm ci --only=production
startCommand: cd ai-accelerated && ./deploy.sh
```

### **2. Directory Structure Issues**

**Problem:** Build process can't find files

**Solution:**
```
Repository Structure:
├── ai-accelerated/
│   ├── package.json          ✅
│   ├── package-lock.json     ✅
│   ├── src/                  ✅
│   ├── deploy.sh            ✅
│   └── render.yaml          ✅
└── (other files)
```

### **3. Environment Variables**

**Problem:** Bot can't access APIs

**Solution:**
- ✅ Copy all 11 variables from your existing Render config
- ✅ Ensure `DISCORD_TOKEN` and `CLIENT_ID` are set
- ✅ Verify API keys are correct

### **4. Health Check Failures**

**Problem:** `/health` endpoint not responding

**Solution:**
- ✅ Express server starts on port 3000
- ✅ Health check endpoint added
- ✅ Monitoring configured

---

## 🚀 **Deployment Checklist**

### **Pre-Deployment**
- ✅ Repository connected to Render
- ✅ Environment variables copied
- ✅ Build commands updated
- ✅ Deployment script ready

### **During Deployment**
- ✅ Build successful (npm ci)
- ✅ Dependencies installed
- ✅ Commands deployed
- ✅ Bot started
- ✅ Health check active

### **Post-Deployment**
- ✅ Health endpoint responding
- ✅ Bot online in Discord
- ✅ Commands working
- ✅ Logs clean

---

## 📊 **Expected Log Output**

### **Successful Deployment:**
```
🚀 Starting AI-Accelerated GotLockz Bot Deployment...
📦 Installing dependencies...
📁 Creating logs directory...
🤖 Deploying Discord commands...
🚀 Starting bot...
Health check server running on port 3000
Ready! Logged in as GotLockz Bot#1234
GotLockz Bot is online and ready for action! 🚀
```

### **Common Error Patterns:**
```
❌ Error: package.json not found
→ Check directory structure

❌ npm ci failed
→ Verify package-lock.json exists

❌ Discord token invalid
→ Check DISCORD_TOKEN environment variable

❌ Commands not deployed
→ Verify CLIENT_ID and permissions
```

---

## 🔄 **Quick Fixes**

### **If Build Fails:**
1. Check Render logs
2. Verify environment variables
3. Ensure repository is up to date
4. Try manual deployment

### **If Bot Won't Start:**
1. Check Discord token
2. Verify bot permissions
3. Check guild ID if using guild commands
4. Review error logs

### **If Commands Don't Work:**
1. Check if deploy-commands ran
2. Verify bot has proper permissions
3. Check channel IDs
4. Test with `/admin ping`

---

## 📞 **Support**

### **Render Support:**
- **Logs**: Check Render dashboard
- **Status**: [status.render.com](https://status.render.com)
- **Docs**: [render.com/docs](https://render.com/docs)

### **Bot Issues:**
- **Discord**: Check bot permissions
- **API Keys**: Verify all keys are valid
- **Channels**: Ensure channel IDs are correct

---

**🎯 With these fixes, deployment should be smooth and successful!** 