/**
 * Betting Message Service - Create structured betting messages
 */
import { EmbedBuilder } from 'discord.js';
import { 
  VIPPlayMessage, 
  FreePlayMessage, 
  LottoTicketMessage, 
  BetSlip, 
  GameData,
  BettingMessage,
  VIPPlayCounter 
} from '../types';

// In-memory counters (in production, use Redis or database)
let vipPlayCounter = 1;
let freePlayCounter = 1;
let lottoTicketCounter = 1;

/**
 * Get next VIP play number
 */
function getNextVIPPlayNumber(): number {
  return vipPlayCounter++;
}

/**
 * Get next Free play number
 */
function getNextFreePlayNumber(): number {
  return freePlayCounter++;
}

/**
 * Get next Lotto ticket number
 */
function getNextLottoTicketNumber(): number {
  return lottoTicketCounter++;
}

/**
 * Create a VIP Play message
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
  const playNumber = getNextVIPPlayNumber();
  
  // Create VIP Play message
  const now = new Date().toISOString();
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
      startTime: gameData.startTime || gameData.date + 'T19:00:00Z'
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
 * Create a Free Play message
 */
export async function createFreePlayMessage(
  betSlip: BetSlip,
  gameData: GameData,
  analysis: string,
  imageUrl?: string
): Promise<FreePlayMessage> {
  const now = new Date().toISOString();
  
  if (betSlip.legs.length === 0) {
    throw new Error('Free play must have at least 1 leg');
  }
  
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
    playNumber: getNextFreePlayNumber(),
    game: {
      away: gameData.teams[0],
      home: gameData.teams[1],
      startTime: gameData.startTime || gameData.date + 'T19:00:00Z'
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
  
  return freePlayMessage;
}

/**
 * Create a Lotto Ticket message
 */
export async function createLottoTicketMessage(
  betSlip: BetSlip,
  gameData: GameData,
  analysis: string,
  imageUrl?: string,
  notes?: string
): Promise<LottoTicketMessage> {
  const now = new Date().toISOString();
  
  if (betSlip.legs.length < 2) {
    throw new Error('Lotto ticket must have at least 2 legs');
  }
  
  // Calculate parlay odds (simplified calculation)
  const parlayOdds = betSlip.legs.reduce((total, leg) => {
    const odds = leg.odds > 0 ? leg.odds : -Math.abs(leg.odds);
    return total + odds;
  }, 0);
  
  const firstLeg = betSlip.legs[0];
  if (!firstLeg) {
    throw new Error('Invalid bet slip structure');
  }
  
  // Create Lotto Ticket message
  const lottoMessage: LottoTicketMessage = {
    channel: 'lotto_ticket',
    timestamp: now,
    ticketNumber: getNextLottoTicketNumber(),
    game: {
      away: firstLeg.teamA,
      home: firstLeg.teamB,
      startTime: gameData.startTime || gameData.date + 'T19:00:00Z'
    },
    bet: {
      selection: firstLeg.teamA,
      market: `${firstLeg.teamA} vs ${firstLeg.teamB}`,
      odds: parlayOdds,
      unitSize: betSlip.units
    },
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
 * Validate Lotto Ticket message
 */
function validateLottoTicketMessage(message: LottoTicketMessage): boolean {
  if (message.channel !== 'lotto_ticket') return false;
  if (message.ticketNumber < 1) return false;
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
function formatVIPPlayForDiscord(message: VIPPlayMessage): EmbedBuilder {
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
 * Format Free Play message for Discord embed
 */
function formatFreePlayForDiscord(message: FreePlayMessage): EmbedBuilder {
  const embed = new EmbedBuilder()
    .setTitle('🎁 Free Play is Here!')
    .setDescription(message.analysis)
    .setColor(0x0099ff) // Blue for free plays
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
      }
    ])
    .setTimestamp(new Date(message.timestamp))
    .setFooter({ text: 'GotLockz Family • Free Play' });
  
  if (message.assets?.imageUrl) {
    embed.setImage(message.assets.imageUrl);
  }
  
  return embed;
}

/**
 * Format Lotto Ticket message for Discord embed
 */
function formatLottoTicketForDiscord(message: LottoTicketMessage): EmbedBuilder {
  const embed = new EmbedBuilder()
    .setTitle('🎰 Lotto Ticket Alert!')
    .setDescription(message.analysis)
    .setColor(0xff6600) // Orange for lotto tickets
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
    .setFooter({ text: 'GotLockz Family • Lotto Ticket' });
  
  if (message.notes) {
    embed.addFields({
      name: '📝 Notes',
      value: message.notes,
      inline: false
    });
  }
  
  if (message.assets?.imageUrl) {
    embed.setImage(message.assets.imageUrl);
  }
  
  return embed;
}

/**
 * Get current VIP play counter stats
 */
export function getVIPPlayCounterStats(): VIPPlayCounter {
  return {
    date: new Date().toISOString().split('T')[0] || '',
    count: vipPlayCounter - 1,
    lastReset: new Date().toISOString()
  };
}

/**
 * Fallback generic betting message builder
 */
export function createBettingMessage(betLegs: any[], slipData: any): string {
  // ✅ Safe fallback if no bet legs found
  if (!betLegs || betLegs.length === 0) {
    console.warn('No bet legs found in slip:', slipData);
    return "❌ Couldn't find any valid bet legs on this slip.\nPlease double-check the image or upload a clearer version.";
  }

  let message = "✅ **GotLockz Betting Play**\n\n";

  betLegs.forEach((leg, idx) => {
    message += `**Leg ${idx + 1}:** ${leg.description}\nOdds: ${leg.odds}\n\n`;
  });

  if (slipData) {
    message += `📌 Slip Info: ${JSON.stringify(slipData)}`;
  }

  return message;
} 