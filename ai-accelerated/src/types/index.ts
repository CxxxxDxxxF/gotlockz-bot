import { SlashCommandBuilder, CommandInteraction } from 'discord.js';

// Discord Command Types
export interface DiscordCommand {
  data: SlashCommandBuilder;
  execute: (interaction: CommandInteraction, client?: any) => Promise<void>;
}

// Tesseract OCR Types
export interface TesseractWord {
  text: string;
  confidence: number;
  bbox: {
    x0: number;
    y0: number;
    x1: number;
    y1: number;
  };
}

export interface TesseractData {
  words: TesseractWord[];
  text: string;
  confidence: number;
  lines: Array<{
    text: string;
    bbox: { x0: number; y0: number; x1: number; y1: number };
    confidence: number;
  }>;
}

// Betting Data Types
export interface BetLeg {
  gameId: string;
  teamA: string;
  teamB: string;
  odds: number;
}

export interface BetSlip {
  legs: BetLeg[];
  units: number;
  type: 'SINGLE' | 'PARLAY';
}

// Game Data Types - Aligned with GameStats from mlbService
export interface GameData {
  gameId: string;
  date: string;
  teams: [string, string];
  score: string;
  status: 'scheduled' | 'live' | 'final';
  startTime?: string;
  venue?: string;
  weather?: WeatherData;
  keyStats?: {
    homeTeam: {
      batting_avg: string;
      runs: string;
      hits: string;
      home_runs: string;
      rbis: string;
      era: string;
      wins: string;
      losses: string;
      saves: string;
      strikeouts: string;
    };
    awayTeam: {
      batting_avg: string;
      runs: string;
      hits: string;
      home_runs: string;
      rbis: string;
      era: string;
      wins: string;
      losses: string;
      saves: string;
      strikeouts: string;
    };
  };
}

export interface WeatherData {
  temperature: number;
  condition: string;
  windSpeed: number;
  humidity: number;
}

// VIP Play Types
export interface VIPPlayMessage {
  channel: 'vip_plays';
  timestamp: string;
  playNumber: number;
  game: {
    away: string;
    home: string;
    startTime: string;
  };
  bet: {
    selection: string;
    market: string;
    odds: number;
    unitSize: number;
  };
  analysis: string;
  assets?: {
    imageUrl?: string;
  };
}

export interface VIPPlayCounter {
  date: string;
  count: number;
  lastReset: string;
}

// Analysis Types
export interface AnalysisRequest {
  betSlip: BetSlip;
  gameData: GameData;
  weather?: WeatherData;
}

export interface AnalysisResponse {
  analysis: string;
  confidence: number;
  factors: string[];
}

// OCR Result Types
export interface OCRResult {
  lines: string[];
  confidence: number;
  usedFallback: boolean;
}

// Environment Types
export interface EnvironmentConfig {
  DISCORD_BOT_TOKEN: string;
  DISCORD_CLIENT_ID?: string;
  DISCORD_GUILD_ID?: string;
  OPENAI_API_KEY?: string;
  GOOGLE_APPLICATION_CREDENTIALS?: string;
  OCR_SPACE_API_KEY?: string;
  OPENWEATHER_API_KEY?: string;
  NODE_ENV: string;
  LOG_LEVEL: string;
}

// Legacy types for backward compatibility
export interface FreePlayMessage {
  channel: 'free_plays';
  timestamp: string;
  playNumber: number;
  game: {
    away: string;
    home: string;
    startTime: string;
  };
  bet: {
    selection: string;
    market: string;
    odds: number;
    unitSize: number;
  };
  analysis: string;
  assets?: {
    imageUrl?: string;
  };
}

export interface LottoTicketMessage {
  channel: 'lotto_ticket';
  timestamp: string;
  ticketNumber: number;
  game: {
    away: string;
    home: string;
    startTime: string;
  };
  bet: {
    selection: string;
    market: string;
    odds: number;
    unitSize: number;
  };
  analysis: string;
  notes?: string;
  assets?: {
    imageUrl?: string;
  };
}

/**
 * Union type for all message types
 */
export type BettingMessage = VIPPlayMessage | FreePlayMessage | LottoTicketMessage; 