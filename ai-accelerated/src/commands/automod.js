import { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } from 'discord.js';
import { logger } from '../utils/logger.js';

// In-memory automod storage (replace with database in production)
const automodSettings = new Map();
const userWarnings = new Map();

// Automod configuration
const AUTOMOD_CONFIG = {
  MAX_WARNINGS: 3,
  WARNING_EXPIRY: 24 * 60 * 60 * 1000, // 24 hours
  SPAM_THRESHOLD: 5, // messages per 10 seconds
  CAPS_THRESHOLD: 0.7, // 70% caps ratio
  LINK_WHITELIST: ['discord.com', 'discord.gg', 'youtube.com', 'youtu.be']
};

export const data = new SlashCommandBuilder()
  .setName('automod')
  .setDescription('Configure automod settings')
  .addSubcommand(subcommand =>
    subcommand
      .setName('setup')
      .setDescription('Setup automod for this server')
      .addBooleanOption(option =>
        option.setName('enabled')
          .setDescription('Enable automod')
          .setRequired(true))
      .addBooleanOption(option =>
        option.setName('spam_protection')
          .setDescription('Enable spam protection')
          .setRequired(false))
      .addBooleanOption(option =>
        option.setName('caps_protection')
          .setDescription('Enable caps protection')
          .setRequired(false))
      .addBooleanOption(option =>
        option.setName('link_protection')
          .setDescription('Enable link protection')
          .setRequired(false))
      .addBooleanOption(option =>
        option.setName('mention_protection')
          .setDescription('Enable mention spam protection')
          .setRequired(false)))
  .addSubcommand(subcommand =>
    subcommand
      .setName('status')
      .setDescription('View current automod settings'))
  .addSubcommand(subcommand =>
    subcommand
      .setName('warnings')
      .setDescription('View user warnings')
      .addUserOption(option =>
        option.setName('user')
          .setDescription('User to check warnings for')
          .setRequired(false)))
  .addSubcommand(subcommand =>
    subcommand
      .setName('clear')
      .setDescription('Clear warnings for a user')
      .addUserOption(option =>
        option.setName('user')
          .setDescription('User to clear warnings for')
          .setRequired(true)))
  .setDefaultMemberPermissions(PermissionFlagsBits.ManageGuild);

export async function execute(interaction) {
  const subcommand = interaction.options.getSubcommand();
  const guildId = interaction.guild.id;

  try {
    switch (subcommand) {
    case 'setup': {
      await handleSetup(interaction, guildId);
      break;
    }

    case 'status': {
      await handleStatus(interaction, guildId);
      break;
    }

    case 'warnings': {
      await handleWarnings(interaction, guildId);
      break;
    }

    case 'clear': {
      await handleClear(interaction, guildId);
      break;
    }

    default: {
      await interaction.reply('❌ Unknown subcommand.');
    }
    }
  } catch (error) {
    logger.error('Automod command failed:', error);
    await interaction.reply({
      content: '❌ An error occurred while processing your request.',
      ephemeral: true
    });
  }
}

async function handleSetup(interaction, guildId) {
  const enabled = interaction.options.getBoolean('enabled');
  const spamProtection = interaction.options.getBoolean('spam_protection') ?? true;
  const capsProtection = interaction.options.getBoolean('caps_protection') ?? true;
  const linkProtection = interaction.options.getBoolean('link_protection') ?? true;
  const mentionProtection = interaction.options.getBoolean('mention_protection') ?? true;

  const settings = {
    enabled,
    spamProtection,
    capsProtection,
    linkProtection,
    mentionProtection,
    logChannel: interaction.channel.id,
    setupBy: interaction.user.id,
    setupAt: Date.now()
  };

  automodSettings.set(guildId, settings);

  const embed = new EmbedBuilder()
    .setColor(enabled ? 0x00ff00 : 0xff0000)
    .setTitle('🛡️ Automod Configuration')
    .setDescription(`Automod has been ${enabled ? 'enabled' : 'disabled'} for this server`)
    .addFields(
      { name: '🔄 Spam Protection', value: spamProtection ? '✅ Enabled' : '❌ Disabled', inline: true },
      { name: '📢 Caps Protection', value: capsProtection ? '✅ Enabled' : '❌ Disabled', inline: true },
      { name: '🔗 Link Protection', value: linkProtection ? '✅ Enabled' : '❌ Disabled', inline: true },
      { name: '👥 Mention Protection', value: mentionProtection ? '✅ Enabled' : '❌ Disabled', inline: true },
      { name: '📋 Log Channel', value: `<#${interaction.channel.id}>`, inline: true }
    )
    .setTimestamp();

  await interaction.reply({ embeds: [embed] });
}

async function handleStatus(interaction, guildId) {
  const settings = automodSettings.get(guildId);

  if (!settings) {
    await interaction.reply({
      content: '❌ Automod is not configured for this server. Use `/automod setup` to configure it.',
      ephemeral: true
    });
    return;
  }

  const embed = new EmbedBuilder()
    .setColor(settings.enabled ? 0x00ff00 : 0xff0000)
    .setTitle('🛡️ Automod Status')
    .setDescription(`Server: **${interaction.guild.name}**`)
    .addFields(
      { name: '🔄 Status', value: settings.enabled ? '✅ Active' : '❌ Inactive', inline: true },
      { name: '🔄 Spam Protection', value: settings.spamProtection ? '✅ Enabled' : '❌ Disabled', inline: true },
      { name: '📢 Caps Protection', value: settings.capsProtection ? '✅ Enabled' : '❌ Disabled', inline: true },
      { name: '🔗 Link Protection', value: settings.linkProtection ? '✅ Enabled' : '❌ Disabled', inline: true },
      { name: '👥 Mention Protection', value: settings.mentionProtection ? '✅ Enabled' : '❌ Disabled', inline: true },
      { name: '📋 Log Channel', value: `<#${settings.logChannel}>`, inline: true },
      { name: '⚙️ Configured By', value: `<@${settings.setupBy}>`, inline: true },
      { name: '📅 Setup Date', value: `<t:${Math.floor(settings.setupAt / 1000)}:F>`, inline: true }
    )
    .setTimestamp();

  await interaction.reply({ embeds: [embed] });
}

async function handleWarnings(interaction, guildId) {
  const targetUser = interaction.options.getUser('user') || interaction.user;
  const warnings = getUserWarnings(guildId, targetUser.id);

  const embed = new EmbedBuilder()
    .setColor(0xffa500)
    .setTitle('⚠️ User Warnings')
    .setDescription(`**${targetUser.username}**'s warning history`);

  if (warnings.length === 0) {
    embed.addFields({ name: '📋 Warnings', value: '✅ No warnings on record' });
  } else {
    const warningsText = warnings.map((warning, index) => {
      const timeAgo = `<t:${Math.floor(warning.timestamp / 1000)}:R>`;
      return `${index + 1}. **${warning.reason}** - ${timeAgo}`;
    }).join('\n');

    embed.addFields(
      { name: '📋 Warnings', value: warningsText },
      { name: '⚠️ Total Warnings', value: warnings.length.toString(), inline: true },
      { name: '🚫 Status', value: warnings.length >= AUTOMOD_CONFIG.MAX_WARNINGS ? '🔴 Muted' : '🟡 Active', inline: true }
    );
  }

  await interaction.reply({ embeds: [embed] });
}

async function handleClear(interaction, guildId) {
  const targetUser = interaction.options.getUser('user');
  const warnings = getUserWarnings(guildId, targetUser.id);

  if (warnings.length === 0) {
    await interaction.reply({
      content: `✅ **${targetUser.username}** has no warnings to clear.`,
      ephemeral: true
    });
    return;
  }

  // Clear warnings
  const key = `${guildId}-${targetUser.id}`;
  userWarnings.delete(key);

  const embed = new EmbedBuilder()
    .setColor(0x00ff00)
    .setTitle('✅ Warnings Cleared')
    .setDescription(`Cleared **${warnings.length}** warnings for **${targetUser.username}**`)
    .setTimestamp();

  await interaction.reply({ embeds: [embed] });
}

function getUserWarnings(guildId, userId) {
  const key = `${guildId}-${userId}`;
  const warnings = userWarnings.get(key) || [];
  
  // Filter out expired warnings
  const now = Date.now();
  const validWarnings = warnings.filter(warning => now - warning.timestamp < AUTOMOD_CONFIG.WARNING_EXPIRY);
  
  if (validWarnings.length !== warnings.length) {
    userWarnings.set(key, validWarnings);
  }
  
  return validWarnings;
}

// Function to add warning (called from message handler)
export function addWarning(guildId, userId, reason, moderatorId) {
  const warnings = getUserWarnings(guildId, userId);
  const newWarning = {
    reason,
    moderatorId,
    timestamp: Date.now()
  };
  
  warnings.push(newWarning);
  const key = `${guildId}-${userId}`;
  userWarnings.set(key, warnings);
  
  logger.info('Warning added', {
    guildId,
    userId,
    reason,
    moderatorId,
    totalWarnings: warnings.length
  });
  
  return {
    totalWarnings: warnings.length,
    isMuted: warnings.length >= AUTOMOD_CONFIG.MAX_WARNINGS
  };
}

// Function to check message for violations
export function checkMessage(guildId, message) {
  const settings = automodSettings.get(guildId);
  if (!settings || !settings.enabled) return null;

  const violations = [];

  // Check for spam
  if (settings.spamProtection) {
    // This would need to be implemented with message history tracking
    // For now, just a placeholder
  }

  // Check for excessive caps
  if (settings.capsProtection) {
    const text = message.content;
    const capsCount = (text.match(/[A-Z]/g) || []).length;
    const totalLetters = (text.match(/[A-Za-z]/g) || []).length;
    
    if (totalLetters > 10 && capsCount / totalLetters > AUTOMOD_CONFIG.CAPS_THRESHOLD) {
      violations.push('excessive_caps');
    }
  }

  // Check for unauthorized links
  if (settings.linkProtection) {
    const urlRegex = /https?:\/\/[^\s]+/g;
    const urls = message.content.match(urlRegex) || [];
    
    for (const url of urls) {
      const domain = new URL(url).hostname.toLowerCase();
      const isWhitelisted = AUTOMOD_CONFIG.LINK_WHITELIST.some(whitelist => 
        domain.includes(whitelist)
      );
      
      if (!isWhitelisted) {
        violations.push('unauthorized_link');
        break;
      }
    }
  }

  // Check for mention spam
  if (settings.mentionProtection) {
    const mentionCount = (message.content.match(/<@!?\d+>/g) || []).length;
    if (mentionCount > 5) {
      violations.push('mention_spam');
    }
  }

  return violations.length > 0 ? violations : null;
}

// Function to get automod settings
export function getAutomodSettings(guildId) {
  return automodSettings.get(guildId);
} 