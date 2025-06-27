/**
 * /pick - Post a betting pick with image analysis and AI
 *
 * Options:
 *   - channel_type (string, required): Type of pick to post (Free Play, VIP Pick, Lotto Ticket)
 *   - image (attachment, required): Betting slip image
 *   - description (string, optional): Additional notes
 */
import { SlashCommandBuilder, ChatInputCommandInteraction, EmbedBuilder } from 'discord.js';
import { analyzeImage } from '../services/ocrService';
import { getGameData } from '../services/mlbService';
import { calculateEdge } from '../services/bettingService';
import { generateAnalysis } from '../services/analysisService';
import { getForecast } from '../services/weatherService';
import { allow } from '../utils/rateLimiter';

export const data = new SlashCommandBuilder()
  .setName('pick')
  .setDescription('Post a betting pick with image analysis and AI')
  .addStringOption(option =>
    option.setName('channel_type')
      .setDescription('Type of pick to post')
      .setRequired(true)
      .addChoices(
        { name: 'Free Play', value: 'free_play' },
        { name: 'VIP Pick', value: 'vip_pick' },
        { name: 'Lotto Ticket', value: 'lotto_ticket' }
      )
  )
  .addAttachmentOption(option =>
    option.setName('image')
      .setDescription('Betting slip image')
      .setRequired(true)
  )
  .addStringOption(option =>
    option.setName('description')
      .setDescription('Additional notes (optional)')
      .setRequired(false)
  );

function mapOcrToBetSlip(ocr: any): any {
  // TODO: Map OCRResult to BetSlip (stub)
  return {
    gameId: '123',
    teams: ['Team A', 'Team B'],
    bet_type: 'ML',
    odds: '+120',
    stake: '100',
    potential_win: '220',
    confidence: ocr.confidence || 0.8,
    timestamp: new Date(),
    bookmaker: 'StubBook',
  };
}

function buildPickEmbed(betSlip: any, gameData: any, edge: number, weather: any) {
  const color = edge > 5 ? '#00ff00' : edge > 2 ? '#ffff00' : '#ff0000'; // Green/Yellow/Red based on edge
  
  return new EmbedBuilder()
    .setTitle('🏈 Betting Pick')
    .setColor(color)
    .setDescription(`**${betSlip.teams.join(' vs ')}**\nOdds: ${betSlip.odds} | Edge: ${edge.toFixed(2)}%`)
    .addFields(
      { name: '📊 Game', value: betSlip.gameId, inline: true },
      { name: '💰 Stake', value: betSlip.stake, inline: true },
      { name: '🎯 Potential Win', value: betSlip.potential_win, inline: true },
      { name: '🏪 Bookmaker', value: betSlip.bookmaker, inline: true },
      { name: '🌤️ Weather', value: `${weather?.description || 'N/A'}, ${weather?.temperature || 'N/A'}°F`, inline: true }
    )
    .setTimestamp();
}

export async function execute(interaction: ChatInputCommandInteraction) {
  try {
    // Rate limiting check
    if (!allow(interaction.user.id)) {
      return await interaction.reply({ 
        content: '⏰ Please wait a bit before requesting another analysis.', 
        ephemeral: true 
      });
    }

    const image = interaction.options.getAttachment('image');
    if (!image) return await interaction.reply({ content: 'No image provided.', ephemeral: true });
    
    const imageBuffer = await fetch(image.url).then(res => res.arrayBuffer()).then(buf => Buffer.from(buf));
    const ocrResult = await analyzeImage(imageBuffer);
    const betSlip = mapOcrToBetSlip(ocrResult);
    const gameData = await getGameData(betSlip.gameId);
    const weather = await getForecast('New York'); // Fallback location for now
    const edge = calculateEdge(betSlip);
    const analysisText = await generateAnalysis(betSlip, gameData, edge, weather);
    
    return await interaction.reply({
      embeds: [
        buildPickEmbed(betSlip, gameData, edge, weather),
        new EmbedBuilder()
          .setTitle('🤖 GPT Analysis')
          .setDescription(analysisText)
          .setColor('#0099ff')
          .setTimestamp()
      ]
    });
  } catch (err: any) {
    return await interaction.reply({ content: `Error: ${err.message || err}`, ephemeral: true });
  }
} 