import { EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } from 'discord.js';
import { logger } from '../utils/logger.js';
import { bettingDataFormatter } from '../formatters/betting-data-formatter.js';

class PostGenerator {
  constructor() {
    this.initialized = false;
  }

  async initialize() {
    if (this.initialized) return;
    this.initialized = true;
    logger.info('📝 Post generator initialized');
  }

  async generateBettingPost(jsonData) {
    try {
      await this.initialize();
      
      // Format the betting data
      const formattedData = await bettingDataFormatter.format(jsonData);
      
      // Create the main embed
      const embed = this.createBettingEmbed(formattedData);
      
      // Create action buttons
      const actionRow = this.createActionButtons(formattedData);
      
      return {
        embeds: [embed],
        components: [actionRow]
      };
      
    } catch (error) {
      logger.error('Error generating betting post:', error);
      throw error;
    }
  }

  createBettingEmbed(data) {
    const embed = new EmbedBuilder()
      .setColor(this.getTeamColor(data.awayTeam))
      .setTitle(`🔥 ${data.awayTeam} @ ${data.homeTeam}`)
      .setDescription(this.generateDescription(data))
      .addFields(
        { 
          name: '📊 **PICK**', 
          value: data.pick, 
          inline: true 
        },
        { 
          name: '💰 **ODDS**', 
          value: data.odds, 
          inline: true 
        },
        { 
          name: '📈 **CONFIDENCE**', 
          value: data.confidence, 
          inline: true 
        },
        { 
          name: '🏟️ **VENUE**', 
          value: data.venue, 
          inline: true 
        },
        { 
          name: '⏰ **TIME**', 
          value: data.gameTime, 
          inline: true 
        },
        { 
          name: '📺 **BROADCAST**', 
          value: data.broadcast, 
          inline: true 
        }
      )
      .setFooter({ 
        text: 'GotLockz Family | 21+ Only | Please bet responsibly' 
      })
      .setTimestamp();

    // Add team logos if available
    if (data.awayTeamLogo) {
      embed.setThumbnail(data.awayTeamLogo);
    }

    return embed;
  }

  generateDescription(data) {
    const descriptions = [
      `**GotLockz Family** - Here's your free play for today! 🎯`,
      `**Free play is here!** Let's get this money! 💰`,
      `**GotLockz Family** - Time to lock in this winner! 🔒`,
      `**Free play is here!** This one's looking solid! 💪`
    ];

    const randomDescription = descriptions[Math.floor(Math.random() * descriptions.length)];
    
    return `${randomDescription}\n\n${data.analysis}`;
  }

  createActionButtons(data) {
    const row = new ActionRowBuilder()
      .addComponents(
        new ButtonBuilder()
          .setCustomId(`bet_${data.gameId}`)
          .setLabel('💰 Place Bet')
          .setStyle(ButtonStyle.Primary)
          .setEmoji('🎯'),
        new ButtonBuilder()
          .setCustomId(`stats_${data.gameId}`)
          .setLabel('📊 Full Stats')
          .setStyle(ButtonStyle.Secondary)
          .setEmoji('📈'),
        new ButtonBuilder()
          .setCustomId(`weather_${data.gameId}`)
          .setLabel('🌤️ Weather')
          .setStyle(ButtonStyle.Secondary)
          .setEmoji('🌡️'),
        new ButtonBuilder()
          .setCustomId(`lineup_${data.gameId}`)
          .setLabel('👥 Lineups')
          .setStyle(ButtonStyle.Secondary)
          .setEmoji('⚾')
      );

    return row;
  }

  getTeamColor(teamName) {
    // Team color mapping for embeds
    const teamColors = {
      'Yankees': 0x003087,
      'Red Sox': 0xBD3039,
      'Dodgers': 0x005A9C,
      'Giants': 0xFD5A1E,
      'Cubs': 0x0E3386,
      'White Sox': 0x000000,
      'Mets': 0x002D72,
      'Phillies': 0xE81828,
      'Braves': 0xCE1141,
      'Marlins': 0x00A3E0,
      'Nationals': 0xAB0003,
      'Cardinals': 0xC41E3A,
      'Pirates': 0xFDB827,
      'Reds': 0xC6011F,
      'Brewers': 0x12284B,
      'Astros': 0x002D62,
      'Rangers': 0x003278,
      'Angels': 0xBA0021,
      'Athletics': 0x003831,
      'Mariners': 0x0C2C56,
      'Blue Jays': 0x134A8E,
      'Orioles': 0xDF4601,
      'Rays': 0x092C5C,
      'Tigers': 0x0C2340,
      'Indians': 0xE31937,
      'Royals': 0x004687,
      'Twins': 0x002B5C,
      'Rockies': 0x33006F,
      'Diamondbacks': 0xA71930,
      'Padres': 0x2F241D
    };

    return teamColors[teamName] || 0x0099FF;
  }

  async generateErrorPost(error) {
    const embed = new EmbedBuilder()
      .setColor(0xFF0000)
      .setTitle('❌ Error Processing Betting Data')
      .setDescription('Sorry, there was an issue processing the betting analysis. Please try again.')
      .addFields({
        name: '🔧 Technical Details',
        value: error.message || 'Unknown error occurred'
      })
      .setFooter({ 
        text: 'GotLockz Family | Contact support if this persists' 
      })
      .setTimestamp();

    return { embeds: [embed] };
  }

  async generateWelcomePost() {
    const embed = new EmbedBuilder()
      .setColor(0x00FF00)
      .setTitle('🎉 Welcome to GotLockz Family!')
      .setDescription(`
        **GotLockz Family** - Your premier destination for MLB betting analysis! 🏆
        
        🔥 **What we offer:**
        • Daily free plays and analysis
        • Advanced MLB statistics
        • Weather impact analysis
        • Real-time odds tracking
        
        💰 **Remember:** 21+ only, please bet responsibly!
        
        Use \`/help\` to see all available commands.
      `)
      .setFooter({ 
        text: 'GotLockz Family | Let\'s get this money! 💰' 
      })
      .setTimestamp();

    return { embeds: [embed] };
  }
}

export const postGenerator = new PostGenerator(); 