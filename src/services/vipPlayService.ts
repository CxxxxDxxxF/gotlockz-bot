/**
 * VIP Play Service - Structured betting analysis output
 */
import { VIPPlayMessage, VIPPlayCounter } from '../types';
import { BetSlip } from '../utils/parser';
import { GameStats } from './mlbService';

// In-memory counter (in production, use Redis or database)
let playCounter: VIPPlayCounter = {
  date: new Date().toISOString().split('T')[0] ?? '',
  count: 0,
  lastReset: new Date().toISOString()
};

/**
 * Get the next VIP play number for today
 */
function getNextPlayNumber(): number {
  const today = new Date().toISOString().split('T')[0] ?? '';
  
  // Reset counter if it's a new day
  if (playCounter.date !== today) {
    playCounter = {
      date: today,
      count: 0,
      lastReset: new Date().toISOString()
    };
  }
  
  playCounter.count++;
  return playCounter.count;
}

/**
 * Create a VIP Play message from bet slip and analysis data
 */
export async function createVIPPlayMessage(
  betSlip: BetSlip,
  gameData: GameStats,
  analysis: string,
  imageUrl?: string
): Promise<VIPPlayMessage> {
  const now = new Date().toISOString();
  const playNumber = getNextPlayNumber();
  
  // Extract bet details from the first leg
  const firstLeg = betSlip.legs[0];
  if (!firstLeg) {
    throw new Error('No bet legs found in slip');
  }
  
  // Determine bet selection and market
  const selection = firstLeg.teamA; // Default to first team
  const market = `${firstLeg.teamA} vs ${firstLeg.teamB}`;
  
  // Format odds with sign
  const odds = firstLeg.odds > 0 ? firstLeg.odds : -Math.abs(firstLeg.odds);
  
  // Create VIP Play message
  const vipMessage: VIPPlayMessage = {
    channel: 'vip_plays',
    timestamp: now,
    playNumber,
    game: {
      away: gameData.teams[0],
      home: gameData.teams[1],
      startTime: gameData.date + 'T19:00:00Z' // Default game time
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
export function formatVIPPlayForDiscord(message: VIPPlayMessage) {
  const embed: any = {
    title: `🎯 VIP Play #${message.playNumber}`,
    description: message.analysis,
    color: 0x00ff00, // Green for VIP plays
    fields: [
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
    ],
    timestamp: message.timestamp,
    footer: {
      text: `GotLockz Family • VIP Play #${message.playNumber}`
    }
  };
  
  if (message.assets?.imageUrl) {
    embed.image = { url: message.assets.imageUrl };
  }
  
  return embed;
}

/**
 * Get current play counter stats
 */
export function getPlayCounterStats(): VIPPlayCounter {
  return { ...playCounter };
} 