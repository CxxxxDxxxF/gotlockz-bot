import { logger } from '../utils/logger.js';

/**
 * Betting Service - Creates formatted pick messages
 * Format matches GotLockz style
 */
class BettingService {
  constructor() {
    this.vipPlayCount = 0;
    this.freePlayCount = 0;
    this.lottoCount = 0;
  }

  async createBettingMessage(channelType, betSlip, gameData, analysis, imageUrl, units) {
    try {
      logger.info('Creating betting message', { channelType });

      let message;
      
      switch (channelType) {
        case 'vip_plays':
          this.vipPlayCount++;
          message = this.createVIPMessage(betSlip, gameData, analysis, imageUrl, units);
          break;
        case 'free_plays':
          this.freePlayCount++;
          message = this.createFreePlayMessage(betSlip, gameData, analysis, imageUrl);
          break;
        case 'lotto_ticket':
          this.lottoCount++;
          message = this.createLottoMessage(betSlip, gameData, analysis, imageUrl);
          break;
        default:
          throw new Error(`Unknown channel type: ${channelType}`);
      }

      return {
        success: true,
        data: message
      };

    } catch (error) {
      logger.error('Failed to create betting message:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  createVIPMessage(betSlip, gameData, analysis, imageUrl, units) {
    const today = new Date();
    const dateStr = `${today.getMonth() + 1}/${today.getDate()}/${today.getFullYear().toString().slice(-2)}`;
    
    const leg = betSlip.legs?.[0] || {};
    const matchup = leg.matchup || 'Game TBD';
    const fullPick = leg.fullPick || leg.pickLine || 'Pick TBD';
    const unitSize = units || '1';

    // Get analysis text
    const analysisText = this.formatAnalysisText(analysis, leg, gameData);

    // Build the message in the exact format
    let content = `🔒 **VIP PLAY # ${this.vipPlayCount}** 🏆 - ${dateStr}\n\n`;
    content += `⚾ **Game:** ${matchup}\n\n`;
    content += `🏆 **${fullPick}**\n\n`;
    content += `💵 **Unit Size:** ${unitSize}\n\n`;
    content += `👇 **Analysis Below:**\n\n`;
    content += analysisText;

    return {
      content: content,
      files: imageUrl ? [{ attachment: imageUrl, name: 'betslip.png' }] : []
    };
  }

  createFreePlayMessage(betSlip, gameData, analysis, imageUrl) {
    const today = new Date();
    const dateStr = `${today.getMonth() + 1}/${today.getDate()}/${today.getFullYear().toString().slice(-2)}`;
    
    const leg = betSlip.legs?.[0] || {};
    const matchup = leg.matchup || 'Game TBD';
    const fullPick = leg.fullPick || leg.pickLine || 'Pick TBD';

    const analysisText = this.formatAnalysisText(analysis, leg, gameData);

    let content = `🎁 **FREE PLAY** 🎁 - ${dateStr}\n\n`;
    content += `⚾ **Game:** ${matchup}\n\n`;
    content += `🎯 **${fullPick}**\n\n`;
    content += `👇 **Analysis Below:**\n\n`;
    content += analysisText;

    return {
      content: content,
      files: imageUrl ? [{ attachment: imageUrl, name: 'betslip.png' }] : []
    };
  }

  createLottoMessage(betSlip, gameData, analysis, imageUrl) {
    const today = new Date();
    const dateStr = `${today.getMonth() + 1}/${today.getDate()}/${today.getFullYear().toString().slice(-2)}`;
    
    const leg = betSlip.legs?.[0] || {};
    const matchup = leg.matchup || 'Game TBD';
    const fullPick = leg.fullPick || leg.pickLine || 'Pick TBD';

    const analysisText = this.formatAnalysisText(analysis, leg, gameData);

    let content = `🎰 **LOTTO TICKET** 🎰 - ${dateStr}\n\n`;
    content += `⚾ **Game:** ${matchup}\n\n`;
    content += `🎲 **${fullPick}**\n\n`;
    content += `⚠️ **High Risk, High Reward!**\n\n`;
    content += `👇 **Analysis Below:**\n\n`;
    content += analysisText;

    return {
      content: content,
      files: imageUrl ? [{ attachment: imageUrl, name: 'betslip.png' }] : []
    };
  }

  formatAnalysisText(analysis, leg, gameData) {
    // Check if we have a real AI analysis (summary field from OpenAI)
    if (analysis?.summary && typeof analysis.summary === 'string' && analysis.summary.length > 50) {
      return analysis.summary;
    }

    // Fallback analysis text
    const awayTeam = leg.awayTeam || 'the away team';
    const homeTeam = leg.homeTeam || 'the home team';
    
    let text = `This play focuses on ${homeTeam} at home against ${awayTeam}. `;
    
    if (gameData?.venue) {
      text += `The game is being played at ${gameData.venue}. `;
    }

    if (gameData?.weather) {
      text += `Weather conditions: ${gameData.weather.temperature}°F, ${gameData.weather.condition}. `;
    }

    text += `Based on recent performance and matchup analysis, this presents a solid opportunity. `;
    text += `Always manage your bankroll responsibly and bet within your means.`;

    return text;
  }
}

export const bettingService = new BettingService();
export const createBettingMessage = (channelType, betSlip, gameData, analysis, imageUrl, units) => 
  bettingService.createBettingMessage(channelType, betSlip, gameData, analysis, imageUrl, units);
