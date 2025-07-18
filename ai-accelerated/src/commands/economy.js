import { SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } from 'discord.js';
import { logger } from '../utils/logger.js';

// In-memory economy storage (replace with database in production)
const userEconomy = new Map();
const dailyCooldowns = new Map();

// Economy configuration
const ECONOMY_CONFIG = {
  STARTING_BALANCE: 1000,
  DAILY_REWARD: 100,
  DAILY_COOLDOWN: 24 * 60 * 60 * 1000, // 24 hours
  BETTING_MIN: 10,
  BETTING_MAX: 10000
};

export const data = new SlashCommandBuilder()
  .setName('economy')
  .setDescription('Manage your GotLockz economy')
  .addSubcommand(subcommand =>
    subcommand
      .setName('balance')
      .setDescription('Check your balance'))
  .addSubcommand(subcommand =>
    subcommand
      .setName('daily')
      .setDescription('Claim your daily reward'))
  .addSubcommand(subcommand =>
    subcommand
      .setName('bet')
      .setDescription('Place a bet on a pick')
      .addIntegerOption(option =>
        option.setName('amount')
          .setDescription('Amount to bet')
          .setRequired(true)
          .setMinValue(ECONOMY_CONFIG.BETTING_MIN)
          .setMaxValue(ECONOMY_CONFIG.BETTING_MAX))
      .addStringOption(option =>
        option.setName('pick_id')
          .setDescription('ID of the pick to bet on')
          .setRequired(true)))
  .addSubcommand(subcommand =>
    subcommand
      .setName('leaderboard')
      .setDescription('View the richest users'))
  .addSubcommand(subcommand =>
    subcommand
      .setName('transfer')
      .setDescription('Transfer money to another user')
      .addUserOption(option =>
        option.setName('user')
          .setDescription('User to transfer to')
          .setRequired(true))
      .addIntegerOption(option =>
        option.setName('amount')
          .setDescription('Amount to transfer')
          .setRequired(true)
          .setMinValue(1)));

export async function execute(interaction) {
  const subcommand = interaction.options.getSubcommand();
  const userId = interaction.user.id;

  try {
    switch (subcommand) {
    case 'balance': {
      await handleBalance(interaction, userId);
      break;
    }

    case 'daily': {
      await handleDaily(interaction, userId);
      break;
    }

    case 'bet': {
      await handleBet(interaction, userId);
      break;
    }

    case 'leaderboard': {
      await handleLeaderboard(interaction);
      break;
    }

    case 'transfer': {
      await handleTransfer(interaction, userId);
      break;
    }

    default: {
      await interaction.reply('❌ Unknown subcommand.');
    }
    }
  } catch (error) {
    logger.error('Economy command failed:', error);
    await interaction.reply({
      content: '❌ An error occurred while processing your request.',
      ephemeral: true
    });
  }
}

async function handleBalance(interaction, userId) {
  const userData = getUserData(userId);
  
  const embed = new EmbedBuilder()
    .setColor(0x00ff00)
    .setTitle('💰 Your Balance')
    .setDescription(`**${interaction.user.username}**'s GotLockz Economy`)
    .addFields(
      { name: '💵 Balance', value: `$${userData.balance.toLocaleString()}`, inline: true },
      { name: '📈 Total Won', value: `$${userData.totalWon.toLocaleString()}`, inline: true },
      { name: '📉 Total Lost', value: `$${userData.totalLost.toLocaleString()}`, inline: true },
      { name: '🎯 Win Rate', value: `${userData.winRate}%`, inline: true },
      { name: '🏆 Best Win', value: `$${userData.bestWin.toLocaleString()}`, inline: true },
      { name: '📊 Bets Placed', value: userData.betsPlaced.toString(), inline: true }
    )
    .setTimestamp()
    .setFooter({ text: 'GotLockz Economy System' });

  await interaction.reply({ embeds: [embed] });
}

async function handleDaily(interaction, userId) {
  const lastDaily = dailyCooldowns.get(userId) || 0;
  const now = Date.now();
  const timeRemaining = ECONOMY_CONFIG.DAILY_COOLDOWN - (now - lastDaily);

  if (timeRemaining > 0) {
    const hours = Math.floor(timeRemaining / (60 * 60 * 1000));
    const minutes = Math.floor((timeRemaining % (60 * 60 * 1000)) / (60 * 1000));
    
    await interaction.reply({
      content: `⏰ You can claim your daily reward in **${hours}h ${minutes}m**`,
      ephemeral: true
    });
    return;
  }

  const userData = getUserData(userId);
  userData.balance += ECONOMY_CONFIG.DAILY_REWARD;
  dailyCooldowns.set(userId, now);

  const embed = new EmbedBuilder()
    .setColor(0x00ff00)
    .setTitle('🎁 Daily Reward Claimed!')
    .setDescription(`You received **$${ECONOMY_CONFIG.DAILY_REWARD}**`)
    .addFields(
      { name: '💰 New Balance', value: `$${userData.balance.toLocaleString()}`, inline: true },
      { name: '⏰ Next Daily', value: '<t:' + Math.floor((now + ECONOMY_CONFIG.DAILY_COOLDOWN) / 1000) + ':R>', inline: true }
    )
    .setTimestamp();

  await interaction.reply({ embeds: [embed] });
}

async function handleBet(interaction, userId) {
  const amount = interaction.options.getInteger('amount');
  const pickId = interaction.options.getString('pick_id');
  const userData = getUserData(userId);

  if (userData.balance < amount) {
    await interaction.reply({
      content: `❌ Insufficient funds! You have $${userData.balance.toLocaleString()} but need $${amount.toLocaleString()}`,
      ephemeral: true
    });
    return;
  }

  // Deduct bet amount
  userData.balance -= amount;
  userData.betsPlaced++;

  const embed = new EmbedBuilder()
    .setColor(0xffa500)
    .setTitle('🎯 Bet Placed!')
    .setDescription(`You bet **$${amount.toLocaleString()}** on pick **${pickId}**`)
    .addFields(
      { name: '💰 Remaining Balance', value: `$${userData.balance.toLocaleString()}`, inline: true },
      { name: '📊 Total Bets', value: userData.betsPlaced.toString(), inline: true }
    )
    .setTimestamp();

  await interaction.reply({ embeds: [embed] });
}

async function handleLeaderboard(interaction) {
  // Get top 10 users by balance
  const sortedUsers = Array.from(userEconomy.entries())
    .sort(([, a], [, b]) => b.balance - a.balance)
    .slice(0, 10);

  const embed = new EmbedBuilder()
    .setColor(0xffd700)
    .setTitle('🏆 GotLockz Economy Leaderboard')
    .setDescription('Top 10 Richest Users')
    .setTimestamp();

  if (sortedUsers.length === 0) {
    embed.addFields({ name: '📊 No Data', value: 'No users have claimed their starting balance yet!' });
  } else {
    const leaderboardText = sortedUsers.map(([userId, data], index) => {
      const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `${index + 1}.`;
      const user = interaction.client.users.cache.get(userId);
      const username = user ? user.username : 'Unknown User';
      return `${medal} **${username}** - $${data.balance.toLocaleString()}`;
    }).join('\n');

    embed.addFields({ name: '💰 Richest Users', value: leaderboardText });
  }

  await interaction.reply({ embeds: [embed] });
}

async function handleTransfer(interaction, userId) {
  const targetUser = interaction.options.getUser('user');
  const amount = interaction.options.getInteger('amount');
  const userData = getUserData(userId);

  if (targetUser.id === userId) {
    await interaction.reply({
      content: '❌ You cannot transfer money to yourself!',
      ephemeral: true
    });
    return;
  }

  if (userData.balance < amount) {
    await interaction.reply({
      content: `❌ Insufficient funds! You have $${userData.balance.toLocaleString()} but need $${amount.toLocaleString()}`,
      ephemeral: true
    });
    return;
  }

  // Transfer money
  userData.balance -= amount;
  const targetData = getUserData(targetUser.id);
  targetData.balance += amount;

  const embed = new EmbedBuilder()
    .setColor(0x00ff00)
    .setTitle('💸 Transfer Successful!')
    .setDescription(`You transferred **$${amount.toLocaleString()}** to **${targetUser.username}**`)
    .addFields(
      { name: '💰 Your New Balance', value: `$${userData.balance.toLocaleString()}`, inline: true },
      { name: '📤 Amount Sent', value: `$${amount.toLocaleString()}`, inline: true }
    )
    .setTimestamp();

  await interaction.reply({ embeds: [embed] });
}

function getUserData(userId) {
  if (!userEconomy.has(userId)) {
    userEconomy.set(userId, {
      balance: ECONOMY_CONFIG.STARTING_BALANCE,
      totalWon: 0,
      totalLost: 0,
      betsPlaced: 0,
      betsWon: 0,
      bestWin: 0,
      winRate: 0
    });
  }
  return userEconomy.get(userId);
}

// Function to process bet results (called when picks are resolved)
export function processBetResult(userId, betAmount, odds, won) {
  const userData = getUserData(userId);
  
  if (won) {
    const winnings = calculateWinnings(betAmount, odds);
    userData.balance += winnings;
    userData.totalWon += winnings;
    userData.betsWon++;
    userData.bestWin = Math.max(userData.bestWin, winnings);
  } else {
    userData.totalLost += betAmount;
  }

  userData.winRate = Math.round((userData.betsWon / userData.betsPlaced) * 100) || 0;
}

function calculateWinnings(betAmount, odds) {
  // Simple odds calculation (can be enhanced)
  if (odds.startsWith('+')) {
    const multiplier = parseInt(odds) / 100;
    return betAmount + (betAmount * multiplier);
  } else if (odds.startsWith('-')) {
    const multiplier = 100 / Math.abs(parseInt(odds));
    return betAmount + (betAmount * multiplier);
  }
  return betAmount; // Even odds
} 