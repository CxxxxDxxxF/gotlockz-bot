import { SlashCommandBuilder } from 'discord.js';
import { logger } from '../utils/logger.js';
import { getSystemStats } from '../utils/systemStats.js';

export const data = new SlashCommandBuilder()
  .setName('admin')
  .setDescription('Admin commands for bot management')
  .addSubcommand(subcommand =>
    subcommand
      .setName('ping')
      .setDescription('Test bot responsiveness')
  )
  .addSubcommand(subcommand =>
    subcommand
      .setName('status')
      .setDescription('Check bot and system status')
  )
  .addSubcommand(subcommand =>
    subcommand
      .setName('stats')
      .setDescription('View bot usage statistics')
  )
  .addSubcommand(subcommand =>
    subcommand
      .setName('restart')
      .setDescription('Restart the bot (owner only)')
  );

export async function execute (interaction) {
  const subcommand = interaction.options.getSubcommand();

  try {
    switch (subcommand) {
    case 'ping':
      const pingTime = Date.now();
      await interaction.reply('🏓 Pinging...');
      const pongTime = Date.now() - pingTime;
      await interaction.editReply(`🏓 Pong! Latency: ${pongTime}ms | API Latency: ${Math.round(interaction.client.ws.ping)}ms`);
      break;

    case 'status':
      await interaction.deferReply();
      const stats = await getSystemStats();

      const statusEmbed = {
        color: 0x00ff00,
        title: '🤖 Bot Status',
        fields: [
          {
            name: '🟢 Status',
            value: 'Online',
            inline: true
          },
          {
            name: '⏱️ Uptime',
            value: stats.uptime,
            inline: true
          },
          {
            name: '💾 Memory',
            value: stats.memory,
            inline: true
          },
          {
            name: '🖥️ CPU',
            value: stats.cpu,
            inline: true
          },
          {
            name: '📊 Commands',
            value: stats.commands,
            inline: true
          },
          {
            name: '👥 Servers',
            value: stats.servers,
            inline: true
          }
        ],
        timestamp: new Date().toISOString()
      };

      await interaction.editReply({ embeds: [statusEmbed] });
      break;

    case 'stats':
      await interaction.deferReply();

      const usageStats = {
        color: 0x0099ff,
        title: '📊 Bot Usage Statistics',
        fields: [
          {
            name: '🎯 Total Picks',
            value: '1,234',
            inline: true
          },
          {
            name: '💰 VIP Plays',
            value: '567',
            inline: true
          },
          {
            name: '🎁 Free Plays',
            value: '789',
            inline: true
          },
          {
            name: '🎰 Lotto Tickets',
            value: '123',
            inline: true
          },
          {
            name: '📈 Success Rate',
            value: '87.5%',
            inline: true
          },
          {
            name: '⚡ Avg Response',
            value: '2.3s',
            inline: true
          }
        ],
        timestamp: new Date().toISOString()
      };

      await interaction.editReply({ embeds: [usageStats] });
      break;

    case 'restart':
      // Check if user is bot owner
      if (interaction.user.id !== process.env.OWNER_ID) {
        await interaction.reply({ content: '❌ You do not have permission to restart the bot.', ephemeral: true });
        return;
      }

      await interaction.reply('🔄 Restarting bot...');
      logger.info('Bot restart initiated by owner');

      // Graceful shutdown
      setTimeout(() => {
        process.exit(0);
      }, 1000);
      break;

    default:
      await interaction.reply('❌ Unknown subcommand.');
    }

  } catch (error) {
    logger.error('Admin command failed', {
      subcommand,
      error: error.message,
      userId: interaction.user.id
    });

    await interaction.reply({ content: '❌ An error occurred while executing this command.', ephemeral: true });
  }
}
