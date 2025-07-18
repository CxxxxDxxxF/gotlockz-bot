import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';
import { logger } from '../utils/logger.js';

// In-memory leveling storage (replace with database in production)
const userLevels = new Map();

// Leveling configuration
const LEVELING_CONFIG = {
  BASE_XP: 100,
  XP_MULTIPLIER: 1.5,
  MAX_LEVEL: 100,
  XP_PER_MESSAGE: 15,
  XP_PER_COMMAND: 25,
  XP_PER_PICK: 50,
  XP_PER_WIN: 100
};

export const data = new SlashCommandBuilder()
  .setName('level')
  .setDescription('View your level and XP')
  .addSubcommand(subcommand =>
    subcommand
      .setName('profile')
      .setDescription('View your level profile'))
  .addSubcommand(subcommand =>
    subcommand
      .setName('leaderboard')
      .setDescription('View the highest level users'))
  .addSubcommand(subcommand =>
    subcommand
      .setName('rewards')
      .setDescription('View available level rewards'));

export async function execute(interaction) {
  const subcommand = interaction.options.getSubcommand();
  const userId = interaction.user.id;

  try {
    switch (subcommand) {
    case 'profile': {
      await handleProfile(interaction, userId);
      break;
    }

    case 'leaderboard': {
      await handleLeaderboard(interaction);
      break;
    }

    case 'rewards': {
      await handleRewards(interaction);
      break;
    }

    default: {
      await interaction.reply('❌ Unknown subcommand.');
    }
    }
  } catch (error) {
    logger.error('Leveling command failed:', error);
    await interaction.reply({
      content: '❌ An error occurred while processing your request.',
      ephemeral: true
    });
  }
}

async function handleProfile(interaction, userId) {
  const userData = getUserLevelData(userId);
  const level = userData.level;
  const currentXP = userData.xp;
  const xpForNextLevel = getXPForLevel(level + 1);
  const xpProgress = currentXP - getXPForLevel(level);
  const xpNeeded = xpForNextLevel - currentXP;
  const progressPercentage = Math.round((xpProgress / (xpForNextLevel - getXPForLevel(level))) * 100);

  // Create progress bar
  const progressBar = createProgressBar(progressPercentage);

  const embed = new EmbedBuilder()
    .setColor(0x0099ff)
    .setTitle('📊 Level Profile')
    .setDescription(`**${interaction.user.username}**'s GotLockz Progress`)
    .addFields(
      { name: '⭐ Level', value: level.toString(), inline: true },
      { name: '📈 Total XP', value: currentXP.toLocaleString(), inline: true },
      { name: '🎯 XP to Next Level', value: xpNeeded.toLocaleString(), inline: true },
      { name: '📊 Progress', value: `${progressBar} ${progressPercentage}%`, inline: false },
      { name: '🏆 Rank', value: getRank(level), inline: true },
      { name: '💬 Messages', value: userData.messages.toString(), inline: true },
      { name: '🎯 Picks Made', value: userData.picksMade.toString(), inline: true },
      { name: '✅ Wins', value: userData.wins.toString(), inline: true },
      { name: '📈 Win Streak', value: userData.currentStreak.toString(), inline: true },
      { name: '🔥 Best Streak', value: userData.bestStreak.toString(), inline: true }
    )
    .setTimestamp()
    .setFooter({ text: 'GotLockz Leveling System' });

  await interaction.reply({ embeds: [embed] });
}

async function handleLeaderboard(interaction) {
  // Get top 10 users by level and XP
  const sortedUsers = Array.from(userLevels.entries())
    .sort(([, a], [, b]) => {
      if (b.level !== a.level) return b.level - a.level;
      return b.xp - a.xp;
    })
    .slice(0, 10);

  const embed = new EmbedBuilder()
    .setColor(0xffd700)
    .setTitle('🏆 GotLockz Level Leaderboard')
    .setDescription('Top 10 Highest Level Users')
    .setTimestamp();

  if (sortedUsers.length === 0) {
    embed.addFields({ name: '📊 No Data', value: 'No users have gained XP yet!' });
  } else {
    const leaderboardText = sortedUsers.map(([userId, data], index) => {
      const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `${index + 1}.`;
      const user = interaction.client.users.cache.get(userId);
      const username = user ? user.username : 'Unknown User';
      const rank = getRank(data.level);
      return `${medal} **${username}** - Level ${data.level} (${rank}) - ${data.xp.toLocaleString()} XP`;
    }).join('\n');

    embed.addFields({ name: '⭐ Top Users', value: leaderboardText });
  }

  await interaction.reply({ embeds: [embed] });
}

async function handleRewards(interaction) {
  const rewards = [
    { level: 5, reward: '🎨 Custom Role Color', description: 'Choose your own role color' },
    { level: 10, reward: '🎭 Custom Nickname', description: 'Set a custom nickname' },
    { level: 15, reward: '💰 +$500 Daily Reward', description: 'Increased daily economy reward' },
    { level: 20, reward: '🎯 VIP Access', description: 'Access to VIP picks and analysis' },
    { level: 25, reward: '🏆 Exclusive Badge', description: 'Special profile badge' },
    { level: 30, reward: '🎁 Mystery Box', description: 'Random reward box' },
    { level: 50, reward: '👑 Legend Status', description: 'Permanent VIP access' },
    { level: 100, reward: '🌟 GotLockz Master', description: 'Ultimate achievement unlocked' }
  ];

  const userData = getUserLevelData(interaction.user.id);
  const userLevel = userData.level;

  const rewardsText = rewards.map(reward => {
    const status = userLevel >= reward.level ? '✅' : '🔒';
    return `${status} **Level ${reward.level}**: ${reward.reward}\n   └ ${reward.description}`;
  }).join('\n\n');

  const embed = new EmbedBuilder()
    .setColor(0x00ff00)
    .setTitle('🎁 Level Rewards')
    .setDescription(`**${interaction.user.username}** - Level ${userLevel}`)
    .addFields(
      { name: '📋 Available Rewards', value: rewardsText },
      { name: '📊 Your Progress', value: `${userLevel}/100 levels completed` }
    )
    .setTimestamp();

  await interaction.reply({ embeds: [embed] });
}

function getUserLevelData(userId) {
  if (!userLevels.has(userId)) {
    userLevels.set(userId, {
      level: 1,
      xp: 0,
      messages: 0,
      picksMade: 0,
      wins: 0,
      currentStreak: 0,
      bestStreak: 0,
      lastMessageTime: 0
    });
  }
  return userLevels.get(userId);
}

function getXPForLevel(level) {
  if (level <= 1) return 0;
  return Math.floor(LEVELING_CONFIG.BASE_XP * Math.pow(LEVELING_CONFIG.XP_MULTIPLIER, level - 2));
}

function createProgressBar(percentage) {
  const filled = Math.floor(percentage / 10);
  const empty = 10 - filled;
  return '█'.repeat(filled) + '░'.repeat(empty);
}

function getRank(level) {
  if (level >= 100) return '🌟 GotLockz Master';
  if (level >= 50) return '👑 Legend';
  if (level >= 30) return '💎 Elite';
  if (level >= 20) return '🏆 Champion';
  if (level >= 15) return '⭐ Veteran';
  if (level >= 10) return '🔥 Pro';
  if (level >= 5) return '📈 Rising Star';
  return '🌱 Rookie';
}

// Function to add XP (called from other commands)
export function addXP(userId, amount, reason = '') {
  const userData = getUserLevelData(userId);
  const oldLevel = userData.level;
  
  userData.xp += amount;
  
  // Check for level up
  while (userData.xp >= getXPForLevel(userData.level + 1) && userData.level < LEVELING_CONFIG.MAX_LEVEL) {
    userData.level++;
  }
  
  const newLevel = userData.level;
  
  logger.info('XP added', {
    userId,
    amount,
    reason,
    oldLevel,
    newLevel,
    totalXP: userData.xp
  });
  
  return {
    leveledUp: newLevel > oldLevel,
    oldLevel,
    newLevel,
    xpGained: amount
  };
}

// Function to add message XP (called from message handler)
export function addMessageXP(userId) {
  const userData = getUserLevelData(userId);
  const now = Date.now();
  const cooldown = 60 * 1000; // 1 minute cooldown
  
  if (now - userData.lastMessageTime < cooldown) {
    return null; // Still in cooldown
  }
  
  userData.lastMessageTime = now;
  userData.messages++;
  
  return addXP(userId, LEVELING_CONFIG.XP_PER_MESSAGE, 'message');
}

// Function to add pick XP (called when picks are made)
export function addPickXP(userId, won = false) {
  const userData = getUserLevelData(userId);
  userData.picksMade++;
  
  if (won) {
    userData.wins++;
    userData.currentStreak++;
    userData.bestStreak = Math.max(userData.bestStreak, userData.currentStreak);
    return addXP(userId, LEVELING_CONFIG.XP_PER_WIN, 'win');
  } else {
    userData.currentStreak = 0;
    return addXP(userId, LEVELING_CONFIG.XP_PER_PICK, 'pick');
  }
} 