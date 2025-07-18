import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';
import { logger } from '../utils/logger.js';

export const data = new SlashCommandBuilder()
  .setName('ping')
  .setDescription('Check bot response time and status');

export async function execute(interaction) {
  try {
    const sent = Date.now();
    
    // Calculate bot latency
    const botLatency = Date.now() - sent;
    const apiLatency = Math.round(interaction.client.ws.ping);
    
    // Determine status color and message
    let status, color, statusEmoji;
    
    if (apiLatency < 100) {
      status = 'Excellent';
      color = 0x00FF00;
      statusEmoji = '🟢';
    } else if (apiLatency < 200) {
      status = 'Good';
      color = 0xFFFF00;
      statusEmoji = '🟡';
    } else if (apiLatency < 500) {
      status = 'Fair';
      color = 0xFFA500;
      statusEmoji = '🟠';
    } else {
      status = 'Poor';
      color = 0xFF0000;
      statusEmoji = '🔴';
    }
    
    const embed = new EmbedBuilder()
      .setColor(color)
      .setTitle(`${statusEmoji} GotLockz Bot Status`)
      .setDescription('**GotLockz Family** - Bot is online and ready! 🚀')
      .addFields(
        {
          name: '📡 **API Latency**',
          value: `${apiLatency}ms`,
          inline: true
        },
        {
          name: '🤖 **Bot Latency**',
          value: `${botLatency}ms`,
          inline: true
        },
        {
          name: '📊 **Status**',
          value: status,
          inline: true
        },
        {
          name: '🖥️ **Platform**',
          value: 'M4 Mac (ARM64)',
          inline: true
        },
        {
          name: '⏰ **Uptime**',
          value: formatUptime(process.uptime()),
          inline: true
        },
        {
          name: '💾 **Memory**',
          value: formatMemory(process.memoryUsage()),
          inline: true
        }
      )
      .setFooter({ 
        text: 'GotLockz Family | 21+ Only | Please bet responsibly' 
      })
      .setTimestamp();
    
    await interaction.reply({ embeds: [embed] });
    
    logger.command('ping', interaction.user.id, { 
      apiLatency, 
      botLatency, 
      status 
    });
    
  } catch (error) {
    logger.error('Ping command failed:', error);
    await interaction.reply({ 
      content: '❌ Error checking bot status. Please try again.', 
      ephemeral: true 
    });
  }
}

function formatUptime(seconds) {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (days > 0) {
    return `${days}d ${hours}h ${minutes}m`;
  } else if (hours > 0) {
    return `${hours}h ${minutes}m`;
  } else {
    return `${minutes}m`;
  }
}

function formatMemory(memoryUsage) {
  const used = Math.round(memoryUsage.heapUsed / 1024 / 1024);
  const total = Math.round(memoryUsage.heapTotal / 1024 / 1024);
  return `${used}MB / ${total}MB`;
} 