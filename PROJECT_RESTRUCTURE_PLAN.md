# 🚀 GotLockz Bot - Project Restructure Plan

## 📋 Executive Summary

This plan restructures the GotLockz Bot from a broken TypeScript implementation to a modern, production-ready Discord bot with clean architecture, proper dependency management, and comprehensive testing.

### 🎯 **Goals**
- ✅ Fix all build and dependency issues
- ✅ Modernize to latest Discord.js v14 standards
- ✅ Implement clean, maintainable architecture
- ✅ Add comprehensive testing and CI/CD
- ✅ Ensure production-ready deployment
- ✅ Preserve all advanced features (OCR, AI, MLB data)

---

## 🏗️ **New Project Structure**

```
gotlockz-bot/
├── src/
│   ├── commands/           # Discord slash commands
│   │   ├── pick.ts        # Main betting analysis command
│   │   ├── admin.ts       # Admin utilities
│   │   └── index.ts       # Command registry
│   ├── services/          # Core business logic
│   │   ├── ocr/           # OCR processing
│   │   │   ├── parser.ts  # Advanced OCR with preprocessing
│   │   │   ├── vision.ts  # Google Vision integration
│   │   │   └── types.ts   # OCR type definitions
│   │   ├── mlb/           # MLB data services
│   │   │   ├── api.ts     # MLB Stats API client
│   │   │   ├── scraper.ts # Fast data scraper
│   │   │   └── types.ts   # MLB type definitions
│   │   ├── weather/       # Weather services
│   │   │   ├── api.ts     # OpenWeatherMap client
│   │   │   └── impact.ts  # Weather impact analysis
│   │   ├── ai/            # AI analysis services
│   │   │   ├── openai.ts  # OpenAI GPT integration
│   │   │   └── cache.ts   # Analysis caching
│   │   └── betting/       # Betting message services
│   │       ├── messages.ts # Message creation
│   │       ├── schemas.ts  # JSON schema validation
│   │       └── embeds.ts   # Discord embed formatting
│   ├── utils/             # Utilities and helpers
│   │   ├── env.ts         # Environment management
│   │   ├── logger.ts      # Structured logging
│   │   ├── rateLimiter.ts # Rate limiting
│   │   └── validator.ts   # Input validation
│   ├── types/             # TypeScript definitions
│   │   ├── discord.ts     # Discord-specific types
│   │   ├── betting.ts     # Betting data types
│   │   └── api.ts         # API response types
│   ├── config/            # Configuration
│   │   ├── commands.ts    # Command definitions
│   │   ├── features.ts    # Feature flags
│   │   └── constants.ts   # App constants
│   └── index.ts           # Main application entry
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   ├── fixtures/          # Test data
│   └── setup.ts           # Test configuration
├── schemas/               # JSON schemas
│   ├── vip-play.json      # VIP play schema
│   ├── free-play.json     # Free play schema
│   └── lotto-ticket.json  # Lotto ticket schema
├── scripts/               # Build and deployment scripts
│   ├── build.ts           # Build script
│   ├── deploy.ts          # Deployment script
│   └── validate.ts        # Schema validation
├── docs/                  # Documentation
│   ├── api.md             # API documentation
│   ├── deployment.md      # Deployment guide
│   └── development.md     # Development guide
├── .github/               # GitHub workflows
│   └── workflows/
│       ├── ci.yml         # Continuous integration
│       ├── deploy.yml     # Deployment pipeline
│       └── security.yml   # Security scanning
├── package.json           # Dependencies and scripts
├── tsconfig.json          # TypeScript configuration
├── jest.config.js         # Jest test configuration
├── .eslintrc.js           # ESLint configuration
├── .prettierrc           # Prettier configuration
├── docker-compose.yml     # Docker development setup
├── Dockerfile             # Production Docker image
├── render.yaml            # Render deployment config
├── .env.example           # Environment variables template
└── README.md              # Project documentation
```

---

## 🔧 **Phase 1: Foundation & Dependencies**

### **1.1 Update Package Dependencies**
```json
{
  "dependencies": {
    "discord.js": "^14.14.1",
    "@discordjs/builders": "^1.11.2",
    "@discordjs/rest": "^2.2.0",
    "tesseract.js": "^5.0.3",
    "@google-cloud/vision": "^5.2.0",
    "openai": "^5.8.2",
    "axios": "^1.10.0",
    "express": "^5.1.0",
    "winston": "^3.11.0",
    "ajv": "^8.17.1",
    "ajv-formats": "^2.1.1",
    "node-cron": "^3.0.3"
  },
  "devDependencies": {
    "typescript": "^5.8.3",
    "@types/node": "^20.8.10",
    "@types/express": "^5.0.3",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.1",
    "@types/jest": "^29.5.8",
    "eslint": "^9.0.0",
    "@typescript-eslint/eslint-plugin": "^7.0.0",
    "@typescript-eslint/parser": "^7.0.0",
    "prettier": "^3.0.0",
    "rimraf": "^6.0.1"
  }
}
```

### **1.2 Fix TypeScript Configuration**
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "sourceMap": true,
    "moduleResolution": "node",
    "baseUrl": "./src",
    "paths": {
      "@/*": ["*"],
      "@/commands/*": ["commands/*"],
      "@/services/*": ["services/*"],
      "@/utils/*": ["utils/*"],
      "@/types/*": ["types/*"],
      "@/config/*": ["config/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests", "archive"]
}
```

### **1.3 Environment Configuration**
```typescript
// src/utils/env.ts
export interface Environment {
  DISCORD_BOT_TOKEN: string;
  DISCORD_CLIENT_ID: string;
  DISCORD_GUILD_ID?: string;
  OPENAI_API_KEY: string;
  OPENWEATHER_API_KEY?: string;
  GOOGLE_APPLICATION_CREDENTIALS?: string;
  NODE_ENV: 'development' | 'production' | 'test';
  LOG_LEVEL: 'debug' | 'info' | 'warn' | 'error';
  PORT?: number;
}

export function getEnv(): Environment {
  const env = {
    DISCORD_BOT_TOKEN: process.env.DISCORD_BOT_TOKEN,
    DISCORD_CLIENT_ID: process.env.DISCORD_CLIENT_ID,
    DISCORD_GUILD_ID: process.env.DISCORD_GUILD_ID,
    OPENAI_API_KEY: process.env.OPENAI_API_KEY,
    OPENWEATHER_API_KEY: process.env.OPENWEATHER_API_KEY,
    GOOGLE_APPLICATION_CREDENTIALS: process.env.GOOGLE_APPLICATION_CREDENTIALS,
    NODE_ENV: (process.env.NODE_ENV as Environment['NODE_ENV']) || 'development',
    LOG_LEVEL: (process.env.LOG_LEVEL as Environment['LOG_LEVEL']) || 'info',
    PORT: process.env.PORT ? parseInt(process.env.PORT) : undefined
  };

  // Validate required environment variables
  const required = ['DISCORD_BOT_TOKEN', 'DISCORD_CLIENT_ID', 'OPENAI_API_KEY'];
  for (const key of required) {
    if (!env[key as keyof Environment]) {
      throw new Error(`Missing required environment variable: ${key}`);
    }
  }

  return env as Environment;
}
```

---

## 🎯 **Phase 2: Core Services Architecture**

### **2.1 OCR Service Refactor**
```typescript
// src/services/ocr/parser.ts
export interface OCRResult {
  text: string;
  confidence: number;
  lines: OCRLine[];
  usedFallback: boolean;
}

export interface OCRLine {
  text: string;
  confidence: number;
  bbox: BoundingBox;
}

export class OCRParser {
  private tesseractWorker: Tesseract.Worker | null = null;
  private visionClient: ImageAnnotatorClient | null = null;

  async initialize(): Promise<void> {
    // Initialize Tesseract worker
    this.tesseractWorker = await createWorker('eng');
    
    // Initialize Google Vision if credentials available
    if (process.env.GOOGLE_APPLICATION_CREDENTIALS) {
      this.visionClient = new ImageAnnotatorClient();
    }
  }

  async parseImage(buffer: Buffer, debug = false): Promise<OCRResult> {
    // 1. Preprocess image
    const processedBuffer = await this.preprocessImage(buffer, debug);
    
    // 2. Try Tesseract first
    const tesseractResult = await this.parseWithTesseract(processedBuffer);
    
    // 3. Use Google Vision fallback if confidence is low
    if (tesseractResult.confidence < 55 && this.visionClient) {
      return await this.parseWithGoogleVision(buffer);
    }
    
    return tesseractResult;
  }

  private async preprocessImage(buffer: Buffer, debug: boolean): Promise<Buffer> {
    // Image preprocessing logic (grayscale, contrast, noise reduction)
  }

  private async parseWithTesseract(buffer: Buffer): Promise<OCRResult> {
    // Tesseract parsing logic
  }

  private async parseWithGoogleVision(buffer: Buffer): Promise<OCRResult> {
    // Google Vision parsing logic
  }
}
```

### **2.2 MLB Service Refactor**
```typescript
// src/services/mlb/api.ts
export interface MLBGameData {
  gameId: string;
  date: string;
  teams: [string, string];
  score?: string;
  status: 'scheduled' | 'live' | 'final';
  startTime?: string;
  venue?: string;
  weather?: WeatherData;
  stats?: TeamStats;
}

export class MLBService {
  private cache = new Map<string, { data: MLBGameData; timestamp: number }>();
  private readonly CACHE_TTL = 5 * 60 * 1000; // 5 minutes

  async getGameData(teamA: string, teamB: string): Promise<MLBGameData> {
    const cacheKey = `${teamA}_${teamB}`;
    const cached = this.cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
      return cached.data;
    }

    const data = await this.fetchGameData(teamA, teamB);
    this.cache.set(cacheKey, { data, timestamp: Date.now() });
    
    return data;
  }

  private async fetchGameData(teamA: string, teamB: string): Promise<MLBGameData> {
    // MLB API integration with error handling and fallbacks
  }
}
```

### **2.3 AI Analysis Service**
```typescript
// src/services/ai/openai.ts
export interface AnalysisRequest {
  betSlip: BetSlip;
  gameData: MLBGameData;
  weather?: WeatherData;
}

export interface AnalysisResponse {
  analysis: string;
  confidence: number;
  factors: string[];
}

export class AIService {
  private openai: OpenAI;
  private cache = new Map<string, { response: AnalysisResponse; timestamp: number }>();
  private readonly CACHE_TTL = 60 * 1000; // 1 minute

  constructor() {
    this.openai = new OpenAI({ apiKey: getEnv().OPENAI_API_KEY });
  }

  async generateAnalysis(request: AnalysisRequest): Promise<AnalysisResponse> {
    const cacheKey = this.generateCacheKey(request);
    const cached = this.cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
      return cached.response;
    }

    const response = await this.callOpenAI(request);
    this.cache.set(cacheKey, { response, timestamp: Date.now() });
    
    return response;
  }

  private async callOpenAI(request: AnalysisRequest): Promise<AnalysisResponse> {
    const prompt = this.buildPrompt(request);
    
    const completion = await this.openai.chat.completions.create({
      model: "gpt-4",
      messages: [{ role: "user", content: prompt }],
      max_tokens: 500,
      temperature: 0.7,
    });

    return {
      analysis: completion.choices[0]?.message?.content || "Analysis failed",
      confidence: 0.8,
      factors: ["AI-generated analysis"]
    };
  }
}
```

---

## 🎮 **Phase 3: Command System**

### **3.1 Command Registry**
```typescript
// src/commands/index.ts
import { Collection, SlashCommandBuilder } from 'discord.js';
import { pickCommand } from './pick';
import { adminCommand } from './admin';

export interface Command {
  data: SlashCommandBuilder;
  execute: (interaction: ChatInputCommandInteraction) => Promise<void>;
}

export const commands = new Collection<string, Command>();
commands.set('pick', pickCommand);
commands.set('admin', adminCommand);

export const commandData = Array.from(commands.values()).map(cmd => cmd.data.toJSON());
```

### **3.2 Pick Command Refactor**
```typescript
// src/commands/pick.ts
import { SlashCommandBuilder, ChatInputCommandInteraction } from 'discord.js';
import { OCRParser } from '@/services/ocr/parser';
import { MLBService } from '@/services/mlb/api';
import { AIService } from '@/services/ai/openai';
import { BettingMessageService } from '@/services/betting/messages';
import { RateLimiter } from '@/utils/rateLimiter';
import { Logger } from '@/utils/logger';

export const pickCommand: Command = {
  data: new SlashCommandBuilder()
    .setName('pick')
    .setDescription('Analyze a bet slip and provide structured betting analysis')
    .addStringOption(option =>
      option
        .setName('channel_type')
        .setDescription('Type of betting play to post')
        .setRequired(true)
        .addChoices(
          { name: 'VIP Play', value: 'vip_plays' },
          { name: 'Free Play', value: 'free_plays' },
          { name: 'Lotto Ticket', value: 'lotto_ticket' }
        )
    )
    .addAttachmentOption(option =>
      option
        .setName('image')
        .setDescription('Bet slip image to analyze')
        .setRequired(true)
    )
    .addStringOption(option =>
      option
        .setName('notes')
        .setDescription('Additional notes (optional)')
        .setRequired(false)
    ),

  execute: async (interaction: ChatInputCommandInteraction) => {
    const logger = new Logger('pick-command');
    
    try {
      await interaction.deferReply();
      
      // Rate limiting
      if (!RateLimiter.allow(interaction.user.id)) {
        return await interaction.editReply('⏰ Rate limit exceeded. Please wait before making another pick.');
      }
      
      // Extract options
      const channelType = interaction.options.getString('channel_type', true);
      const image = interaction.options.getAttachment('image');
      const notes = interaction.options.getString('notes');
      
      if (!image) {
        return await interaction.editReply('❌ Please provide a bet slip image.');
      }
      
      // Process image with OCR
      const ocrParser = new OCRParser();
      await ocrParser.initialize();
      
      const imageBuffer = await fetch(image.url).then(res => res.arrayBuffer()).then(buf => Buffer.from(buf));
      const ocrResult = await ocrParser.parseImage(imageBuffer);
      
      // Parse bet slip
      const betSlip = await parseBetSlip(ocrResult.lines.map(line => line.text));
      if (!betSlip) {
        return await interaction.editReply('❌ Could not parse bet slip. Please check the image quality.');
      }
      
      // Get game data
      const mlbService = new MLBService();
      const gameData = await mlbService.getGameData(betSlip.legs[0]?.teamA || '', betSlip.legs[0]?.teamB || '');
      
      // Generate AI analysis
      const aiService = new AIService();
      const analysis = await aiService.generateAnalysis({ betSlip, gameData });
      
      // Create betting message
      const bettingService = new BettingMessageService();
      const message = await bettingService.createMessage(channelType, betSlip, gameData, analysis, image.url, notes);
      
      // Send response
      await interaction.editReply(message);
      
      logger.info('Pick command executed successfully', { channelType, userId: interaction.user.id });
      
    } catch (error) {
      logger.error('Pick command failed', { error, userId: interaction.user.id });
      await interaction.editReply('❌ An error occurred while processing your request. Please try again.');
    }
  }
};
```

---

## 🧪 **Phase 4: Testing Infrastructure**

### **4.1 Jest Configuration**
```javascript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src', '<rootDir>/tests'],
  testMatch: ['**/__tests__/**/*.ts', '**/?(*.)+(spec|test).ts'],
  transform: {
    '^.+\\.ts$': 'ts-jest',
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/index.ts',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

### **4.2 Test Examples**
```typescript
// tests/unit/services/ocr/parser.test.ts
import { OCRParser } from '@/services/ocr/parser';

describe('OCRParser', () => {
  let parser: OCRParser;

  beforeEach(async () => {
    parser = new OCRParser();
    await parser.initialize();
  });

  afterEach(async () => {
    await parser.cleanup();
  });

  it('should parse image with high confidence', async () => {
    const testImage = fs.readFileSync('tests/fixtures/test-bet-slip.png');
    const result = await parser.parseImage(testImage);
    
    expect(result.confidence).toBeGreaterThan(60);
    expect(result.lines).toHaveLength.greaterThan(0);
    expect(result.text).toContain('MLB');
  });

  it('should use Google Vision fallback for low confidence', async () => {
    // Test fallback logic
  });
});
```

---

## 🚀 **Phase 5: Deployment & CI/CD**

### **5.1 Docker Configuration**
```dockerfile
# Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM node:18-alpine AS production

WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./

USER node
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

CMD ["node", "dist/index.js"]
```

### **5.2 GitHub Actions CI/CD**
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run linting
      run: npm run lint
    
    - name: Run type checking
      run: npm run type-check
    
    - name: Run tests
      run: npm test
    
    - name: Build application
      run: npm run build
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to Render
      run: |
        # Deploy logic here
```

---

## 📋 **Implementation Checklist**

### **Phase 1: Foundation (Week 1)**
- [ ] Update package.json with correct dependencies
- [ ] Fix TypeScript configuration
- [ ] Set up proper environment management
- [ ] Create basic project structure
- [ ] Set up ESLint and Prettier

### **Phase 2: Core Services (Week 2)**
- [ ] Refactor OCR service with proper error handling
- [ ] Update MLB service with caching
- [ ] Implement AI service with fallbacks
- [ ] Create betting message service
- [ ] Add comprehensive logging

### **Phase 3: Commands (Week 3)**
- [ ] Refactor command system
- [ ] Update pick command with new services
- [ ] Implement admin commands
- [ ] Add rate limiting
- [ ] Create command registry

### **Phase 4: Testing (Week 4)**
- [ ] Set up Jest configuration
- [ ] Write unit tests for all services
- [ ] Add integration tests
- [ ] Implement test coverage reporting
- [ ] Create test fixtures

### **Phase 5: Deployment (Week 5)**
- [ ] Create Docker configuration
- [ ] Set up GitHub Actions CI/CD
- [ ] Configure Render deployment
- [ ] Add health checks
- [ ] Create deployment documentation

---

## 🗑️ **Files to Remove/Archive**

### **Remove Completely**
- `archive/` - Old Python implementation
- `debug-ocr.js` - Debug script
- `mlb_model.py` - Python model
- `outdated.json` - Outdated data
- `pyrightconfig.json` - Python config
- `pytest.ini` - Python test config
- `requirements.txt` - Python dependencies

### **Archive for Reference**
- `ADVANCED_FEATURES_COMPLETE.md` - Move to docs/
- `INTEGRATION_COMPLETE.md` - Move to docs/
- `SCRAPER_IMPROVEMENTS.md` - Move to docs/
- `BOT_STRUCTURE.txt` - Move to docs/

### **Update and Keep**
- `README.md` - Update with new structure
- `CHANGELOG.md` - Continue with new version
- `package.json` - Update dependencies
- `tsconfig.json` - Fix configuration
- `render.yaml` - Update for new structure

---

## 🎯 **Success Metrics**

### **Technical Metrics**
- ✅ Zero TypeScript compilation errors
- ✅ 100% test coverage for core services
- ✅ < 5 second response time for pick command
- ✅ 99.9% uptime on Render
- ✅ Zero security vulnerabilities

### **Feature Metrics**
- ✅ All OCR features working (Tesseract + Google Vision)
- ✅ AI analysis generating insights
- ✅ MLB data integration functional
- ✅ Weather impact analysis working
- ✅ All message types (VIP, Free, Lotto) functional

### **Development Metrics**
- ✅ Automated CI/CD pipeline
- ✅ Comprehensive documentation
- ✅ Code quality tools (ESLint, Prettier)
- ✅ Performance monitoring
- ✅ Error tracking and logging

---

## 🚀 **Next Steps**

1. **Immediate Action**: Start with Phase 1 (Foundation)
2. **Parallel Work**: Begin service refactoring while fixing dependencies
3. **Testing**: Implement tests alongside development
4. **Deployment**: Set up CI/CD early for continuous validation
5. **Documentation**: Update docs as features are implemented

This restructure will transform the GotLockz Bot into a modern, maintainable, and production-ready Discord bot while preserving all its advanced features and capabilities. 