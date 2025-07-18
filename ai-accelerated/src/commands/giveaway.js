import { SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } from 'discord.js';
import { logger } from '../utils/logger.js';

export const data = new SlashCommandBuilder()
  .setName('giveaway')
  .setDescription('Create a giveaway for the community')
  .addStringOption(option =>
    option.setName('prize')
      .setDescription('What is being given away?')
      .setRequired(true))
  .addIntegerOption(option =>
    option.setName('winners')
      .setDescription('Number of winners')
      .setRequired(true)
      .setMinValue(1)
      .setMaxValue(10))
  .addIntegerOption(option =>
    option.setName('duration')
      .setDescription('Duration in minutes')
      .setRequired(true)
      .setMinValue(1)
      .setMaxValue(10080)); // Max 1 week

export async function execute(interaction) {
  try {
    // Check if user has permission to create giveaways
    if (!interaction.member.permissions.has('ManageGuild') && interaction.user.id !== process.env.OWNER_ID) {
      await interaction.reply({
        content: '❌ You need Manage Server permissions to create giveaways.',
        ephemeral: true
      });
      return;
    }

    await interaction.deferReply();

    const prize = interaction.options.getString('prize');
    const winners = interaction.options.getInteger('winners');
    const duration = interaction.options.getInteger('duration');
    const endTime = Date.now() + (duration * 60 * 1000);

    // Create giveaway embed
    const giveawayEmbed = new EmbedBuilder()
      .setColor(0xff6b6b)
      .setTitle('🎉 GIVEAWAY 🎉')
      .setDescription(`**${prize}**`)
      .addFields(
        { name: '👑 Winners', value: `${winners}`, inline: true },
        { name: '⏰ Ends', value: `<t:${Math.floor(endTime / 1000)}:R>`, inline: true },
        { name: '🎯 Participants', value: '0', inline: true }
      )
      .setTimestamp()
      .setFooter({ text: 'React with 🎉 to enter!' });

    // Create enter button
    const actionRow = new ActionRowBuilder()
      .addComponents(
        new ButtonBuilder()
          .setCustomId('giveaway_enter')
          .setLabel('🎉 Enter Giveaway')
          .setStyle(ButtonStyle.Primary)
      );

    // Send giveaway
    const giveawayChannel = interaction.client.channels.cache.get(process.env.GIVEAWAY_CHANNEL_ID) || interaction.channel;
    
    const message = await giveawayChannel.send({
      embeds: [giveawayEmbed],
      components: [actionRow]
    });

    // Store giveaway data (placeholder for database)
    const giveawayData = {
      messageId: message.id,
      channelId: giveawayChannel.id,
      prize,
      winners,
      endTime,
      participants: [],
      ended: false,
      createdBy: interaction.user.id
    };

    logger.info('Giveaway created', {
      messageId: message.id,
      prize,
      winners,
      duration,
      createdBy: interaction.user.id
    });

    // Set timeout to end giveaway
    setTimeout(async () => {
      await endGiveaway(giveawayData, interaction.client);
    }, duration * 60 * 1000);

    await interaction.editReply({
      content: `✅ Giveaway created successfully in ${giveawayChannel}!`,
      ephemeral: true
    });

  } catch (error) {
    logger.error('Giveaway command failed:', error);
    await interaction.editReply({
      content: '❌ An error occurred while creating the giveaway.',
      ephemeral: true
    });
  }
}

async function endGiveaway(giveawayData, client) {
  try {
    const channel = client.channels.cache.get(giveawayData.channelId);
    if (!channel) return;

    const message = await channel.messages.fetch(giveawayData.messageId);
    if (!message) return;

    // Select winners
    const participants = giveawayData.participants;
    const winners = [];
    
    for (let i = 0; i < Math.min(giveawayData.winners, participants.length); i++) {
      const winnerIndex = Math.floor(Math.random() * participants.length);
      winners.push(participants[winnerIndex]);
      participants.splice(winnerIndex, 1);
    }

    // Update embed
    const embed = EmbedBuilder.from(message.embeds[0]);
    embed.setColor(winners.length > 0 ? 0x51cf66 : 0xff6b6b);
    embed.setTitle(winners.length > 0 ? '🎉 GIVEAWAY ENDED 🎉' : '❌ GIVEAWAY ENDED ❌');
    
    if (winners.length > 0) {
      embed.setDescription(`**${giveawayData.prize}**\n\n🎊 **Winners:** ${winners.map(id => `<@${id}>`).join(', ')}`);
    } else {
      embed.setDescription(`**${giveawayData.prize}**\n\n❌ No participants entered this giveaway.`);
    }

    embed.spliceFields(1, 1, { name: '⏰ Ended', value: `<t:${Math.floor(Date.now() / 1000)}:F>`, inline: true });
    embed.spliceFields(2, 1, { name: '🎯 Participants', value: `${giveawayData.participants.length}`, inline: true });

    // Remove button
    const actionRow = new ActionRowBuilder()
      .addComponents(
        new ButtonBuilder()
          .setCustomId('giveaway_ended')
          .setLabel('Giveaway Ended')
          .setStyle(ButtonStyle.Secondary)
          .setDisabled(true)
      );

    await message.edit({
      embeds: [embed],
      components: [actionRow]
    });

    // Announce winners
    if (winners.length > 0) {
      await channel.send({
        content: `🎉 Congratulations ${winners.map(id => `<@${id}>`).join(', ')}! You won **${giveawayData.prize}**!`,
        allowedMentions: { users: winners }
      });
    }

    logger.info('Giveaway ended', {
      messageId: giveawayData.messageId,
      winners: winners.length,
      participants: giveawayData.participants.length
    });

  } catch (error) {
    logger.error('Error ending giveaway:', error);
  }
} 