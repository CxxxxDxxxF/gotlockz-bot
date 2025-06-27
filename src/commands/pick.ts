/**
 * /pick - Post a betting pick with image analysis and AI
 *
 * Options:
 *   - channel_type (string, required): Type of pick to post (Free Play, VIP Pick, Lotto Ticket)
 *   - image (attachment, required): Betting slip image
 *   - description (string, optional): Additional notes
 */
import { SlashCommandBuilder, ChatInputCommandInteraction } from 'discord.js';
import { analyzeImage } from '../services/ocrService';
import { getGameData } from '../services/mlbService';
import { getForecast } from '../services/weatherService';
import { allow } from '../utils/rateLimiter';
import { createVIPPlayMessage, formatVIPPlayForDiscord, validateVIPPlayMessage } from '../services/vipPlayService';
import { parseBetSlip } from '../utils/parser';
import { generateAnalysis } from '../services/analysisService';

export const data = new SlashCommandBuilder()
  .setName('pick')
  .setDescription('Analyze a bet slip and provide VIP play analysis')
  .addAttachmentOption(option =>
    option
      .setName('image')
      .setDescription('Bet slip image to analyze')
      .setRequired(true)
  );

export async function execute(interaction: ChatInputCommandInteraction) {
  try {
    await interaction.deferReply();
    
    // Rate limiting check
    if (!allow(interaction.user.id)) {
      return await interaction.editReply('⏰ Rate limit exceeded. Please wait before making another pick.');
    }
    
    const image = interaction.options.getAttachment('image');
    if (!image) {
      return await interaction.editReply('❌ Please provide a bet slip image.');
    }
    
    // Extract text from image
    const imageBuffer = await fetch(image.url).then(res => res.arrayBuffer()).then(buf => Buffer.from(buf));
    const ocrLines = await analyzeImage(imageBuffer);
    
    // Parse bet slip
    const betSlip = await parseBetSlip(ocrLines);
    if (!betSlip) {
      return await interaction.editReply('❌ Could not parse bet slip. Please check the image quality.');
    }
    
    // Get game data
    const gameData = await getGameData(betSlip.legs[0]?.gameId || '');
    if (!gameData) {
      return await interaction.editReply('❌ Could not fetch game data. Please try again.');
    }
    
    // Get weather data
    const weather = await getForecast('New York'); // Fallback location for now
    const edge = 0.05; // Default edge calculation
    const analysis = await generateAnalysis(betSlip, gameData, edge, weather);
    
    // Create structured VIP Play message
    const vipMessage = await createVIPPlayMessage(betSlip, gameData, analysis, image.url);
    
    // Validate the message
    if (!validateVIPPlayMessage(vipMessage)) {
      return await interaction.editReply('❌ Failed to create valid VIP Play message.');
    }
    
    // Format for Discord
    const embed = formatVIPPlayForDiscord(vipMessage);
    
    return await interaction.editReply({
      content: `🎯 **VIP Play #${vipMessage.playNumber}** - GotLockz Family, let's get this bread! 💰`,
      embeds: [embed]
    });
  } catch (err: any) {
    console.error('Error in pick command:', err);
    return await interaction.editReply(`❌ An error occurred: ${err.message}`);
  }
} 