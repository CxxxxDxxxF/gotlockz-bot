/**
 * /pick - Post a betting pick with image analysis and AI
 *
 * Options:
 *   - channel_type (string, required): Type of pick to post (Free Play, VIP Pick, Lotto Ticket)
 *   - image (attachment, required): Betting slip image
 *   - notes (string, optional): Additional notes
 */
import { SlashCommandBuilder, ChatInputCommandInteraction } from 'discord.js';
import { analyzeImage } from '../services/ocrService';
import { getGameData, convertGameStatsToGameData } from '../services/mlbService';
import { getForecast } from '../services/weatherService';
import { RateLimiter } from '../utils/rateLimiter';
import { Logger } from '../utils/logger';
import { 
  createVIPPlayMessage, 
  createFreePlayMessage, 
  createLottoTicketMessage,
  validateBettingMessage,
  formatBettingMessageForDiscord 
} from '../services/bettingMessageService';
import { parseBetSlip } from '../utils/parser';
import { generateAnalysis } from '../services/analysisService';

export const data = new SlashCommandBuilder()
  .setName('pick')
  .setDescription('Analyze a bet slip and provide structured betting analysis')
  .addStringOption((option: SlashCommandStringOption) =>
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
  .addAttachmentOption((option: SlashCommandAttachmentOption) =>
    option
      .setName('image')
      .setDescription('Bet slip image to analyze')
      .setRequired(true)
  )
  .addStringOption((option: SlashCommandStringOption) =>
    option
      .setName('notes')
      .setDescription('Additional notes (optional, mainly for lotto tickets)')
      .setRequired(false)
  )
  .addBooleanOption((option: SlashCommandBooleanOption) =>
    option
      .setName('debug')
      .setDescription('Enable debug mode for OCR analysis (saves debug images)')
      .setRequired(false)
  );

export async function execute(interaction: ChatInputCommandInteraction): Promise<void> {
  const logger = new Logger('pick-command');
  
  try {
    await interaction.deferReply();
    
    // Rate limiting check
    if (!RateLimiter.allow(interaction.user.id)) {
      const timeRemaining = RateLimiter.getTimeRemaining(interaction.user.id);
      await interaction.editReply(`⏰ Rate limit exceeded. Please wait ${Math.ceil(timeRemaining / 1000)} seconds before making another pick.`);
      return;
    }
    
    const channelType = interaction.options.getString('channel_type', true);
    const image = interaction.options.getAttachment('image');
    const notes = interaction.options.getString('notes');
    const debug = interaction.options.getBoolean('debug') ?? false;
    
    if (!image) {
      await interaction.editReply('❌ Please provide a bet slip image.');
      return;
    }
    
    logger.info('Processing pick command', { 
      channelType, 
      userId: interaction.user.id,
      debug 
    });
    
    // Extract text from image
    const imageBuffer = await fetch(image.url).then(res => res.arrayBuffer()).then(buf => Buffer.from(buf));
    const ocrLines = await analyzeImage(imageBuffer, debug);
    
    // Parse bet slip
    const betSlip = await parseBetSlip(ocrLines);
    if (!betSlip) {
      await interaction.editReply('❌ Could not parse bet slip. Please check the image quality.');
      return;
    }
    
    // Get game data
    const gameStats = await getGameData(betSlip.legs[0]?.gameId || '');
    if (!gameStats) {
      await interaction.editReply('❌ Could not fetch game data. Please try again.');
      return;
    }
    
    // Convert to GameData format
    const gameData = convertGameStatsToGameData(gameStats);
    
    // Get weather data
    const weather = await getForecast('New York'); // Fallback location for now
    const analysis = await generateAnalysis(betSlip, gameData, weather);
    
    // Create structured betting message based on channel type
    let bettingMessage;
    let content = '';
    
    switch (channelType) {
      case 'vip_plays':
        bettingMessage = await createVIPPlayMessage(betSlip, gameData, analysis, image.url);
        if (typeof bettingMessage === 'string') {
          await interaction.editReply(bettingMessage);
          return;
        }
        content = `🎯 **VIP Play #${bettingMessage.playNumber}** - GotLockz Family, let's get this bread! 💰`;
        break;
        
      case 'free_plays':
        bettingMessage = await createFreePlayMessage(betSlip, gameData, analysis, image.url);
        content = `🎁 **Free Play is Here!** - GotLockz Family, enjoy this one on us! 🎉`;
        break;
        
      case 'lotto_ticket':
        bettingMessage = await createLottoTicketMessage(betSlip, gameData, analysis, image.url, notes || undefined);
        content = `🎰 **Lotto Ticket Alert!** - GotLockz Family, let's hit the jackpot! 🚀`;
        break;
        
      default:
        await interaction.editReply('❌ Invalid channel type selected.');
        return;
    }
    
    // Validate the message
    if (!validateBettingMessage(bettingMessage)) {
      await interaction.editReply('❌ Failed to create valid betting message.');
      return;
    }
    
    // Format for Discord
    const embed = formatBettingMessageForDiscord(bettingMessage);
    
    await interaction.editReply({
      content,
      embeds: [embed]
    });
    
    logger.info('Pick command executed successfully', { 
      channelType, 
      userId: interaction.user.id 
    });
    
  } catch (error) {
    logger.error('Pick command failed', { 
      error, 
      userId: interaction.user.id 
    });
    await interaction.editReply(`❌ An error occurred: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
} 