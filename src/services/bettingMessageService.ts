/**
 * Betting Message Service - Unified service for all betting message types
 */
import { 
  VIPPlayMessage, 
  FreePlayMessage, 
  LottoTicketMessage, 
  BettingMessage,
  VIPPlayCounter 
} from '../types';
import { BetSlip } from '../utils/parser';
import { GameStats } from './mlbService';

// In-memory counter for VIP plays (in production, use Redis or database)
let vipPlayCounter: VIPPlayCounter = {
  date: new Date().toISOString().split('T')[0] ?? '',
  count: 0,
  lastReset: new Date().toISOString()
};

/**
 * Get the next VIP play number for today
 */
function getNextVIPPlayNumber(): number {
  const today = new Date().toISOString().split('T')[0] ?? '';
  
  // Reset counter if it's a new day
  if (vipPlayCounter.date !== today) {
    vipPlayCounter = {
      date: today,
      count: 0,
      lastReset: new Date().toISOString()
    };
  }
  
  vipPlayCounter.count++;
  return vipPlayCounter.count;
}

/**
 * Create a VIP Play message
 */
export async function createVIPPlayMessage(
  betSlip: BetSlip,
  gameData: GameStats,
  analysis: string,
  imageUrl?: string
): Promise<VIPPlayMessage | string> {
  const now = new Date().toISOString();
  const playNumber = getNextVIPPlayNumber();
  
  // SAFETY CHECK: If no bet legs, return a friendly message
  if (!betSlip.legs || betSlip.legs.length === 0) {
    console.warn('No bet legs found in slip:', betSlip);
    return '❌ **Couldn't find any valid bet legs on this slip.**\nPlease double-check the image or upload a clearer version.';
  }
  
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
    ...(imageUrl && { assets: { imageUrl } })
  };
  
  return vipMessage;
}

/**
 * Create a Free Play message
 */
export async function createFreePlayMessage(
  betSlip: BetSlip,
  gameData: GameStats,
  analysis: string,
  imageUrl?: string
): Promise<FreePlayMessage> {
  const now = new Date().toISOString();
  
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
  
  // Create Free Play message
  const freePlayMessage: FreePlayMessage = {
    channel: 'free_plays',
    timestamp: now,
    playType: 'FREE_PLAY',
    game: {
      away: gameData.teams[0],
      home: gameData.teams[1],
      startTime: gameData.date + 'T19:00:00Z' // Default game time
    },
    bet: {
      selection,
      market,
      odds
    },
    analysis,
    ...(imageUrl && { assets: { imageUrl } })
  };
  
  return freePlayMessage;
}

/**
 * Create a Lotto Ticket message
 */
export async function createLottoTicketMessage(
  betSlip: BetSlip,
  gameData: GameStats,
  analysis: string,
  imageUrl?: string,
  notes?: string
): Promise<LottoTicketMessage> {
  const now = new Date().toISOString();
  
  if (betSlip.legs.length < 2) {
    throw new Error('Lotto ticket must have at least 2 legs');
  }
  
  // Create games array from legs
  const games = betSlip.legs.map(leg => ({
    away: leg.teamA,
    home: leg.teamB,
    startTime: gameData.date + 'T19:00:00Z' // Default game time
  }));
  
  // Create legs array
  const legs = betSlip.legs.map(leg => ({
    selection: leg.teamA,
    market: `${leg.teamA} vs ${leg.teamB}`,
    odds: leg.odds > 0 ? leg.odds : -Math.abs(leg.odds)
  }));
  
  // Calculate parlay odds (simplified calculation)
  const parlayOdds = betSlip.legs.reduce((total, leg) => {
    const odds = leg.odds > 0 ? leg.odds : -Math.abs(leg.odds);
    return total + odds;
  }, 0);
  
  // Create Lotto Ticket message
  const lottoMessage: LottoTicketMessage = {
    channel: 'lotto_ticket',
    timestamp: now,
    ticketType: 'LOTTO_TICKET',
    games,
    legs,
    parlayOdds,
    analysis,
    ...(notes && { notes }),
    ...(imageUrl && { assets: { imageUrl } })
  };
  
  return lottoMessage;
}

/**
 * Validate any betting message against its schema
 */
export function validateBettingMessage(message: BettingMessage): boolean {
  // Basic validation checks
  if (!message.timestamp || !message.analysis) return false;
  
  // Validate ISO date-time format
  try {
    new Date(message.timestamp);
  } catch {
    return false;
  }
  
  // Type-specific validation
  switch (message.channel) {
    case 'vip_plays':
      return validateVIPPlayMessage(message as VIPPlayMessage);
    case 'free_plays':
      return validateFreePlayMessage(message as FreePlayMessage);
    case 'lotto_ticket':
      return validateLottoTicketMessage(message as LottoTicketMessage);
    default:
      return false;
  }
}

/**
 * Validate VIP Play message
 */
function validateVIPPlayMessage(message: VIPPlayMessage): boolean {
  if (message.channel !== 'vip_plays') return false;
  if (message.playNumber < 1) return false;
  if (!message.game.away || !message.game.home) return false;
  if (!message.bet.selection || !message.bet.market) return false;
  if (typeof message.bet.odds !== 'number') return false;
  if (typeof message.bet.unitSize !== 'number' || message.bet.unitSize <= 0) return false;
  if (!message.analysis || message.analysis.trim().length === 0) return false;
  
  try {
    new Date(message.game.startTime);
  } catch {
    return false;
  }
  
  return true;
}

/**
 * Validate Free Play message
 */
function validateFreePlayMessage(message: FreePlayMessage): boolean {
  if (message.channel !== 'free_plays') return false;
  if (message.playType !== 'FREE_PLAY') return false;
  if (!message.game.away || !message.game.home) return false;
  if (!message.bet.selection || !message.bet.market) return false;
  if (typeof message.bet.odds !== 'number') return false;
  if (!message.analysis || message.analysis.trim().length === 0) return false;
  
  try {
    new Date(message.game.startTime);
  } catch {
    return false;
  }
  
  return true;
}

/**
 * Validate Lotto Ticket message
 */
function validateLottoTicketMessage(message: LottoTicketMessage): boolean {
  if (message.channel !== 'lotto_ticket') return false;
  if (message.ticketType !== 'LOTTO_TICKET') return false;
  if (!Array.isArray(message.games) || message.games.length < 2) return false;
  if (!Array.isArray(message.legs) || message.legs.length < 2) return false;
  if (typeof message.parlayOdds !== 'number') return false;
  if (!message.analysis || message.analysis.trim().length === 0) return false;
  
  // Validate games
  for (const game of message.games) {
    if (!game.away || !game.home) return false;
    try {
      new Date(game.startTime);
    } catch {
      return false;
    }
  }
  
  // Validate legs
  for (const leg of message.legs) {
    if (!leg.selection || !leg.market) return false;
    if (typeof leg.odds !== 'number') return false;
  }
  
  return true;
}

/**
 * Format any betting message for Discord embed
 */
export function formatBettingMessageForDiscord(message: BettingMessage) {
  switch (message.channel) {
    case 'vip_plays':
      return formatVIPPlayForDiscord(message as VIPPlayMessage);
    case 'free_plays':
      return formatFreePlayForDiscord(message as FreePlayMessage);
    case 'lotto_ticket':
      return formatLottoTicketForDiscord(message as LottoTicketMessage);
    default:
      throw new Error(`Unknown message channel: ${(message as any).channel}`);
  }
}

/**
 * Format VIP Play message for Discord embed
 */
function formatVIPPlayForDiscord(message: VIPPlayMessage) {
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
 * Format Free Play message for Discord embed
 */
function formatFreePlayForDiscord(message: FreePlayMessage) {
  const embed: any = {
    title: '🎁 Free Play is Here!',
    description: message.analysis,
    color: 0x0099ff, // Blue for free plays
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
      }
    ],
    timestamp: message.timestamp,
    footer: {
      text: 'GotLockz Family • Free Play'
    }
  };
  
  if (message.assets?.imageUrl) {
    embed.image = { url: message.assets.imageUrl };
  }
  
  return embed;
}

/**
 * Format Lotto Ticket message for Discord embed
 */
function formatLottoTicketForDiscord(message: LottoTicketMessage) {
  const embed: any = {
    title: '🎰 Lotto Ticket Alert!',
    description: message.analysis,
    color: 0xff6600, // Orange for lotto tickets
    fields: [
      {
        name: '🎮 Games',
        value: message.games.map(game => `${game.away} @ ${game.home}`).join('\n'),
        inline: false
      },
      {
        name: '🎲 Legs',
        value: message.legs.map(leg => `${leg.selection} - ${leg.market} (${leg.odds > 0 ? '+' : ''}${leg.odds})`).join('\n'),
        inline: false
      },
      {
        name: '💰 Parlay Odds',
        value: message.parlayOdds > 0 ? `+${message.parlayOdds}` : message.parlayOdds.toString(),
        inline: true
      }
    ],
    timestamp: message.timestamp,
    footer: {
      text: 'GotLockz Family • Lotto Ticket'
    }
  };
  
  if (message.notes) {
    embed.fields.push({
      name: '📝 Notes',
      value: message.notes,
      inline: false
    });
  }
  
  if (message.assets?.imageUrl) {
    embed.image = { url: message.assets.imageUrl };
  }
  
  return embed;
}

/**
 * Get current VIP play counter stats
 */
export function getVIPPlayCounterStats(): VIPPlayCounter {
  return { ...vipPlayCounter };
} 