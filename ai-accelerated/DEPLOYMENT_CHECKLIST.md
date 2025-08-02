# Deployment Checklist - GotLockz Bot

## ✅ Pre-Deployment Checklist

### 1. Code Quality
- [x] All tests passing
- [x] Pick command updated with units validation
- [x] Image processing module integrated
- [x] Test-OCR command ready
- [x] Error handling implemented
- [x] Logging configured

### 2. Dependencies
- [x] package.json updated
- [x] All required packages installed
- [x] Sharp installation handled gracefully
- [x] ES6 modules configured

### 3. Configuration
- [x] Commands configuration updated
- [x] Environment variables documented
- [ ] DISCORD_TOKEN set in Render
- [ ] Other environment variables configured

### 4. Documentation
- [x] README updated
- [x] Command usage documented
- [x] Deployment guide created

## 🚀 Deployment Steps

### Step 1: Git Preparation
```bash
# Check current status
git status

# Add all changes
git add .

# Commit with descriptive message
git commit -m "feat: Add units validation for VIP plays and OCR integration

- Replace notes option with units option for VIP plays
- Add validation logic for units requirement
- Integrate image processing module with OCR
- Add test-ocr command for Discord testing
- Update command configuration and documentation
- Handle Sharp installation issues gracefully"

# Push to repository
git push origin main
```

### Step 2: Render Configuration

#### Environment Variables to Set in Render:
```
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_CLIENT_ID=your_discord_client_id_here
DISCORD_GUILD_ID=your_discord_guild_id_here
```

#### Optional Environment Variables:
```
NODE_ENV=production
LOG_LEVEL=info
RATE_LIMIT_WINDOW=60000
RATE_LIMIT_MAX_REQUESTS=5
```

### Step 3: Command Registration
After deployment, register the updated commands:
```bash
# Deploy commands to Discord
node deploy-commands.js
```

### Step 4: Testing in Discord
1. Test `/pick` command with VIP plays (requires units)
2. Test `/pick` command with Free plays (no units allowed)
3. Test `/test-ocr` command with image upload
4. Verify error messages and validation

## 🔧 Troubleshooting

### Common Issues:

1. **Sharp Installation Error**
   - ✅ Handled gracefully with fallback
   - OCR will use fallback text on Windows

2. **Discord Token Missing**
   - Set DISCORD_TOKEN in Render environment variables
   - Ensure bot has proper permissions

3. **Command Not Found**
   - Run `node deploy-commands.js` after deployment
   - Check bot permissions in Discord

4. **Rate Limiting**
   - Commands have built-in rate limiting
   - Users will see clear error messages

## 📊 Monitoring

### What to Monitor:
- Bot uptime and responsiveness
- Command usage patterns
- Error rates and types
- OCR success rates
- User feedback on new units feature

### Log Locations:
- Render logs: Available in Render dashboard
- Application logs: Check console output
- Error tracking: Built-in error logging

## ✅ Post-Deployment Verification

1. **Bot Status**: `/admin status` should work
2. **Pick Command**: Test all three channel types
3. **OCR Testing**: Upload bet slip images
4. **Error Handling**: Test invalid inputs
5. **Rate Limiting**: Test rapid command usage

## 🎯 Success Criteria

- [ ] Bot starts successfully on Render
- [ ] All commands register properly
- [ ] VIP plays require units input
- [ ] Free plays reject units input
- [ ] OCR processing works (with fallback)
- [ ] Error messages are user-friendly
- [ ] Rate limiting functions correctly

## 📝 Notes

- Sharp installation issues on Windows are handled gracefully
- OCR will use fallback text if Sharp fails to load
- All validation happens before expensive operations
- Commands are designed to be user-friendly with clear error messages 