# 🚀 Render Deployment Guide - AI-Accelerated GotLockz Bot

## ✅ **Prerequisites Met**
- ✅ All APIs stored properly on Render
- ✅ Environment variables configured
- ✅ Health check endpoint added
- ✅ Render configuration ready

---

## 🚀 **Quick Deploy to Render**

### **Option 1: One-Click Deploy (Recommended)**

1. **Click the Deploy Button**
   ```
   [Deploy to Render] - Coming soon
   ```

2. **Configure Environment Variables**
   - All variables are already set to `sync: false` in `render.yaml`
   - Render will prompt you to enter the values from your existing configuration

3. **Deploy**
   - Render will automatically build and deploy your bot
   - Commands will be deployed automatically on startup

### **Option 2: Manual Deploy**

1. **Connect Repository**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   ```
   Name: gotlockz-bot-ai
   Environment: Node
   Build Command: cd ai-accelerated && npm install
   Start Command: cd ai-accelerated && npm run deploy && npm start
   ```

3. **Set Environment Variables**
   Copy these from your existing Render configuration:
   ```
   DISCORD_TOKEN=your_bot_token
   CLIENT_ID=your_client_id
   OPENAI_API_KEY=your_openai_key
   HUGGINGFACE_API_KEY=your_hf_key
   MLB_API_KEY=your_mlb_key
   OPENWEATHER_API_KEY=your_weather_key
   REDIS_URL=your_redis_url
   NODE_ENV=production
   LOG_LEVEL=info
   RATE_LIMIT_COOLDOWN=12000
   DEBUG=false
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy automatically

---

## 📊 **Deployment Status**

### **Build Process**
1. ✅ **Repository Connected**
2. ✅ **Dependencies Installed**
3. ✅ **Commands Deployed**
4. ✅ **Bot Started**
5. ✅ **Health Check Active**

### **Monitoring**
- **Health Check**: `https://your-app.onrender.com/health`
- **Logs**: Available in Render dashboard
- **Metrics**: CPU, memory, and response times

---

## 🔧 **Environment Variables Reference**

### **Required Variables**
```bash
DISCORD_TOKEN=your_discord_bot_token
CLIENT_ID=your_discord_client_id
```

### **AI Services (Optional but Recommended)**
```bash
OPENAI_API_KEY=your_openai_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
```

### **Data APIs (Optional)**
```bash
MLB_API_KEY=your_mlb_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
REDIS_URL=your_redis_url
```

### **Configuration**
```bash
NODE_ENV=production
LOG_LEVEL=info
RATE_LIMIT_COOLDOWN=12000
DEBUG=false
```

---

## 🎯 **Post-Deployment Testing**

### **1. Health Check**
```bash
curl https://your-app.onrender.com/health
```
Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "uptime": 123.456,
  "memory": {...},
  "version": "1.0.0"
}
```

### **2. Discord Commands**
- `/admin ping` - Test bot responsiveness
- `/admin status` - Check system health
- `/pick` - Test betting analysis (with image)

### **3. Log Monitoring**
- Check Render logs for any errors
- Verify bot startup messages
- Monitor command execution

---

## 🔄 **Auto-Deployment**

### **GitHub Integration**
- ✅ **Auto-deploy on push** to main branch
- ✅ **Build status** monitoring
- ✅ **Rollback** capability

### **Environment Updates**
- Environment variables can be updated without redeploy
- Changes take effect on next restart
- No downtime for configuration changes

---

## 📈 **Performance Monitoring**

### **Render Metrics**
- **CPU Usage**: Monitor during peak times
- **Memory Usage**: Should stay under 2GB
- **Response Time**: Target <5 seconds
- **Uptime**: 99.9% availability

### **Bot Metrics**
- **Command Success Rate**: >95%
- **OCR Accuracy**: >95%
- **AI Response Time**: <3 seconds
- **Error Rate**: <1%

---

## 🛠️ **Troubleshooting**

### **Common Issues**

1. **Bot Not Starting**
   ```bash
   # Check logs in Render dashboard
   # Verify DISCORD_TOKEN is correct
   # Ensure CLIENT_ID matches your bot
   ```

2. **Commands Not Working**
   ```bash
   # Check if deploy-commands ran successfully
   # Verify bot has proper permissions
   # Check guild ID if using guild-specific commands
   ```

3. **AI Services Failing**
   ```bash
   # Verify API keys are correct
   # Check API rate limits
   # Monitor OpenAI/HuggingFace quotas
   ```

4. **High Memory Usage**
   ```bash
   # Check for memory leaks in logs
   # Monitor image processing
   # Consider upgrading plan if needed
   ```

### **Log Analysis**
```bash
# Common log patterns to watch for:
"Ready! Logged in as" - Bot started successfully
"Successfully reloaded X commands" - Commands deployed
"OCR analysis completed" - Image processing working
"AI analysis completed" - AI services functioning
```

---

## 🚀 **Scaling Options**

### **Current Plan: Starter**
- **CPU**: 0.1 cores
- **RAM**: 512MB
- **Cost**: Free tier

### **Upgrade Options**
- **Standard**: 0.5 cores, 1GB RAM ($7/month)
- **Pro**: 1 core, 2GB RAM ($25/month)
- **Custom**: Based on needs

### **When to Upgrade**
- **High CPU usage** (>80% consistently)
- **Memory pressure** (>80% RAM usage)
- **Slow response times** (>10 seconds)
- **High error rates** (>5%)

---

## 🎉 **Success Checklist**

- ✅ **Repository connected to Render**
- ✅ **Environment variables configured**
- ✅ **Build successful**
- ✅ **Bot online in Discord**
- ✅ **Commands responding**
- ✅ **Health check passing**
- ✅ **Logs clean**
- ✅ **Performance acceptable**

---

## 📞 **Support**

### **Render Support**
- **Documentation**: [render.com/docs](https://render.com/docs)
- **Status**: [status.render.com](https://status.render.com)
- **Community**: [community.render.com](https://community.render.com)

### **Bot Support**
- **Discord**: Join our support server
- **GitHub**: Issue tracker
- **Documentation**: README_AI.md

---

**🚀 Your AI-accelerated GotLockz Bot is ready to deploy on Render!**

With all APIs properly stored and configured, deployment should be seamless and take only a few minutes. 