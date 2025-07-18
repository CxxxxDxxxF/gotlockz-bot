import { EmbedBuilder } from 'discord.js';
import { logger } from '../utils/logger.js';

class BettingService {
  constructor () {
    this.templates = {
      vip_plays: this.createVIPTemplate(),
      free_plays: this.createFreePlayTemplate(),
      lotto_ticket: this.createLottoTemplate()
    };
  }

  async createBettingMessage (channelType, betSlip, gameData, analysis, imageUrl, notes) {
    try {
      logger.info('Creating betting message', { channelType });

      const template = this.templates[channelType];
      if (!template) {
        throw new Error(`Unknown channel type: ${channelType}`);
      }

      const embed = await template(betSlip, gameData, analysis, imageUrl, notes);

      return {
        success: true,
        data: { embeds: [embed] }
      };

    } catch (error) {
      logger.error('Failed to create betting message:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  createVIPTemplate () {
    return async (betSlip, gameData, analysis, imageUrl, notes) => {
      const embed = new EmbedBuilder()
        .setColor(0xFFD700) // Gold color for VIP
        .setTitle('💰 **VIP PLAY** 💰')
        .setDescription(this.generateVIPDescription(betSlip, analysis))
        .setThumbnail(imageUrl)
        .setTimestamp();

      // Add bet details
      embed.addFields(
        {
          name: '🎯 **BET DETAILS**',
          value: this.formatBetDetails(betSlip),
          inline: false
        },
        {
          name: '📊 **AI ANALYSIS**',
          value: this.formatAnalysis(analysis),
          inline: false
        }
      );

      // Add game info if available
      if (gameData) {
        embed.addFields({
          name: '🏟️ **GAME INFO**',
          value: this.formatGameInfo(gameData),
          inline: false
        });
      }

      // Add notes if provided
      if (notes) {
        embed.addFields({
          name: '📝 **NOTES**',
          value: notes,
          inline: false
        });
      }

      // Add footer with confidence
      embed.setFooter({
        text: `Confidence: ${Math.round(analysis.confidence * 100)}% | Risk: ${analysis.riskLevel.toUpperCase()} | AI-Powered Analysis`
      });

      return embed;
    };
  }

  createFreePlayTemplate () {
    return async (betSlip, gameData, analysis, imageUrl, notes) => {
      const embed = new EmbedBuilder()
        .setColor(0x00FF00) // Green color for free plays
        .setTitle('🎁 **FREE PLAY IS HERE!** 🎁')
        .setDescription(this.generateFreePlayDescription(betSlip, analysis))
        .setThumbnail(imageUrl)
        .setTimestamp();

      // Add bet details
      embed.addFields(
        {
          name: '🎯 **BET DETAILS**',
          value: this.formatBetDetails(betSlip),
          inline: false
        },
        {
          name: '🤖 **AI INSIGHTS**',
          value: this.formatAnalysis(analysis),
          inline: false
        }
      );

      // Add game info if available
      if (gameData) {
        embed.addFields({
          name: '🏟️ **GAME INFO**',
          value: this.formatGameInfo(gameData),
          inline: false
        });
      }

      // Add notes if provided
      if (notes) {
        embed.addFields({
          name: '📝 **NOTES**',
          value: notes,
          inline: false
        });
      }

      // Add footer
      embed.setFooter({
        text: `GotLockz Family | Confidence: ${Math.round(analysis.confidence * 100)}% | Risk: ${analysis.riskLevel.toUpperCase()}`
      });

      return embed;
    };
  }

  createLottoTemplate () {
    return async (betSlip, gameData, analysis, imageUrl, notes) => {
      const embed = new EmbedBuilder()
        .setColor(0xFF69B4) // Pink color for lotto tickets
        .setTitle('🎰 **LOTTO TICKET** 🎰')
        .setDescription(this.generateLottoDescription(betSlip, analysis))
        .setThumbnail(imageUrl)
        .setTimestamp();

      // Add bet details
      embed.addFields(
        {
          name: '🎯 **BET DETAILS**',
          value: this.formatBetDetails(betSlip),
          inline: false
        },
        {
          name: '🎲 **LOTTO ANALYSIS**',
          value: this.formatLottoAnalysis(analysis),
          inline: false
        }
      );

      // Add game info if available
      if (gameData) {
        embed.addFields({
          name: '🏟️ **GAME INFO**',
          value: this.formatGameInfo(gameData),
          inline: false
        });
      }

      // Add notes if provided
      if (notes) {
        embed.addFields({
          name: '📝 **NOTES**',
          value: notes,
          inline: false
        });
      }

      // Add footer
      embed.setFooter({
        text: `High Risk, High Reward | Confidence: ${Math.round(analysis.confidence * 100)}% | GotLockz Family`
      });

      return embed;
    };
  }

  generateVIPDescription (betSlip, analysis) {
    const confidence = Math.round(analysis.confidence * 100);
    const riskLevel = analysis.riskLevel.toUpperCase();

    return `**GotLockz Family** - Premium VIP analysis with ${confidence}% confidence level.\n\n` +
           `This ${riskLevel} risk play has been carefully analyzed by our AI system using multiple models.\n\n` +
           `**Key Factors:**\n${analysis.keyFactors.slice(0, 3).map(factor => `• ${factor}`).join('\n')}`;
  }

  generateFreePlayDescription (betSlip, analysis) {
    const confidence = Math.round(analysis.confidence * 100);

    return `**GotLockz Family** - Free play opportunity with ${confidence}% confidence!\n\n` +
           'Our AI analysis suggests this could be a solid play. Remember, this is for entertainment purposes.\n\n' +
           `**AI Insights:**\n${analysis.keyFactors.slice(0, 2).map(factor => `• ${factor}`).join('\n')}`;
  }

  generateLottoDescription (betSlip, analysis) {
    const confidence = Math.round(analysis.confidence * 100);

    return `**GotLockz Family** - High-risk lotto ticket with ${confidence}% confidence!\n\n` +
           'This is a long-shot play - high risk, high reward potential.\n\n' +
           `**Risk Factors:**\n${analysis.keyFactors.slice(0, 2).map(factor => `• ${factor}`).join('\n')}`;
  }

  formatBetDetails (betSlip) {
    let details = '';

    if (betSlip.legs && betSlip.legs.length > 0) {
      details += betSlip.legs.map((leg, i) =>
        `**Leg ${i + 1}:** ${leg.teamA} vs ${leg.teamB}\n` +
        `**Odds:** ${leg.odds || 'N/A'}\n`
      ).join('\n');
    }

    if (betSlip.stake) {
      details += `\n**Stake:** $${betSlip.stake}`;
    }

    if (betSlip.potentialWin) {
      details += `\n**Potential Win:** $${betSlip.potentialWin}`;
    }

    return details || 'Bet details not available';
  }

  formatAnalysis (analysis) {
    const confidence = Math.round(analysis.confidence * 100);
    const riskLevel = analysis.riskLevel.toUpperCase();

    let formatted = `**Confidence:** ${confidence}%\n`;
    formatted += `**Risk Level:** ${riskLevel}\n`;
    formatted += `**AI Models Used:** ${analysis.modelsUsed}\n\n`;

    if (analysis.recommendations && analysis.recommendations.length > 0) {
      formatted += `**Recommendation:** ${analysis.recommendations[0]}\n\n`;
    }

    if (analysis.keyFactors && analysis.keyFactors.length > 0) {
      formatted += `**Key Factors:**\n${analysis.keyFactors.slice(0, 3).map(factor => `• ${factor}`).join('\n')}`;
    }

    return formatted;
  }

  formatLottoAnalysis (analysis) {
    const confidence = Math.round(analysis.confidence * 100);

    let formatted = `**Confidence:** ${confidence}%\n`;
    formatted += '**Risk Level:** HIGH (Lotto Ticket)\n';
    formatted += `**AI Models Used:** ${analysis.modelsUsed}\n\n`;

    formatted += '**🎲 This is a high-risk, high-reward play!**\n';
    formatted += '**💰 Only bet what you can afford to lose!**\n\n';

    if (analysis.keyFactors && analysis.keyFactors.length > 0) {
      formatted += `**Risk Factors:**\n${analysis.keyFactors.slice(0, 2).map(factor => `• ${factor}`).join('\n')}`;
    }

    return formatted;
  }

  formatGameInfo (gameData) {
    if (!gameData) {return 'Game information not available';}

    let info = '';

    if (gameData.teams) {
      info += `**Teams:** ${gameData.teams.away?.name || 'N/A'} vs ${gameData.teams.home?.name || 'N/A'}\n`;
    }

    if (gameData.venue) {
      info += `**Venue:** ${gameData.venue}\n`;
    }

    if (gameData.weather) {
      info += `**Weather:** ${JSON.stringify(gameData.weather)}\n`;
    }

    if (gameData.status) {
      info += `**Status:** ${gameData.status}`;
    }

    return info || 'Game information not available';
  }
}

export const bettingService = new BettingService();
export const { createBettingMessage } = bettingService;
