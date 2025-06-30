# GotLockz Bot

A high-performance MLB Discord bot with advanced analytics, real-time updates, and AI-powered betting analysis supporting multiple message types.

[![Schema Validation](https://github.com/your-username/gotlockz-bot/workflows/Validate%20JSON%20Schemas/badge.svg)](https://github.com/your-username/gotlockz-bot/actions/workflows/validate-schemas.yml)

## 🚀 Quick Start

### Environment Variables

The bot requires the following environment variables:

- `DISCORD_BOT_TOKEN` - Your Discord bot token
- `DISCORD_CLIENT_ID` - Your Discord application client ID  
- `DISCORD_GUILD_ID` - Your Discord server ID (optional, for guild-specific commands)
- `OPENAI_API_KEY` - Your OpenAI API key for GPT analysis
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to Google Cloud service account key file (optional, for OCR fallback)

### Installation

1. Clone the repository
2. Install dependencies: `npm install`
3. Set up environment variables
4. Run the bot: `npm start`

## 🎯 Features

- **Advanced OCR**: Image preprocessing, Tesseract JSON parsing, word clustering, and Google Vision fallback
- **Multi-Message Types**: Support for VIP Plays, Free Plays, and Lotto Tickets
- **Image Analysis**: OCR-powered betting slip analysis with confidence scoring
- **GPT Integration**: AI-powered betting analysis and insights using OpenAI
- **Weather Context**: Weather data integration for enhanced analysis
- **Rate Limiting**: Built-in protection against spam (12-second cooldown)
- **Health Monitoring**: HTTP health endpoint for uptime checks
- **Caching**: Intelligent caching to reduce API costs
- **Schema Validation**: Structured message formats with JSON schema compliance

## 🔍 Advanced OCR Features

The bot now includes sophisticated OCR capabilities:

### Image Preprocessing
- **Grayscale conversion** for better text recognition
- **Contrast enhancement** to improve readability
- **Resize optimization** to ~1000px height for optimal processing
- **Noise reduction** with Gaussian blur
- **Binary thresholding** for clean text extraction

### Tesseract JSON Parsing
- **Word-level confidence filtering** (minimum 60% confidence)
- **Spatial clustering** by Y-coordinate proximity
- **Bounding box analysis** for accurate text positioning
- **Multi-line text reconstruction** from individual words

### Google Vision Fallback
- **Automatic fallback** when Tesseract confidence < 55%
- **High-accuracy text detection** for challenging images
- **Bounding polygon analysis** for precise text positioning
- **Seamless integration** with existing OCR pipeline

### Confidence Scoring
- **Average confidence calculation** across all detected words
- **Low-confidence cluster logging** for debugging
- **Automatic quality assessment** and fallback triggering
- **Detailed logging** of OCR performance metrics

## 📋 Commands

### `/pick`
Analyze a bet slip and provide structured betting analysis with support for multiple message types.

**Parameters:**
- `channel_type` (required): Type of betting play to post
  - `VIP Play` - Premium betting analysis with sequential numbering
  - `Free Play` - Complimentary betting picks for the community
  - `Lotto Ticket` - High-risk parlay bets with multiple legs
- `image` (required): Bet slip image attachment to analyze
- `notes` (optional): Additional notes, mainly for lotto tickets

#### Usage Examples

**VIP Play:**
```
/pick channel_type:VIP Play image:[bet-slip.png]
```
*Generates a structured VIP Play message with sequential numbering and unit size information.*

**Free Play:**
```
/pick channel_type:Free Play image:[bet-slip.png]
```
*Creates a free play message for community sharing without unit requirements.*

**Lotto Ticket:**
```
/pick channel_type:Lotto Ticket image:[parlay-slip.png] notes:High-risk 3-leg parlay!
```
*Generates a lotto ticket message with multiple games, legs, and calculated parlay odds.*

### `/admin`
Admin commands for bot management.

**Subcommands:**
- `ping`: Test bot responsiveness
- `status`: Check bot and system status

## 📊 Message Types & Schemas

The bot generates structured messages that conform to specific JSON schemas:

### 🎯 VIP Plays
- **Channel**: `vip_plays`
- **Features**: Sequential daily numbering, unit size tracking, premium analysis
- **Schema**: Includes `playNumber`, `unitSize`, and enhanced betting details
- **Color**: Green (#00ff00)

### 🎁 Free Plays  
- **Channel**: `free_plays`
- **Features**: Community-focused, no unit requirements, accessible analysis
- **Schema**: Simplified structure without unit size or numbering
- **Color**: Blue (#0099ff)

### 🎰 Lotto Tickets
- **Channel**: `lotto_ticket`
- **Features**: Multi-leg parlays, calculated odds, optional notes
- **Schema**: Supports multiple games, legs array, and parlay odds calculation
- **Color**: Orange (#ff6600)

### JSON Schema References

Each message type follows a specific JSON schema for validation and consistency:

- **[VIP Play Schema](schemas/vip-play.json)**: Structured format with sequential numbering and unit tracking
- **[Free Play Schema](schemas/free-play.json)**: Simplified format for community sharing  
- **[Lotto Ticket Schema](schemas/lotto-ticket.json)**: Complex format supporting multi-leg parlays

All schemas are validated on every push and pull request to ensure message format consistency.

## 🛠️ Development

### Scripts
- Build: `npm run build`
- Test: `npm test`
- Type check: `npm run type-check`
- Start: `npm start`
- Dev: `npm run dev`

### Testing
Comprehensive test coverage including:
- Environment variable validation
- Command registration and option parsing
- Service integration (OCR, MLB, Weather, Analysis)
- Message type validation and formatting
- Rate limiting and caching
- **Advanced OCR testing** with image preprocessing and word clustering

**Test Results:**
- 8/9 test suites passing (88.9%)
- 52/54 tests passing (96.3%)
- Full coverage of all message types
- **OCR preprocessing and clustering tests**

## 🏗️ Architecture

### Services
- **OCR Parser Service**: Advanced image preprocessing and Tesseract JSON parsing
- **OCR Service**: Image text extraction with Google Vision fallback
- **MLB Service**: Game statistics and real-time data
- **Weather Service**: Weather forecasts and conditions
- **Betting Message Service**: Unified service for all message types
- **Analysis Service**: GPT-powered betting insights with caching

### OCR Processing Pipeline
1. **Image Preprocessing** → Grayscale, contrast, resize, threshold
2. **Tesseract Analysis** → JSON word extraction with confidence scores
3. **Word Filtering** → Remove low-confidence words (< 60%)
4. **Spatial Clustering** → Group words by Y-coordinate proximity
5. **Confidence Assessment** → Calculate average confidence
6. **Fallback Decision** → Use Google Vision if confidence < 55%
7. **Text Reconstruction** → Build clean text lines from clusters

### Message Processing Pipeline
1. **Image Upload** → Advanced OCR text extraction
2. **Text Parsing** → Bet slip structure analysis
3. **Data Enrichment** → Game stats and weather context
4. **AI Analysis** → GPT-powered insights
5. **Message Creation** → Type-specific structured message
6. **Validation** → Schema compliance check
7. **Discord Formatting** → Embed generation and posting

### Rate Limiting & Caching
- Per-user rate limiting (12-second cooldown)
- 1-minute cache for analysis results
- Intelligent API cost management
- Type-safe message validation

## 🚀 Deployment

### Render Deployment
The bot is configured for automatic deployment on Render:

1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. Deploy automatically on pushes to `main`

### Google Cloud Vision Setup (Optional)
For enhanced OCR capabilities:

1. Create a Google Cloud project
2. Enable the Cloud Vision API
3. Create a service account and download the JSON key file
4. Set `GOOGLE_APPLICATION_CREDENTIALS` to the path of your key file
5. The bot will automatically use Google Vision as a fallback for low-confidence OCR results

### Health Endpoint
The bot exposes a health endpoint at `/health`:
```bash
curl https://your-service-url/health
# Returns: { "status": "ok", "uptime": 123.45 }
```

## 📊 Monitoring

### Startup Logs
Look for these messages in Render logs:
```
Bot is ready and analysis service is up!
Health endpoint listening on port 3000
Advanced OCR parser initialized
```

### Environment Verification
Ensure these environment variables are set in Render:
- `DISCORD_BOT_TOKEN`
- `DISCORD_CLIENT_ID` 
- `DISCORD_GUILD_ID`
- `OPENAI_API_KEY`
- `GOOGLE_APPLICATION_CREDENTIALS` (optional)

### OCR Performance Monitoring
- Average confidence scores logged for each image
- Low-confidence clusters flagged for review
- Google Vision fallback usage tracked
- Image preprocessing metrics recorded

### Message Type Monitoring
- VIP Play counter resets daily
- All message types validate against schemas
- Rate limiting prevents spam
- Caching reduces API costs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests: `npm test`
4. Ensure all message types work correctly
5. Test OCR functionality with various image qualities
6. Submit a pull request

## 📄 License

MIT License
# Test comment
