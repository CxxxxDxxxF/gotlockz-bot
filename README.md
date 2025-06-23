# 🏆 GotLockz Bot V2

**Modern Discord bot for betting pick management with OCR, live stats, and AI analysis.**

## 🚀 Features

### Core Functionality
- **OCR Image Processing** - Extract betting data from slip images
- **Live MLB Stats** - Real-time team and player statistics
- **AI Analysis** - Contextual insights using OpenAI GPT-4
- **Two-Phase Processing** - Immediate response + async enhancement
- **Cloud Deployment** - Render-ready with health monitoring

### Commands
- `/pick` - Post a betting pick with image analysis
- `/stats` - Get live team/player statistics
- `/status` - Bot health and system status
- `/help` - Command documentation

## 🏗️ Architecture

```
gotlockz-v2/
├── src/
│   ├── bot/
│   │   ├── main.py          # Bot entry point
│   │   ├── commands/        # Discord commands
│   │   ├── services/        # External integrations
│   │   └── utils/           # Utilities
│   ├── api/                 # Health check endpoints
│   └── config/              # Configuration
├── tests/                   # Test suite
├── docker/                  # Container files
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## 🛠️ Tech Stack

- **Language**: Python 3.11+
- **Framework**: Discord.py 2.3+
- **OCR**: Tesseract + OpenCV
- **APIs**: ESPN, MLB Stats, OpenAI
- **Deployment**: Render + Docker
- **Monitoring**: Health checks + logging

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone repository
git clone <your-repo>
cd gotlockz-v2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit with your tokens
DISCORD_TOKEN=your_discord_token
OPENAI_API_KEY=your_openai_key
```

### 3. Run Bot
```bash
python src/bot/main.py
```

## 📦 Docker Deployment

```bash
# Build and run
docker build -t gotlockz-v2 .
docker run --env-file .env gotlockz-v2

# Or with docker-compose
docker-compose up -d
```

## 🔧 Development

### Project Structure
- **Clean Architecture** - Separation of concerns
- **Type Hints** - Full type safety
- **Async/Await** - Non-blocking operations
- **Error Handling** - Graceful degradation
- **Testing** - Comprehensive test suite

### Key Principles
1. **Reliability First** - Never timeout or crash
2. **Performance** - Fast response times
3. **Maintainability** - Clean, documented code
4. **Scalability** - Cloud-ready architecture

## 📊 Performance Targets

- **Command Response**: < 3 seconds (Discord requirement)
- **OCR Processing**: < 2 seconds
- **API Calls**: < 1 second each
- **Uptime**: 99.9% availability

## 🎯 Roadmap

### Phase 1: Core Bot ✅
- [x] Basic Discord integration
- [x] OCR image processing
- [x] Live stats integration
- [x] AI analysis

### Phase 2: Enhancement 🚧
- [ ] Database integration
- [ ] Caching layer
- [ ] Advanced analytics
- [ ] Team dashboard

### Phase 3: Enterprise 🎯
- [ ] Multi-server support
- [ ] Advanced monitoring
- [ ] Performance optimization
- [ ] Security hardening

---

**Built with ❤️ for the GotLockz team**
