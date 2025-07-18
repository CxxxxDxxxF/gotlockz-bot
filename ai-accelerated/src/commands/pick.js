import { SlashCommandBuilder } from 'discord.js';
import { analyzeImage } from '../services/ocrService.js';
import { getGameData } from '../services/mlbService.js';
import { generateAnalysis } from '../services/aiService.js';
import { createBettingMessage } from '../services/bettingService.js';
import { rateLimiter } from '../utils/rateLimiter.js';
import { logger } from '../utils/logger.js';

export const data = new SlashCommandBuilder()
  .setName('pick')
  .setDescription('Analyze a bet slip and provide AI-powered betting analysis')
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
  )
  .addBooleanOption(option =>
    option
      .setName('debug')
      .setDescription('Enable debug mode for detailed analysis')
      .setRequired(false)
  );

export async function execute(interaction) {
  const startTime = Date.now();
  
  try {
    await interaction.deferReply();
    
    // Rate limiting
    if (!rateLimiter.allow(interaction.user.id)) {
      const timeRemaining = rateLimiter.getTimeRemaining(interaction.user.id);
      await interaction.editReply(`⏰ Rate limit exceeded. Please wait ${Math.ceil(timeRemaining / 1000)} seconds before making another pick.`);
      return;
    }
    
    const channelType = interaction.options.getString('channel_type');
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
      debug,
      imageUrl: image.url
    });
    
    // Step 1: Extract text from image using AI-powered OCR
    logger.info('Starting OCR analysis...');
    const ocrResult = await analyzeImage(image.url, debug);
    
    if (!ocrResult.success) {
      await interaction.editReply(`❌ OCR failed: ${ocrResult.error}`);
      return;
    }
    
    // Step 2: Parse bet slip data
    logger.info('Parsing bet slip data...');
    const betSlip = ocrResult.data;
    
    if (!betSlip || !betSlip.legs || betSlip.legs.length === 0) {
      await interaction.editReply('❌ Could not parse bet slip. Please check the image quality.');
      return;
    }
    
    // Step 3: Get game data and statistics
    logger.info('Fetching game data...');
    const gameData = await getGameData(betSlip.legs[0]);
    
    if (!gameData) {
      await interaction.editReply('❌ Could not fetch game data. Please try again.');
      return;
    }
    
    // Step 4: Generate AI analysis
    logger.info('Generating AI analysis...');
    const analysis = await generateAnalysis(betSlip, gameData, debug);
    
    if (!analysis.success) {
      await interaction.editReply(`❌ AI analysis failed: ${analysis.error}`);
      return;
    }
    
    // Step 5: Create betting message
    logger.info('Creating betting message...');
    const message = await createBettingMessage(channelType, betSlip, gameData, analysis.data, image.url, notes);
    
    if (!message.success) {
      await interaction.editReply(`❌ Failed to create message: ${message.error}`);
      return;
    }
    
    // Step 6: Send response
    await interaction.editReply(message.data);
    
    const totalTime = Date.now() - startTime;
    logger.info('Pick command completed successfully', {
      channelType,
      userId: interaction.user.id,
      totalTime: `${totalTime}ms`,
      ocrTime: ocrResult.time,
      analysisTime: analysis.time
    });
    
  } catch (error) {
    logger.error('Pick command failed', {
      error: error.message,
      stack: error.stack,
      userId: interaction.user.id
    });
    
    await interaction.editReply('❌ An unexpected error occurred. Please try again.');
  }
} 