import { logger } from '../utils/logger.js';
import { getGameTime } from './espnService.js';

/**
 * Betting Service - Creates formatted pick messages
 * Format matches GotLockz style - ALL BOLD
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

      // Get game time from ESPN
      const leg = betSlip.legs?.[0] || {};
      let gameTime = null;
      
      if (leg.awayTeam && leg.homeTeam) {
        gameTime = await getGameTime(leg.awayTeam, leg.homeTeam);
      }

      let message;
      
      switch (channelType) {
        case 'vip_plays':
          this.vipPlayCount++;
          message = this.createVIPMessage(betSlip, gameData, analysis, imageUrl, units, gameTime);
          break;
        case 'free_plays':
          this.freePlayCount++;
          message = this.createFreePlayMessage(betSlip, gameData, analysis, imageUrl, gameTime);
          break;
        case 'lotto_ticket':
          this.lottoCount++;
          message = this.createLottoMessage(betSlip, gameData, analysis, imageUrl, gameTime);
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

  createVIPMessage(betSlip, gameData, analysis, imageUrl, units, gameTime) {
    const leg = betSlip.legs?.[0] || {};
    
    // Get date from ESPN or use today
    const dateStr = gameTime?.date || this.getTodayDate();
    const timeStr = gameTime?.time || '';
    
    // Build matchup with time
    const awayTeam = leg.awayTeam || 'Away Team';
    const homeTeam = leg.homeTeam || 'Home Team';
    const matchupWithTime = timeStr 
      ? `${awayTeam} @ ${homeTeam} (${dateStr} ${timeStr})`
      : `${awayTeam} @ ${homeTeam}`;
    
    // Build pick line: Team + Bet Type + (Odds) - odds only once, no duplicate
    let pickTeam = leg.pickLine || awayTeam;
    const betType = leg.betType || 'Money Line';
    const odds = leg.odds || 'N/A';
    
    // Remove odds from pickTeam if already included (avoid duplication)
    pickTeam = pickTeam.replace(/\s*[+-]\d{2,4}\s*$/, '').trim();
    
    const pickLineFormatted = `${pickTeam} ${betType} (${odds})`;
    
    const unitSize = units || '1';

    // Get analysis text
    const analysisText = this.formatAnalysisText(analysis, leg, gameData);

    // Build the message - wrap entire thing in ** for bold, emoji | text format
    let content = `**# 🔒| VIP PLAY # ${this.vipPlayCount} 🏆 - ${dateStr}\n\n`;
    content += `⚾ | Game: ${matchupWithTime}\n\n`;
    content += `🏆 | ${pickLineFormatted}\n\n`;
    content += `💵 | Unit Size: ${unitSize}\n\n`;
    content += `👇 | Analysis Below:\n\n`;
    content += `${analysisText}**`;

    return {
      content: content,
      files: imageUrl ? [{ attachment: imageUrl, name: 'betslip.png' }] : []
    };
  }

  createFreePlayMessage(betSlip, gameData, analysis, imageUrl, gameTime) {
    const leg = betSlip.legs?.[0] || {};
    
    const dateStr = gameTime?.date || this.getTodayDate();
    const timeStr = gameTime?.time || '';
    
    const awayTeam = leg.awayTeam || 'Away Team';
    const homeTeam = leg.homeTeam || 'Home Team';
    const matchupWithTime = timeStr 
      ? `${awayTeam} @ ${homeTeam} (${dateStr} ${timeStr})`
      : `${awayTeam} @ ${homeTeam}`;
    
    let pickTeam = leg.pickLine || awayTeam;
    const betType = leg.betType || 'Money Line';
    const odds = leg.odds || 'N/A';
    pickTeam = pickTeam.replace(/\s*[+-]\d{2,4}\s*$/, '').trim();
    const pickLineFormatted = `${pickTeam} ${betType} (${odds})`;

    const analysisText = this.formatAnalysisText(analysis, leg, gameData);

    // Build the message - wrap entire thing in ** for bold, emoji | text format
    let content = `**# 🎁| FREE PLAY 🎁 - ${dateStr}\n\n`;
    content += `⚾ | Game: ${matchupWithTime}\n\n`;
    content += `🎯 | ${pickLineFormatted}\n\n`;
    content += `👇 | Analysis Below:\n\n`;
    content += `${analysisText}**`;

    return {
      content: content,
      files: imageUrl ? [{ attachment: imageUrl, name: 'betslip.png' }] : []
    };
  }

  createLottoMessage(betSlip, gameData, analysis, imageUrl, gameTime) {
    const leg = betSlip.legs?.[0] || {};
    
    const dateStr = gameTime?.date || this.getTodayDate();
    const timeStr = gameTime?.time || '';
    
    const awayTeam = leg.awayTeam || 'Away Team';
    const homeTeam = leg.homeTeam || 'Home Team';
    const matchupWithTime = timeStr 
      ? `${awayTeam} @ ${homeTeam} (${dateStr} ${timeStr})`
      : `${awayTeam} @ ${homeTeam}`;
    
    let pickTeam = leg.pickLine || awayTeam;
    const betType = leg.betType || 'Money Line';
    const odds = leg.odds || 'N/A';
    pickTeam = pickTeam.replace(/\s*[+-]\d{2,4}\s*$/, '').trim();
    const pickLineFormatted = `${pickTeam} ${betType} (${odds})`;

    const analysisText = this.formatAnalysisText(analysis, leg, gameData);

    // Build the message - wrap entire thing in ** for bold, emoji | text format
    let content = `**# 🎰| LOTTO TICKET 🎰 - ${dateStr}\n\n`;
    content += `⚾ | Game: ${matchupWithTime}\n\n`;
    content += `🎲 | ${pickLineFormatted}\n\n`;
    content += `⚠️ | High Risk, High Reward!\n\n`;
    content += `👇 | Analysis Below:\n\n`;
    content += `${analysisText}**`;

    return {
      content: content,
      files: imageUrl ? [{ attachment: imageUrl, name: 'betslip.png' }] : []
    };
  }

  getTodayDate() {
    const today = new Date();
    return `${today.getMonth() + 1}/${today.getDate()}/${today.getFullYear().toString().slice(-2)}`;
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

    text += `Based on recent performance and matchup analysis, this presents a solid opportunity. `;
    text += `Always manage your bankroll responsibly and bet within your means.`;

    return text;
  }
}

export const bettingService = new BettingService();
export const createBettingMessage = (channelType, betSlip, gameData, analysis, imageUrl, units) => 
  bettingService.createBettingMessage(channelType, betSlip, gameData, analysis, imageUrl, units);
