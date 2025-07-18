import { SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } from 'discord.js';
import { logger } from '../utils/logger.js';

export const data = new SlashCommandBuilder()
  .setName('suggest')
  .setDescription('Submit a suggestion for the GotLockz team')
  .addStringOption(option =>
    option.setName('suggestion')
      .setDescription('Your suggestion for improving the bot')
      .setRequired(true)
      .setMaxLength(1000));

export async function execute(interaction) {
  try {
    await interaction.deferReply({ ephemeral: true });

    const suggestion = interaction.options.getString('suggestion');
    const userId = interaction.user.id;
    const username = interaction.user.username;

    // Create suggestion embed
    const suggestionEmbed = new EmbedBuilder()
      .setColor(0x0099ff)
      .setTitle('💡 New Suggestion')
      .setDescription(suggestion)
      .addFields(
        { name: '👤 Submitted by', value: `<@${userId}>`, inline: true },
        { name: '📅 Date', value: new Date().toLocaleDateString(), inline: true },
        { name: '📊 Status', value: '🟡 Pending Review', inline: true }
      )
      .setTimestamp()
      .setFooter({ text: 'GotLockz Bot Suggestions' });

    // Create action buttons
    const actionRow = new ActionRowBuilder()
      .addComponents(
        new ButtonBuilder()
          .setCustomId('suggest_approve')
          .setLabel('✅ Approve')
          .setStyle(ButtonStyle.Success),
        new ButtonBuilder()
          .setCustomId('suggest_deny')
          .setLabel('❌ Deny')
          .setStyle(ButtonStyle.Danger),
        new ButtonBuilder()
          .setCustomId('suggest_implement')
          .setLabel('🚀 Implement')
          .setStyle(ButtonStyle.Primary)
      );

    // Send to suggestions channel
    const suggestionsChannel = interaction.client.channels.cache.get(process.env.SUGGESTIONS_CHANNEL_ID);
    
    if (suggestionsChannel) {
      const message = await suggestionsChannel.send({
        embeds: [suggestionEmbed],
        components: [actionRow]
      });

      // Store suggestion in database (placeholder)
      logger.info('Suggestion submitted', {
        userId,
        username,
        suggestion,
        messageId: message.id
      });

      await interaction.editReply({
        content: '✅ Your suggestion has been submitted successfully! The team will review it.',
        ephemeral: true
      });
    } else {
      await interaction.editReply({
        content: '❌ Suggestions channel not configured. Please contact an administrator.',
        ephemeral: true
      });
    }

  } catch (error) {
    logger.error('Suggestion command failed:', error);
    await interaction.editReply({
      content: '❌ An error occurred while submitting your suggestion.',
      ephemeral: true
    });
  }
} 