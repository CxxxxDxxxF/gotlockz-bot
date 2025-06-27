/**
 * /admin - Admin commands
 *
 * Subcommands:
 *   - purge: Delete a number of messages
 *   - stats: Show bot uptime and version
 */
import { SlashCommandBuilder, ChatInputCommandInteraction, Client, EmbedBuilder } from 'discord.js';
import pkg from '../../package.json';

export const data = new SlashCommandBuilder()
  .setName('admin')
  .setDescription('Admin commands')
  .addSubcommand(sub =>
    sub.setName('purge')
      .setDescription('Delete a number of messages')
      .addIntegerOption(opt =>
        opt.setName('amount')
          .setDescription('Number of messages to delete')
          .setRequired(true)
      )
  )
  .addSubcommand(sub =>
    sub.setName('stats')
      .setDescription('Show bot uptime and version')
  );

export async function execute(interaction: ChatInputCommandInteraction, client?: Client) {
  const sub = interaction.options.getSubcommand();
  if (sub === 'purge') {
    const amount = interaction.options.getInteger('amount', true);
    if (!interaction.channel || !('bulkDelete' in interaction.channel)) {
      return interaction.reply({ content: 'Cannot purge messages in this channel.', ephemeral: true });
    }
    // @ts-ignore
    await interaction.channel.bulkDelete(amount, true);
    return interaction.reply({ content: `Deleted ${amount} messages.`, ephemeral: true });
  } else if (sub === 'stats') {
    const uptime = client?.uptime ? Math.floor(client.uptime / 1000) : 0;
    const embed = new EmbedBuilder()
      .setTitle('Bot Stats')
      .addFields(
        { name: 'Uptime', value: `${uptime} seconds`, inline: true },
        { name: 'Version', value: pkg.version, inline: true }
      )
      .setTimestamp();
    return interaction.reply({ embeds: [embed], ephemeral: true });
  }
  return;
} 