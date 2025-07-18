import { SlashCommandBuilder } from 'discord.js';
import { rateLimiter } from '../utils/rateLimiter.js';
import { logger, logError, logCommand, logService } from '../utils/logger.js';

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

export async function execute (interaction) {
  const startTime = Date.now();
  const commandId = `pick_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  try {
    // Log command start
    logCommand('pick', interaction.user.id, {
      commandId,
      channelType: interaction.options.getString('channel_type'),
      hasImage: !!interaction.options.getAttachment('image'),
      hasNotes: !!interaction.options.getString('notes'),
      debug: interaction.options.getBoolean('debug') ?? false
    });

    console.log(`🚀 [${commandId}] Pick command started by ${interaction.user.username} (${interaction.user.id})`);

    await interaction.deferReply();

    // Rate limiting
    if (!rateLimiter.allow(interaction.user.id)) {
      const timeRemaining = rateLimiter.getTimeRemaining(interaction.user.id);
      const errorMsg = `⏰ Rate limit exceeded. Please wait ${Math.ceil(timeRemaining / 1000)} seconds before making another pick.`;
      
      logCommand('pick', interaction.user.id, { commandId, result: 'rate_limited', timeRemaining });
      console.log(`⏰ [${commandId}] Rate limited for user ${interaction.user.id}`);
      
      await interaction.editReply(errorMsg);
      return;
    }

    const channelType = interaction.options.getString('channel_type');
    const image = interaction.options.getAttachment('image');
    const notes = interaction.options.getString('notes');
    const debug = interaction.options.getBoolean('debug') ?? false;

    if (!image) {
      logError(new Error('No image provided'), { commandId, userId: interaction.user.id });
      await interaction.editReply('❌ Please provide a bet slip image.');
      return;
    }

    console.log(`📸 [${commandId}] Processing image: ${image.url}`);

    // Dynamically import services to avoid sharp loading during deployment
    console.log(`📦 [${commandId}] Importing services...`);
    
    let analyzeImage, getGameData, generateAnalysis, createBettingMessage;
    
    try {
      const ocrModule = await import('../services/ocrService.js');
      analyzeImage = ocrModule.analyzeImage;
      console.log(`✅ [${commandId}] OCR service imported`);
    } catch (error) {
      logError(error, { commandId, service: 'ocr', userId: interaction.user.id });
      throw new Error(`OCR service import failed: ${error.message}`);
    }

    try {
      const mlbModule = await import('../services/mlbService.js');
      getGameData = mlbModule.getGameData;
      console.log(`✅ [${commandId}] MLB service imported`);
    } catch (error) {
      logError(error, { commandId, service: 'mlb', userId: interaction.user.id });
      throw new Error(`MLB service import failed: ${error.message}`);
    }

    try {
      const aiModule = await import('../services/aiService.js');
      generateAnalysis = aiModule.generateAnalysis;
      console.log(`✅ [${commandId}] AI service imported`);
    } catch (error) {
      logError(error, { commandId, service: 'ai', userId: interaction.user.id });
      throw new Error(`AI service import failed: ${error.message}`);
    }

    try {
      const bettingModule = await import('../services/bettingService.js');
      createBettingMessage = bettingModule.createBettingMessage;
      console.log(`✅ [${commandId}] Betting service imported`);
    } catch (error) {
      logError(error, { commandId, service: 'betting', userId: interaction.user.id });
      throw new Error(`Betting service import failed: ${error.message}`);
    }

    // Step 1: Extract text from image using AI-powered OCR
    console.log(`🔍 [${commandId}] Starting OCR analysis...`);
    logService('ocr', 'analyze_image', { commandId, imageUrl: image.url, debug });
    
    const ocrResult = await analyzeImage(image.url, debug);

    if (!ocrResult.success) {
      logError(new Error(`OCR failed: ${ocrResult.error}`), { 
        commandId, 
        userId: interaction.user.id,
        ocrError: ocrResult.error,
        ocrTime: ocrResult.time
      });
      
      console.log(`❌ [${commandId}] OCR failed: ${ocrResult.error}`);
      await interaction.editReply(`❌ OCR failed: ${ocrResult.error}\n\nPlease ensure the image is clear and contains readable text.`);
      return;
    }

    console.log(`✅ [${commandId}] OCR completed in ${ocrResult.time}ms`);

    // Step 2: Parse bet slip data
    console.log(`📊 [${commandId}] Parsing bet slip data...`);
    const betSlip = ocrResult.data;

    if (!betSlip || !betSlip.legs || betSlip.legs.length === 0) {
      logError(new Error('Bet slip parsing failed'), { 
        commandId, 
        userId: interaction.user.id,
        betSlip,
        ocrText: ocrResult.rawText
      });
      
      console.log(`❌ [${commandId}] Bet slip parsing failed:`, betSlip);
      await interaction.editReply('❌ Could not parse bet slip. Please check the image quality and ensure team names are visible.');
      return;
    }

    console.log(`✅ [${commandId}] Bet slip parsed: ${betSlip.legs.length} legs found`);

    // Step 3: Get game data and statistics
    console.log(`🏟️ [${commandId}] Fetching game data...`);
    logService('mlb', 'get_game_data', { commandId, legs: betSlip.legs });
    
    const gameData = await getGameData(betSlip.legs[0]);

    // Game data is optional, continue even if it fails
    if (!gameData) {
      console.log(`⚠️ [${commandId}] Game data fetch failed, continuing with basic analysis`);
      logService('mlb', 'get_game_data', { commandId, result: 'failed' });
    } else {
      console.log(`✅ [${commandId}] Game data fetched successfully`);
    }

    // Step 4: Generate AI analysis
    console.log(`🤖 [${commandId}] Generating AI analysis...`);
    logService('ai', 'generate_analysis', { commandId, legs: betSlip.legs.length });
    
    const analysis = await generateAnalysis(betSlip, gameData, debug);

    if (!analysis.success) {
      console.log(`⚠️ [${commandId}] AI analysis failed: ${analysis.error}, using fallback`);
      logService('ai', 'generate_analysis', { commandId, result: 'failed', error: analysis.error });
      // Continue with fallback analysis
    } else {
      console.log(`✅ [${commandId}] AI analysis completed in ${analysis.time}ms`);
    }

    // Step 5: Create betting message
    console.log(`📝 [${commandId}] Creating betting message...`);
    logService('betting', 'create_message', { commandId, channelType });
    
    const message = await createBettingMessage(channelType, betSlip, gameData, analysis.data || analysis, image.url, notes);

    if (!message.success) {
      logError(new Error(`Message creation failed: ${message.error}`), { 
        commandId, 
        userId: interaction.user.id,
        channelType,
        betSlip,
        analysis: analysis.data || analysis
      });
      
      console.log(`❌ [${commandId}] Message creation failed: ${message.error}`);
      await interaction.editReply(`❌ Failed to create message: ${message.error}\n\nPlease try again or contact support.`);
      return;
    }

    console.log(`✅ [${commandId}] Message created successfully`);

    // Step 6: Send response
    await interaction.editReply(message.data);

    const totalTime = Date.now() - startTime;
    console.log(`🎉 [${commandId}] Pick command completed successfully in ${totalTime}ms`);
    
    logCommand('pick', interaction.user.id, { 
      commandId, 
      result: 'success',
      totalTime,
      ocrTime: ocrResult.time,
      analysisTime: analysis.time
    });

  } catch (error) {
    const totalTime = Date.now() - startTime;
    
    logError(error, {
      commandId,
      userId: interaction.user.id,
      totalTime,
      channelType: interaction.options.getString('channel_type'),
      hasImage: !!interaction.options.getAttachment('image')
    });

    console.error(`💥 [${commandId}] Pick command failed after ${totalTime}ms:`, {
      error: error.message,
      stack: error.stack,
      userId: interaction.user.id
    });

    const errorMessage = '❌ An unexpected error occurred. Please try again.\n\n' +
                        'If this problem persists, please:\n' +
                        '• Check that the image is clear and readable\n' +
                        '• Ensure team names are visible in the image\n' +
                        '• Try uploading a different image format (PNG, JPG)\n\n' +
                        `Error ID: ${commandId}`;

    try {
      await interaction.editReply(errorMessage);
    } catch (replyError) {
      console.error(`💥 [${commandId}] Failed to send error reply:`, replyError.message);
    }
  }
}
