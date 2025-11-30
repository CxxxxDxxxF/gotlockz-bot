import { logger } from '../utils/logger.js';

/**
 * AI Service - Uses OpenAI for accurate betting analysis
 * Removed HuggingFace dependency - OpenAI only
 */
class AIService {
  constructor() {
    this.openai = null;
    this.initialized = false;
  }

  async initialize() {
    if (this.initialized) return;

    if (process.env.OPENAI_API_KEY) {
      try {
        const OpenAI = (await import('openai')).default;
        this.openai = new OpenAI({
          apiKey: process.env.OPENAI_API_KEY
        });
        this.initialized = true;
        logger.info('OpenAI service initialized successfully');
      } catch (error) {
        logger.error('Failed to initialize OpenAI:', error);
      }
    } else {
      logger.warn('No OPENAI_API_KEY found - using fallback analysis');
    }
  }

  async generateAnalysis(betSlip, gameData, debug = false) {
    const startTime = Date.now();

    try {
      await this.initialize();

      // If no OpenAI available, use fallback
      if (!this.openai) {
        logger.warn('OpenAI not available - using fallback analysis');
        return {
          success: true,
          data: this.generateFallbackAnalysis(betSlip, gameData),
          time: Date.now() - startTime
        };
      }

      logger.info('Starting AI analysis', {
        legs: betSlip.legs?.length || 0,
        debug
      });

      // Build comprehensive prompt with real data
      const prompt = this.buildAnalysisPrompt(betSlip, gameData);

      const response = await this.openai.chat.completions.create({
        model: 'gpt-4o-mini', // Cost-effective and fast
        messages: [
          {
            role: 'system',
            content: `You are an expert sports betting analyst. Analyze bets using ONLY the data provided - do NOT make up statistics or facts. 

Your analysis should include:
1. Quick assessment of the bet value
2. Key factors that could affect the outcome
3. Risk level (Low/Medium/High)
4. Confidence rating (1-10)

Keep responses concise (2-3 paragraphs max). Be direct and actionable.
If data is limited, acknowledge that and provide general insights based on what's available.`
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        max_tokens: 400,
        temperature: 0.3
      });

      const analysisText = response.choices[0].message.content;

      if (debug) {
        logger.info('OpenAI analysis:', { analysisText });
      }

      const analysis = this.parseAnalysis(analysisText);
      const time = Date.now() - startTime;

      logger.info('AI analysis completed', { time: `${time}ms` });

      return {
        success: true,
        data: analysis,
        time
      };

    } catch (error) {
      logger.error('AI analysis failed:', error);
      
      // Return fallback on error
      return {
        success: true,
        data: this.generateFallbackAnalysis(betSlip, gameData),
        time: Date.now() - startTime,
        error: error.message
      };
    }
  }

  buildAnalysisPrompt(betSlip, gameData) {
    let prompt = `## BET SLIP ANALYSIS REQUEST\n\n`;

    // Add bet legs
    prompt += `### BETS:\n`;
    if (betSlip.legs && betSlip.legs.length > 0) {
      betSlip.legs.forEach((leg, i) => {
        prompt += `${i + 1}. ${leg.teamA || 'Team A'} vs ${leg.teamB || 'Team B'}`;
        if (leg.odds) prompt += ` | Odds: ${leg.odds}`;
        if (leg.spread) prompt += ` | Spread: ${leg.spread}`;
        if (leg.type) prompt += ` | Type: ${leg.type}`;
        prompt += `\n`;
      });
    } else {
      prompt += `- Bet details from image\n`;
    }

    // Add stake info if available
    if (betSlip.stake) {
      prompt += `\nStake: $${betSlip.stake}`;
    }
    if (betSlip.potentialWin) {
      prompt += ` | Potential Win: $${betSlip.potentialWin}`;
    }
    prompt += `\n`;

    // Add game data if available
    if (gameData) {
      prompt += `\n### GAME DATA:\n`;
      
      if (gameData.teams) {
        prompt += `- Matchup: ${gameData.teams.away?.name || 'Away'} @ ${gameData.teams.home?.name || 'Home'}\n`;
      }
      if (gameData.venue) {
        prompt += `- Venue: ${gameData.venue}\n`;
      }
      if (gameData.status) {
        prompt += `- Status: ${gameData.status}\n`;
      }
      if (gameData.weather) {
        prompt += `- Weather: ${gameData.weather.temperature}°F, ${gameData.weather.condition}, Wind: ${gameData.weather.windSpeed}mph\n`;
      }
      if (gameData.teamStats) {
        prompt += `\n### TEAM STATS:\n`;
        prompt += JSON.stringify(gameData.teamStats, null, 2);
      }
    }

    prompt += `\n\nProvide a concise betting analysis based on this information.`;

    return prompt;
  }

  parseAnalysis(rawAnalysis) {
    return {
      summary: rawAnalysis,
      confidence: this.extractConfidence(rawAnalysis),
      riskLevel: this.extractRiskLevel(rawAnalysis),
      recommendation: this.extractRecommendation(rawAnalysis),
      timestamp: new Date().toISOString()
    };
  }

  extractConfidence(text) {
    // Look for confidence patterns like "7/10", "confidence: 8", etc.
    const patterns = [
      /confidence[:\s]*(\d+)/i,
      /(\d+)\s*\/\s*10/,
      /rating[:\s]*(\d+)/i
    ];
    
    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match) {
        const value = parseInt(match[1]);
        return value <= 10 ? value / 10 : value / 100;
      }
    }
    return 0.7; // Default
  }

  extractRiskLevel(text) {
    const lower = text.toLowerCase();
    if (lower.includes('high risk') || lower.includes('risky')) return 'high';
    if (lower.includes('low risk') || lower.includes('safe')) return 'low';
    return 'medium';
  }

  extractRecommendation(text) {
    const lower = text.toLowerCase();
    if (lower.includes('strong play') || lower.includes('recommend')) return 'Favorable';
    if (lower.includes('avoid') || lower.includes('pass')) return 'Caution';
    return 'Evaluate';
  }

  generateFallbackAnalysis(betSlip, gameData) {
    const legs = betSlip?.legs?.length || 1;
    const isParlay = legs > 1;

    return {
      summary: isParlay 
        ? `This is a ${legs}-leg parlay. Parlays carry higher risk but offer bigger payouts. Each leg must hit for the bet to win. Consider the correlation between legs and whether the odds justify the risk.`
        : `Single game bet detected. Review recent team performance, head-to-head history, and any injury news before placing. Consider line movement and public betting percentages if available.`,
      confidence: isParlay ? 0.5 : 0.65,
      riskLevel: isParlay ? 'high' : 'medium',
      recommendation: isParlay ? 'Higher Risk Play' : 'Standard Play',
      timestamp: new Date().toISOString(),
      note: 'Analysis generated without AI - add OPENAI_API_KEY for detailed insights'
    };
  }
}

export const aiService = new AIService();

// Export the method bound to the instance
export const generateAnalysis = (betSlip, gameData, debug) => 
  aiService.generateAnalysis(betSlip, gameData, debug);

export const generateFallbackAnalysis = (betSlip, gameData) => 
  aiService.generateFallbackAnalysis(betSlip, gameData);
