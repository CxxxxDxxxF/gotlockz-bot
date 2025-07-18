import OpenAI from 'openai';
import { HfInference } from '@huggingface/inference';
import { logger } from '../utils/logger.js';

class AIService {
  constructor () {
    this.openai = null;
    this.hf = null;

    this.models = {
      gpt4: 'gpt-4',
      gpt35: 'gpt-3.5-turbo',
      claude: 'claude-3-sonnet-20240229',
      local: 'microsoft/DialoGPT-medium' // Placeholder for local model
    };
  }

  initialize () {
    if (!this.openai && process.env.OPENAI_API_KEY) {
      this.openai = new OpenAI({
        apiKey: process.env.OPENAI_API_KEY
      });
    }

    if (!this.hf && process.env.HUGGINGFACE_API_KEY) {
      this.hf = new HfInference(process.env.HUGGINGFACE_API_KEY);
    }
  }

  async generateAnalysis (betSlip, gameData, debug = false) {
    const startTime = Date.now();

    try {
      // Initialize AI clients
      this.initialize();

      // Check if we have any AI services available
      if (!this.openai && !this.hf) {
        logger.warn('No AI services available - using fallback analysis');
        return this.generateFallbackAnalysis(betSlip, gameData);
      }

      logger.info('Starting AI analysis', {
        legs: betSlip.legs.length,
        debug
      });

      // Prepare context for AI
      const context = this.prepareContext(betSlip, gameData);

      // Generate analysis using available AI models
      const analysisPromises = [];

      if (this.openai) {
        analysisPromises.push(this.analyzeWithGPT4(context, debug));
        analysisPromises.push(this.analyzeWithClaude(context, debug));
      }

      if (this.hf) {
        analysisPromises.push(this.analyzeWithLocalModel(context, debug));
      }

      // Always include fallback analysis
      analysisPromises.push(this.analyzeWithLocalModel(context, debug));

      const analyses = await Promise.allSettled(analysisPromises);

      // Combine and synthesize results
      const combinedAnalysis = this.combineAnalyses(analyses, debug);

      const time = Date.now() - startTime;

      logger.info('AI analysis completed', {
        time: `${time}ms`,
        modelsUsed: analyses.filter(r => r.status === 'fulfilled').length
      });

      return {
        success: true,
        data: combinedAnalysis,
        time: time,
        models: analyses.map((r, i) => ({
          model: Object.keys(this.models)[i],
          status: r.status,
          error: r.status === 'rejected' ? r.reason.message : null
        }))
      };

    } catch (error) {
      logger.error('AI analysis failed:', error);
      return {
        success: false,
        error: error.message,
        time: Date.now() - startTime
      };
    }
  }

  prepareContext (betSlip, gameData) {
    const context = {
      betSlip: {
        legs: betSlip.legs.map(leg => ({
          teams: `${leg.teamA} vs ${leg.teamB}`,
          odds: leg.odds,
          type: this.inferBetType(leg)
        })),
        stake: betSlip.stake,
        totalOdds: betSlip.totalOdds,
        potentialWin: betSlip.potentialWin
      },
      gameData: {
        teams: gameData?.teams,
        venue: gameData?.venue,
        weather: gameData?.weather,
        stats: gameData?.teamA?.stats || gameData?.teamB?.stats
      },
      analysis: {
        timestamp: new Date().toISOString(),
        confidence: 0.85 // Placeholder
      }
    };

    return context;
  }

  inferBetType (leg) {
    // Simple bet type inference
    if (leg.odds > 0) {return 'underdog';}
    if (leg.odds < 0) {return 'favorite';}
    return 'pickem';
  }

  async analyzeWithGPT4 (context, debug = false) {
    try {
      const prompt = this.buildAnalysisPrompt(context);

      const response = await this.openai.chat.completions.create({
        model: this.models.gpt4,
        messages: [
          {
            role: 'system',
            content: `You are an expert MLB betting analyst with 20+ years of experience. 
            Analyze the provided bet slip and game data to provide insights on:
            1. Bet value and risk assessment
            2. Key factors affecting the outcome
            3. Historical context and trends
            4. Weather and venue impact
            5. Recommended confidence level (1-10)
            
            Be concise, professional, and focus on actionable insights.`
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        max_tokens: 500,
        temperature: 0.3
      });

      const analysis = response.choices[0].message.content;

      if (debug) {
        logger.info('GPT-4 analysis:', { analysis });
      }

      return this.parseAnalysis(analysis, 'gpt4');

    } catch (error) {
      logger.error('GPT-4 analysis failed:', error);
      throw error;
    }
  }

  async analyzeWithClaude (context, debug = false) {
    try {
      const prompt = this.buildAnalysisPrompt(context);

      const response = await this.openai.chat.completions.create({
        model: this.models.claude,
        messages: [
          {
            role: 'system',
            content: `You are a professional sports betting analyst specializing in MLB. 
            Provide a comprehensive analysis including:
            - Risk assessment and value analysis
            - Statistical insights and trends
            - External factors (weather, venue, injuries)
            - Confidence rating and reasoning
            
            Format your response in a structured, easy-to-read manner.`
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        max_tokens: 400,
        temperature: 0.2
      });

      const analysis = response.choices[0].message.content;

      if (debug) {
        logger.info('Claude analysis:', { analysis });
      }

      return this.parseAnalysis(analysis, 'claude');

    } catch (error) {
      logger.error('Claude analysis failed:', error);
      throw error;
    }
  }

  analyzeWithLocalModel (context, debug = false) {
    try {
      // Placeholder for local model analysis
      // In production, you'd use a local LLM like Llama or Mistral

      const analysis = {
        confidence: 0.75,
        riskLevel: 'medium',
        keyFactors: [
          'Team form and recent performance',
          'Head-to-head history',
          'Weather conditions',
          'Venue factors'
        ],
        recommendation: 'Proceed with caution',
        reasoning: 'Based on recent form and historical data'
      };

      if (debug) {
        logger.info('Local model analysis:', { analysis });
      }

      return analysis;

    } catch (error) {
      logger.error('Local model analysis failed:', error);
      throw error;
    }
  }

  buildAnalysisPrompt (context) {
    return `
Bet Slip Analysis Request:

BET DETAILS:
${context.betSlip.legs.map((leg, i) => `
Leg ${i + 1}: ${leg.teams}
Odds: ${leg.odds}
Type: ${leg.type}
`).join('')}

Stake: $${context.betSlip.stake || 'N/A'}
Total Odds: ${context.betSlip.totalOdds || 'N/A'}

GAME DATA:
Teams: ${context.gameData.teams?.away?.name || 'N/A'} vs ${context.gameData.teams?.home?.name || 'N/A'}
Venue: ${context.gameData.venue || 'N/A'}
Weather: ${JSON.stringify(context.gameData.weather) || 'N/A'}

Please provide a comprehensive analysis including risk assessment, key factors, and confidence level.
    `.trim();
  }

  parseAnalysis (rawAnalysis, model) {
    // Simple parsing - in production, you'd use more sophisticated parsing
    return {
      model,
      confidence: this.extractConfidence(rawAnalysis),
      riskLevel: this.extractRiskLevel(rawAnalysis),
      keyFactors: this.extractKeyFactors(rawAnalysis),
      recommendation: this.extractRecommendation(rawAnalysis),
      reasoning: rawAnalysis.substring(0, 200) + '...',
      timestamp: new Date().toISOString()
    };
  }

  extractConfidence (text) {
    const confidenceMatch = text.match(/confidence[:\s]*(\d+)/i);
    return confidenceMatch ? parseInt(confidenceMatch[1]) / 10 : 0.7;
  }

  extractRiskLevel (text) {
    if (text.toLowerCase().includes('high risk')) {return 'high';}
    if (text.toLowerCase().includes('low risk')) {return 'low';}
    return 'medium';
  }

  extractKeyFactors (text) {
    const factors = [];
    const lines = text.split('\n');

    for (const line of lines) {
      if (line.includes('factor') || line.includes('consider') || line.includes('impact')) {
        factors.push(line.trim());
      }
    }

    return factors.slice(0, 3); // Return top 3 factors
  }

  extractRecommendation (text) {
    if (text.toLowerCase().includes('recommend') || text.toLowerCase().includes('suggest')) {
      const lines = text.split('\n');
      for (const line of lines) {
        if (line.toLowerCase().includes('recommend') || line.toLowerCase().includes('suggest')) {
          return line.trim();
        }
      }
    }
    return 'Analysis complete';
  }

  combineAnalyses (analyses, debug = false) {
    const successfulAnalyses = analyses
      .filter(r => r.status === 'fulfilled')
      .map(r => r.value);

    if (successfulAnalyses.length === 0) {
      throw new Error('All AI models failed');
    }

    // Combine confidence scores
    const avgConfidence = successfulAnalyses.reduce((sum, a) => sum + a.confidence, 0) / successfulAnalyses.length;

    // Combine key factors
    const allFactors = successfulAnalyses.flatMap(a => a.keyFactors || []);
    const uniqueFactors = [...new Set(allFactors)];

    // Determine overall risk level
    const riskLevels = successfulAnalyses.map(a => a.riskLevel);
    const overallRisk = this.calculateOverallRisk(riskLevels);

    const combined = {
      confidence: avgConfidence,
      riskLevel: overallRisk,
      keyFactors: uniqueFactors.slice(0, 5),
      recommendations: successfulAnalyses.map(a => a.recommendation),
      reasoning: successfulAnalyses.map(a => a.reasoning).join(' '),
      modelsUsed: successfulAnalyses.length,
      timestamp: new Date().toISOString()
    };

    if (debug) {
      logger.info('Combined analysis:', { combined });
    }

    return combined;
  }

  calculateOverallRisk (riskLevels) {
    const riskScores = { low: 1, medium: 2, high: 3 };
    const avgScore = riskLevels.reduce((sum, risk) => sum + riskScores[risk], 0) / riskLevels.length;

    if (avgScore <= 1.5) {return 'low';}
    if (avgScore <= 2.5) {return 'medium';}
    return 'high';
  }

  generateFallbackAnalysis (_betSlip, _gameData) {
    // Simple fallback analysis when AI services are not available
    const analysis = {
      confidence: 0.65,
      riskLevel: 'medium',
      keyFactors: [
        'Team performance analysis',
        'Historical matchup data',
        'Current form and statistics'
      ],
      recommendation: 'Consider this play with moderate confidence',
      reasoning: 'Based on available data and statistical analysis',
      modelsUsed: 1,
      timestamp: new Date().toISOString()
    };

    return {
      success: true,
      data: analysis,
      time: 0,
      models: [{ model: 'fallback', status: 'fulfilled', error: null }]
    };
  }
}

export const aiService = new AIService();
export const { generateAnalysis } = aiService;
