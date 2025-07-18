# 🔍 **RENDER LOGGING SETUP GUIDE**

## 🎯 **Overview**

This guide ensures you can see detailed error logs on Render when Discord commands fail. The bot now includes comprehensive logging that will help you debug any issues.

---

## 📊 **What Gets Logged**

### **1. Command Execution**
- ✅ **Command Start**: When `/pick` is initiated
- ✅ **Service Imports**: Each service loading step
- ✅ **Processing Steps**: OCR, AI analysis, message creation
- ✅ **Success/Failure**: Final result with timing
- ✅ **Error Details**: Full stack traces and context

### **2. Error Tracking**
- ✅ **Uncaught Exceptions**: Global error handling
- ✅ **Service Failures**: Individual service errors
- ✅ **Import Errors**: Module loading issues
- ✅ **Discord API Errors**: Bot interaction failures

### **3. Performance Metrics**
- ✅ **Response Times**: How long each step takes
- ✅ **Memory Usage**: System resource monitoring
- ✅ **Command Counts**: Usage statistics

---

## 🔧 **How to View Logs on Render**

### **Method 1: Render Dashboard**
1. Go to your Render dashboard
2. Click on your GotLockz Bot service
3. Click the **"Logs"** tab
4. You'll see real-time logs with timestamps

### **Method 2: Health Check Endpoint**
- **URL**: `https://your-bot-name.onrender.com/health`
- **Shows**: Bot status, uptime, system stats
- **Useful for**: Quick health checks

### **Method 3: Development Logs (Local)**
- **URL**: `https://your-bot-name.onrender.com/logs` (development only)
- **Shows**: Recent error and combined logs
- **Useful for**: Detailed debugging

---

## 📝 **Log Format Examples**

### **Successful Command**
```
🚀 [pick_1731897600000_abc123] Pick command started by username (123456789)
📦 [pick_1731897600000_abc123] Importing services...
✅ [pick_1731897600000_abc123] OCR service imported
✅ [pick_1731897600000_abc123] MLB service imported
✅ [pick_1731897600000_abc123] AI service imported
✅ [pick_1731897600000_abc123] Betting service imported
🔍 [pick_1731897600000_abc123] Starting OCR analysis...
✅ [pick_1731897600000_abc123] OCR completed in 1500ms
📊 [pick_1731897600000_abc123] Parsing bet slip data...
✅ [pick_1731897600000_abc123] Bet slip parsed: 1 legs found
🏟️ [pick_1731897600000_abc123] Fetching game data...
✅ [pick_1731897600000_abc123] Game data fetched successfully
🤖 [pick_1731897600000_abc123] Generating AI analysis...
✅ [pick_1731897600000_abc123] AI analysis completed in 2000ms
📝 [pick_1731897600000_abc123] Creating betting message...
✅ [pick_1731897600000_abc123] Message created successfully
🎉 [pick_1731897600000_abc123] Pick command completed successfully in 4500ms
```

### **Failed Command**
```
🚀 [pick_1731897600000_abc123] Pick command started by username (123456789)
📦 [pick_1731897600000_abc123] Importing services...
✅ [pick_1731897600000_abc123] OCR service imported
✅ [pick_1731897600000_abc123] MLB service imported
✅ [pick_1731897600000_abc123] AI service imported
❌ [pick_1731897600000_abc123] Betting service import failed: Cannot find module
💥 [pick_1731897600000_abc123] Pick command failed after 500ms: Betting service import failed
```

---

## 🚨 **Common Error Patterns**

### **1. Service Import Failures**
```
❌ [pick_xxx] OCR service import failed: Cannot find module './src/services/ocrService.js'
```
**Solution**: Check file paths and module exports

### **2. OCR Processing Errors**
```
❌ [pick_xxx] OCR failed: All OCR engines failed
```
**Solution**: Check image quality or OCR service configuration

### **3. AI Analysis Failures**
```
⚠️ [pick_xxx] AI analysis failed: API key not found, using fallback
```
**Solution**: Check environment variables for AI services

### **4. Message Creation Failures**
```
❌ [pick_xxx] Message creation failed: Cannot read properties of undefined
```
**Solution**: Check data validation and sanitization

---

## 🔍 **Debugging Steps**

### **Step 1: Check Render Logs**
1. Go to Render dashboard → Your service → Logs
2. Look for error messages with `💥` or `❌`
3. Note the command ID for tracking

### **Step 2: Check Health Endpoint**
```
GET https://your-bot-name.onrender.com/health
```
Should return:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-18T21:30:00.000Z",
  "uptime": 3600,
  "stats": {
    "uptime": "1h 0m",
    "memory": "45MB",
    "cpu": "120ms",
    "commands": "15",
    "servers": "1"
  }
}
```

### **Step 3: Check Environment Variables**
Ensure these are set in Render:
- `DISCORD_TOKEN`
- `DISCORD_CLIENT_ID`
- `GUILD_ID`
- `OWNER_ID`

### **Step 4: Test Commands**
1. Try `/admin ping` first (simplest command)
2. Then try `/pick` with a clear image
3. Check logs for each step

---

## 📋 **Log Levels**

### **Console Output (Render Logs)**
- 🚀 **Info**: Command starts, service loads
- ✅ **Success**: Operations completed
- ⚠️ **Warning**: Non-critical issues
- ❌ **Error**: Operation failures
- 💥 **Critical**: Unhandled errors

### **File Logs (Development)**
- `logs/error.log`: Only error messages
- `logs/combined.log`: All log levels

---

## 🛠️ **Troubleshooting**

### **If You See "Application Did Not Respond"**
1. Check Render logs for timeout errors
2. Look for service import failures
3. Verify environment variables
4. Check if bot has proper permissions

### **If Commands Don't Load**
1. Check command import errors in logs
2. Verify file paths are correct
3. Ensure all dependencies are installed

### **If Services Fail**
1. Check individual service logs
2. Verify API keys and endpoints
3. Look for network connectivity issues

---

## 🎯 **Quick Commands**

### **Check Bot Status**
```bash
curl https://your-bot-name.onrender.com/health
```

### **View Recent Logs (Development)**
```bash
curl https://your-bot-name.onrender.com/logs
```

### **Monitor Logs in Real-time**
1. Go to Render dashboard
2. Click on your service
3. Click "Logs" tab
4. Watch for new entries

---

## ✅ **Success Indicators**

### **Bot is Working When You See:**
- ✅ `🤖 Bot logged in as GotLockz Bot#1234`
- ✅ `📦 Loading commands...`
- ✅ `✅ Loaded 5 commands`
- ✅ `🎉 Bot setup complete!`

### **Commands are Working When You See:**
- ✅ `🚀 [pick_xxx] Pick command started by username`
- ✅ `✅ [pick_xxx] OCR service imported`
- ✅ `✅ [pick_xxx] Message created successfully`
- ✅ `🎉 [pick_xxx] Pick command completed successfully`

---

## 🚀 **Next Steps**

1. **Deploy to Render** with these logging enhancements
2. **Test the `/pick` command** with a bet slip image
3. **Check Render logs** for any errors
4. **Use the health endpoint** to monitor bot status
5. **Contact support** with specific error IDs if issues persist

**With this logging setup, you'll have complete visibility into what's happening when commands fail!** 🔍 