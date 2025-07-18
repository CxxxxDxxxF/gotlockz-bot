/**
 * /admin - Admin commands
 *
 * Subcommands:
 *   - purge: Delete a number of messages
 *   - stats: Show bot uptime and version
 */
import { ChatInputCommandInteraction, Client, EmbedBuilder } from 'discord.js';
import { SlashCommandBuilder } from '@discordjs/builders';
import pkg from '../../package.json';

export const data = new SlashCommandBuilder()
  .setName('admin')
  .setDescription('Admin commands')
  .addSubcommand((sub: any) =>
    sub.setName('purge')
      .setDescription('Delete a number of messages')
      .addIntegerOption((opt: any) =>
        opt.setName('amount')
          .setDescription('Number of messages to delete')
          .setRequired(true)
      )
  )
  .addSubcommand((sub: any) =>
    sub.setName('stats')
      .setDescription('Show bot uptime and version')
  );

export async function execute(interaction: ChatInputCommandInteraction, client?: Client): Promise<void> {
  const sub: string = interaction.options.getSubcommand();
  if (sub === 'purge') {
    const amount = interaction.options.getInteger('amount', true);
    if (!interaction.channel || !('bulkDelete' in interaction.channel)) {
      await interaction.reply({ content: 'Cannot purge messages in this channel.', ephemeral: true });
      return;
    }
    // @ts-ignore
    await interaction.channel.bulkDelete(amount, true);
    await interaction.reply({ content: `Deleted ${amount} messages.`, ephemeral: true });
    return;
  } else if (sub === 'stats') {
    const uptime = client?.uptime ? Math.floor(client.uptime / 1000) : 0;
    const embed = new EmbedBuilder()
      .setDescription('Bot Stats')
      .addFields(
        { name: 'Uptime', value: `${uptime} seconds`, inline: true },
        { name: 'Version', value: pkg.version, inline: true }
      )
      .setTimestamp();
    await interaction.reply({ embeds: [embed], ephemeral: true });
    return;
  }
  return;
} 