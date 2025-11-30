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
            content: `You are an elite sports betting analyst who CONVINCES readers why a bet is worth taking. Your job is to SELL the pick with real stats.

CRITICAL STAT INTERPRETATION:
- OFFENSE: Higher yards, points, completion % = GOOD
- DEFENSE yards allowed: LOWER = GOOD (means they don't give up yards)
- DEFENSE yards allowed: HIGHER = BAD (means they give up lots of yards = WEAKNESS to exploit)
- Interceptions/Sacks BY a defense = GOOD for that defense (they're creating turnovers)
- Rankings: #1 is best, #32 is worst

WRITING STYLE:
- Write like you're convincing a friend to tail your bet
- NO headers, titles, bullet points, or bold text
- Single line breaks between paragraphs
- Confident, persuasive tone

WHAT TO INCLUDE:
- Reference the actual STAT LEADERS by name (the stars on offense)
- Explain specific matchup advantages with rankings
- Point out defensive weaknesses to exploit (high yards allowed = bad defense)
- Explain WHY the odds offer value
- Talk about home/away record if relevant
- End with a confident closing statement

DO NOT:
- Confuse what's good vs bad for defense (giving up yards = BAD, getting INTs = GOOD)
- Mention random players - only reference the stat leaders provided
- Make up any stats not in the data
- Be uncertain - you believe in this pick

Write 2-3 punchy paragraphs that make readers want to bet this immediately.`
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
    let prompt = `BETTING PICK TO ANALYZE:\n\n`;

    const leg = betSlip.legs?.[0] || {};
    const pickTeam = leg.pickLine?.replace(/\s*[+-]\d+\.?\d*\s*$/, '').trim() || leg.homeTeam || 'Unknown';
    
    prompt += `We are betting on: ${pickTeam} ${leg.betType || 'Money Line'} (${leg.odds || 'N/A'})\n`;
    prompt += `Game: ${leg.awayTeam || 'Away'} @ ${leg.homeTeam || 'Home'}\n\n`;

    if (gameData && gameData.sportType === 'nfl') {
      prompt += `=== NFL STATS TO USE IN YOUR ANALYSIS ===\n\n`;
      
      // Team we're betting on
      const bettingOn = pickTeam.toLowerCase().includes(gameData.homeTeam?.name?.toLowerCase()?.split(' ').pop()) 
        ? gameData.homeTeam 
        : gameData.awayTeam;
      const opponent = bettingOn === gameData.homeTeam ? gameData.awayTeam : gameData.homeTeam;
      
      if (bettingOn) {
        prompt += `OUR PICK - ${bettingOn.name || pickTeam}:\n`;
        prompt += `Record: ${bettingOn.record || 'N/A'}`;
        if (bettingOn.homeRecord) prompt += ` | Home: ${bettingOn.homeRecord}`;
        if (bettingOn.awayRecord) prompt += ` | Away: ${bettingOn.awayRecord}`;
        prompt += `\n`;
        if (bettingOn.standings) prompt += `Standings: ${bettingOn.standings}\n`;
        
        // Stat Leaders - the actual stars of this team
        if (bettingOn.statLeaders?.length > 0) {
          prompt += `OFFENSIVE STARS (stat leaders):\n`;
          for (const leader of bettingOn.statLeaders) {
            prompt += `- ${leader.category}: ${leader.name} (${leader.position}) - ${leader.stat}\n`;
          }
        }
        
        if (bettingOn.offense && Object.keys(bettingOn.offense).length > 0) {
          prompt += `OFFENSIVE STATS (higher = better):\n`;
          for (const [stat, data] of Object.entries(bettingOn.offense).slice(0, 6)) {
            prompt += `- ${stat}: ${data.value}${data.rank ? ` (Rank #${data.rank} in NFL)` : ''}\n`;
          }
        }
        if (bettingOn.defense && Object.keys(bettingOn.defense).length > 0) {
          prompt += `DEFENSIVE STATS (for yards allowed, LOWER = better; for turnovers/sacks, HIGHER = better):\n`;
          for (const [stat, data] of Object.entries(bettingOn.defense).slice(0, 6)) {
            prompt += `- ${stat}: ${data.value}${data.rank ? ` (Rank #${data.rank})` : ''}\n`;
          }
        }
        prompt += `\n`;
      }

      if (opponent) {
        prompt += `OPPONENT - ${opponent.name}:\n`;
        prompt += `Record: ${opponent.record || 'N/A'}\n`;
        
        if (opponent.offense && Object.keys(opponent.offense).length > 0) {
          prompt += `THEIR OFFENSE (we need to stop this):\n`;
          for (const [stat, data] of Object.entries(opponent.offense).slice(0, 5)) {
            prompt += `- ${stat}: ${data.value}${data.rank ? ` (Rank #${data.rank})` : ''}\n`;
          }
        }
        if (opponent.defense && Object.keys(opponent.defense).length > 0) {
          prompt += `THEIR DEFENSE (weaknesses our offense can exploit - high yards allowed = weak, low sacks/INTs = weak):\n`;
          for (const [stat, data] of Object.entries(opponent.defense).slice(0, 5)) {
            prompt += `- ${stat}: ${data.value}${data.rank ? ` (Rank #${data.rank})` : ''}\n`;
          }
        }
        prompt += `\n`;
      }

      // Key matchups
      if (gameData.keyMatchups?.length > 0) {
        prompt += `KEY MATCHUPS:\n`;
        gameData.keyMatchups.forEach(m => prompt += `- ${m}\n`);
        prompt += `\n`;
      }

      // Game info
      if (gameData.gameInfo) {
        prompt += `GAME INFO:\n`;
        if (gameData.gameInfo.venue) prompt += `Venue: ${gameData.gameInfo.venue}\n`;
        if (gameData.gameInfo.odds?.details) prompt += `Vegas Line: ${gameData.gameInfo.odds.details}\n`;
        prompt += `\n`;
      }

    } else if (gameData) {
      // MLB or other sport
      prompt += `=== GAME DATA ===\n`;
      if (gameData.awayTeam) prompt += `Away: ${gameData.awayTeam.name} (${gameData.awayTeam.record || 'N/A'})\n`;
      if (gameData.homeTeam) prompt += `Home: ${gameData.homeTeam.name} (${gameData.homeTeam.record || 'N/A'})\n`;
      if (gameData.venue) prompt += `Venue: ${gameData.venue}\n`;
    } else {
      prompt += `Limited data available - provide analysis based on general team knowledge and the odds.\n`;
    }

    prompt += `\n=== YOUR TASK ===
Write a CONVINCING analysis (2-3 paragraphs) explaining WHY this bet is worth taking.
Focus on specific matchup advantages, exploit defensive weaknesses, and reference the stats above.
Be confident - you're selling this pick to readers. End strong.`;

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
