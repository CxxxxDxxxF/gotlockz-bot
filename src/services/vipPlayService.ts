/**
 * VIP Play Service - Structured betting analysis output
 */
import {
  VIPPlayMessage,
  VIPPlayCounter,
  BetSlip,
  GameData
} from '../types';
import { EmbedBuilder } from 'discord.js';

// In-memory counter (in production, use Redis or database)
let playCounter: VIPPlayCounter = {
  date: new Date().toISOString().split('T')[0] ?? '',
  count: 0,
  lastReset: new Date().toISOString()
};

/**
 * Create a VIP Play message from bet slip and analysis data
 */
export async function createVIPPlayMessage(
  betSlip: BetSlip,
  gameData: GameData,
  analysis: string,
  imageUrl?: string
): Promise<VIPPlayMessage | string> {
  // Safe fallback for empty bet legs
  if (!betSlip.legs || betSlip.legs.length === 0) {
    return "❌ Couldn't find any valid bet legs on this slip. Please upload a clearer version.";
  }

  const firstLeg = betSlip.legs[0];
  if (!firstLeg) {
    return "❌ Invalid bet slip structure.";
  }

  if (!gameData.teams || gameData.teams.length < 2) {
    return "❌ Invalid game data - missing team information.";
  }

  // Increment play counter
  playCounter.count += 1;
  
  // Your normal VIPPlayMessage creation logic here
  const now = new Date().toISOString();
  const playNumber = playCounter.count;
  const selection = firstLeg.teamA;
  const market = `${firstLeg.teamA} vs ${firstLeg.teamB}`;
  const odds = firstLeg.odds > 0 ? firstLeg.odds : -Math.abs(firstLeg.odds);

  const vipMessage: VIPPlayMessage = {
    channel: 'vip_plays',
    timestamp: now,
    playNumber,
    game: {
      away: gameData.teams[0] || 'TBD',
      home: gameData.teams[1] || 'TBD',
      startTime: gameData.date + 'T19:00:00Z'
    },
    bet: {
      selection,
      market,
      odds,
      unitSize: betSlip.units
    },
    analysis,
    ...(imageUrl ? { assets: { imageUrl } } : {})
  };

  return vipMessage;
}

/**
 * Validate VIP Play message against schema
 */
export function validateVIPPlayMessage(message: VIPPlayMessage): boolean {
  // Basic validation checks
  if (message.channel !== 'vip_plays') return false;
  if (message.playNumber < 1) return false;
  if (!message.game.away || !message.game.home) return false;
  if (!message.bet.selection || !message.bet.market) return false;
  if (typeof message.bet.odds !== 'number') return false;
  if (typeof message.bet.unitSize !== 'number' || message.bet.unitSize <= 0) return false;
  if (!message.analysis || message.analysis.trim().length === 0) return false;
  
  // Validate ISO date-time formats
  try {
    new Date(message.timestamp);
    new Date(message.game.startTime);
  } catch {
    return false;
  }
  
  return true;
}

/**
 * Format VIP Play message for Discord embed
 */
export function formatVIPPlayForDiscord(message: VIPPlayMessage): EmbedBuilder {
  const embed = new EmbedBuilder()
    .setTitle(`🎯 VIP Play #${message.playNumber}`)
    .setDescription(message.analysis)
    .setColor(0x00ff00) // Green for VIP plays
    .addFields([
      {
        name: '🏟️ Game',
        value: `${message.game.away} @ ${message.game.home}`,
        inline: true
      },
      {
        name: '⏰ Start Time',
        value: new Date(message.game.startTime).toLocaleString(),
        inline: true
      },
      {
        name: '🎲 Bet',
        value: `${message.bet.selection} - ${message.bet.market}`,
        inline: true
      },
      {
        name: '💰 Odds',
        value: message.bet.odds > 0 ? `+${message.bet.odds}` : message.bet.odds.toString(),
        inline: true
      },
      {
        name: '📊 Units',
        value: message.bet.unitSize.toString(),
        inline: true
      }
    ])
    .setTimestamp(new Date(message.timestamp))
    .setFooter({ text: `GotLockz Family • VIP Play #${message.playNumber}` });
  
  if (message.assets?.imageUrl) {
    embed.setImage(message.assets.imageUrl);
  }
  
  return embed;
}

/**
 * Get current play counter stats
 */
export function getPlayCounterStats(): VIPPlayCounter {
  return { ...playCounter };
}

/**
 * Reset play counter (for testing purposes)
 */
export function resetPlayCounter(): void {
  playCounter = {
    date: new Date().toISOString().split('T')[0] ?? '',
    count: 0,
    lastReset: new Date().toISOString()
  };
} 