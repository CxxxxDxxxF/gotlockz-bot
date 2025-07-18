# 🚀 GotLockz Bot - AI Accelerated Version

A sophisticated MLB Discord bot with AI-powered OCR, multi-model analysis, and real-time betting insights.

## ✨ **Features**

### 🤖 **AI-Powered Analysis**
- **Multi-Model AI**: GPT-4, Claude, and local models for comprehensive analysis
- **Advanced OCR**: Tesseract.js with image preprocessing for accurate text extraction
- **Smart Betting**: AI-driven risk assessment and confidence scoring
- **Real-time Insights**: Live game data and statistical analysis

### 📊 **Betting Analysis**
- **VIP Plays**: Premium analysis with high confidence
- **Free Plays**: Community picks with AI insights
- **Lotto Tickets**: High-risk, high-reward analysis
- **Risk Assessment**: Multi-factor risk evaluation

### 🛠️ **Technical Excellence**
- **Modern Architecture**: ES6 modules, async/await, proper error handling
- **Rate Limiting**: Intelligent request throttling
- **Caching**: Redis-based caching for performance
- **Logging**: Comprehensive Winston logging
- **Monitoring**: Real-time system stats and health checks

## 🚀 **Quick Start**

### **1. Prerequisites**
- Node.js 18+ 
- Discord Bot Token
- OpenAI API Key (optional)
- HuggingFace API Key (optional)

### **2. Installation**
```bash
# Clone the repository
git clone <repository-url>
cd gotlockz-bot/ai-accelerated

# Install dependencies
npm install

# Copy environment file
cp env.example .env

# Edit .env with your credentials
nano .env
```

### **3. Configuration**
```bash
# Required variables in .env:
DISCORD_TOKEN=your_bot_token
CLIENT_ID=your_client_id
OPENAI_API_KEY=your_openai_key  # Optional
HUGGINGFACE_API_KEY=your_hf_key  # Optional
```

### **4. Deploy Commands**
```bash
# Deploy slash commands to Discord
npm run deploy

# Start the bot
npm start

# Development mode with auto-restart
npm run dev
```

## 📋 **Commands**

### **🎯 `/pick`** - Main Betting Analysis
- **Channel Type**: VIP Play, Free Play, or Lotto Ticket
- **Image**: Bet slip screenshot
- **Notes**: Optional additional information
- **Debug**: Enable detailed analysis mode

### **⚙️ `/admin`** - Bot Management
- **ping**: Test bot responsiveness
- **status**: System health and stats
- **stats**: Usage statistics
- **restart**: Restart bot (owner only)

## 🏗️ **Architecture**

### **Core Services**
```
src/
├── commands/          # Discord slash commands
│   ├── pick.js       # Main betting analysis
│   └── admin.js      # Bot management
├── services/          # Business logic
│   ├── ocrService.js     # Image text extraction
│   ├── mlbService.js     # Baseball data
│   ├── aiService.js      # AI analysis
│   └── bettingService.js # Message formatting
├── utils/             # Utilities
│   ├── logger.js      # Logging
│   ├── rateLimiter.js # Request throttling
│   └── systemStats.js # System monitoring
└── index.js           # Main bot file
```

### **AI Pipeline**
1. **Image Upload** → OCR Processing
2. **Text Extraction** → Bet Slip Parsing
3. **Game Data Fetch** → MLB API Integration
4. **AI Analysis** → Multi-Model Processing
5. **Message Creation** → Discord Embed Generation

## 🤖 **AI Models**

### **OCR Engines**
- **Tesseract.js**: Primary OCR with image preprocessing
- **EasyOCR**: High-accuracy alternative (Python bridge)
- **PaddleOCR**: Fast, lightweight option (Python bridge)

### **Analysis Models**
- **GPT-4**: Primary analysis and insights
- **Claude 3.5**: Risk assessment and reasoning
- **Local Models**: Privacy-focused analysis (Llama, Mistral)

### **Performance Targets**
- **OCR Accuracy**: >95%
- **Response Time**: <5 seconds
- **AI Confidence**: >85% average
- **Memory Usage**: <2GB RAM

## 🔧 **Development**

### **Local Development**
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Lint code
npm run lint

# Format code
npm run format
```

### **Environment Variables**
```bash
# Required
DISCORD_TOKEN=your_bot_token
CLIENT_ID=your_client_id

# Optional AI Services
OPENAI_API_KEY=your_openai_key
HUGGINGFACE_API_KEY=your_hf_key

# Optional APIs
MLB_API_KEY=your_mlb_key
OPENWEATHER_API_KEY=your_weather_key

# Configuration
LOG_LEVEL=info
RATE_LIMIT_COOLDOWN=12000
NODE_ENV=development
```

### **Testing**
```bash
# Run all tests
npm test

# Run specific test
npm test -- --testNamePattern="OCR"

# Coverage report
npm run test:coverage
```

## 📊 **Monitoring**

### **Health Checks**
- **System Stats**: CPU, memory, uptime
- **Bot Status**: Command count, server count
- **Performance**: Response times, error rates
- **AI Models**: Success rates, confidence scores

### **Logging**
- **Console**: Colored, formatted logs
- **Files**: Error and combined logs
- **Levels**: Debug, info, warn, error
- **Structured**: JSON format with metadata

## 🚀 **Deployment**

### **Render (Recommended)**
```yaml
# render.yaml
services:
  - type: web
    name: gotlockz-bot
    env: node
    buildCommand: npm install
    startCommand: npm start
    envVars:
      - key: DISCORD_TOKEN
        sync: false
      - key: CLIENT_ID
        sync: false
      - key: OPENAI_API_KEY
        sync: false
```

### **Docker**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
CMD ["npm", "start"]
```

### **Environment Variables**
Set these in your deployment platform:
- `DISCORD_TOKEN`
- `CLIENT_ID`
- `OPENAI_API_KEY` (optional)
- `HUGGINGFACE_API_KEY` (optional)
- `NODE_ENV=production`

## 🔒 **Security**

### **Rate Limiting**
- **Per User**: 12-second cooldown between requests
- **Global**: Request throttling to prevent abuse
- **Automatic**: Cleanup of old rate limit entries

### **Error Handling**
- **Graceful Degradation**: Fallback when AI services fail
- **Input Validation**: Sanitize all user inputs
- **Secure Logging**: No sensitive data in logs

### **API Security**
- **Environment Variables**: Secure credential storage
- **Request Validation**: Validate all API responses
- **Timeout Protection**: Prevent hanging requests

## 📈 **Performance**

### **Optimizations**
- **Image Preprocessing**: Sharp-based optimization
- **Caching**: Redis-based data caching
- **Async Processing**: Non-blocking operations
- **Memory Management**: Efficient resource usage

### **Scaling**
- **Horizontal**: Multiple bot instances
- **Vertical**: Resource optimization
- **Caching**: Reduce API calls
- **Monitoring**: Performance tracking

## 🤝 **Contributing**

### **Development Setup**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### **Code Standards**
- **ESLint**: Code linting
- **Prettier**: Code formatting
- **Jest**: Unit testing
- **TypeScript**: Type safety (future)

## 📝 **License**

MIT License - see LICENSE file for details.

## 🆘 **Support**

### **Common Issues**
1. **Commands not working**: Run `npm run deploy`
2. **OCR failing**: Check image quality and format
3. **AI analysis slow**: Check API key and rate limits
4. **Bot not starting**: Verify environment variables

### **Getting Help**
- **Discord**: Join our support server
- **Issues**: GitHub issue tracker
- **Documentation**: This README and code comments

---

**🚀 Built with AI acceleration for maximum performance and accuracy!** 