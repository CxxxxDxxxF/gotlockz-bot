import { SlashCommandBuilder, CommandInteraction } from 'discord.js';

// Command types
export interface CommandConfig {
  name: string;
  description: string;
  options?: CommandOption[];
}

export interface CommandOption {
  name: string;
  description: string;
  type: 'STRING' | 'INTEGER' | 'BOOLEAN' | 'USER' | 'CHANNEL' | 'ROLE' | 'MENTIONABLE' | 'NUMBER' | 'ATTACHMENT' | 'SUB_COMMAND';
  required?: boolean;
  choices?: Array<{ name: string; value: string | number }>;
}

export interface Command {
  data: SlashCommandBuilder;
  execute: (interaction: CommandInteraction) => Promise<void>;
}

// Service types
export interface OCRResult {
  text: string;
  confidence: number;
  lines: Array<{
    text: string;
    confidence: number;
    bbox: { x0: number; y0: number; x1: number; y1: number };
  }>;
}

export interface BettingData {
  teams: string[];
  bet_type: string;
  odds: string;
  stake: string;
  potential_win: string;
  confidence: number;
}

export interface MLBTeam {
  id: number;
  name: string;
  abbreviation: string;
  city: string;
}

export interface MLBStats {
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
}

export interface WeatherData {
  temperature: number;
  humidity: number;
  wind_speed: number;
  description: string;
  city: string;
}

export interface GameData {
  team1: {
    name: string;
    stats: MLBStats;
    weather: WeatherData;
  };
  team2: {
    name: string;
    stats: MLBStats;
    weather: WeatherData;
  };
  live_game?: {
    game_id: number;
    away_team: string;
    home_team: string;
    away_score: number;
    home_score: number;
    status: string;
  };
  fetch_time: number;
}

// Configuration types
export interface FeaturesConfig {
  features: {
    ocr: {
      enabled: boolean;
      engine: string;
      languages: string[];
      confidence_threshold: number;
    };
    mlb: {
      enabled: boolean;
      api_base: string;
      cache_timeout: number;
      rate_limit: {
        max_requests: number;
        interval_ms: number;
      };
    };
    weather: {
      enabled: boolean;
      api_key_env: string;
      cache_timeout: number;
    };
    ai_analysis: {
      enabled: boolean;
      model: string;
      max_tokens: number;
      temperature: number;
    };
    system_monitoring: {
      enabled: boolean;
      interval_seconds: number;
      thresholds: {
        cpu_percent: number;
        memory_percent: number;
        disk_percent: number;
      };
    };
  };
  channels: {
    free_play: {
      enabled: boolean;
      template: string;
    };
    vip: {
      enabled: boolean;
      template: string;
    };
    lotto: {
      enabled: boolean;
      template: string;
    };
  };
}

// Environment types
export interface Environment {
  DISCORD_TOKEN: string;
  DISCORD_CLIENT_ID: string;
  OPENAI_API_KEY: string;
  OPENWEATHER_API_KEY?: string;
  NODE_ENV: 'development' | 'production' | 'test';
  LOG_LEVEL: 'debug' | 'info' | 'warn' | 'error';
}

// System monitoring types
export interface SystemMetrics {
  cpu_percent: number;
  memory_percent: number;
  memory_used_gb: number;
  memory_total_gb: number;
  disk_usage_percent: number;
  temperature_celsius?: number;
  timestamp: Date;
}

export interface SystemStatus {
  healthy: boolean;
  warnings: string[];
  criticals: string[];
  metrics: SystemMetrics;
}

/**
 * VIP Play Message Schema
 * Structured format for betting analysis output
 */
export interface VIPPlayMessage {
  channel: 'vip_plays';
  timestamp: string; // ISO 8601 date-time
  playNumber: number; // Sequential VIP play number for the day
  game: {
    away: string;
    home: string;
    startTime: string; // ISO 8601 date-time
  };
  bet: {
    selection: string; // Player or team picked
    market: string; // Bet description (e.g. "Under 1.5 ER")
    odds: number; // Signed odds, e.g. -140 or +347
    unitSize: number; // Units staked, e.g. 10.5
  };
  analysis: string; // Full multi-paragraph hype-driven analysis text
  assets?: {
    imageUrl?: string; // URL or attachment ID of the bet-slip image
  };
}

/**
 * VIP Play Counter for tracking daily play numbers
 */
export interface VIPPlayCounter {
  date: string; // YYYY-MM-DD format
  count: number;
  lastReset: string; // ISO 8601 timestamp
}

/**
 * Free Play Message Schema
 * Structured format for free play betting analysis output
 */
export interface FreePlayMessage {
  channel: 'free_plays';
  timestamp: string; // ISO 8601 date-time
  playType: 'FREE_PLAY';
  game: {
    away: string;
    home: string;
    startTime: string; // ISO 8601 date-time
  };
  bet: {
    selection: string; // Player or team picked
    market: string; // Bet description (e.g. "Under 1.5 ER")
    odds: number; // Signed odds, e.g. -140 or +347
  };
  analysis: string; // Full multi-paragraph hype-driven analysis text
  assets?: {
    imageUrl?: string; // URL or attachment ID of the bet-slip image
  };
}

/**
 * Lotto Ticket Message Schema
 * Structured format for parlay/lotto ticket betting analysis output
 */
export interface LottoTicketMessage {
  channel: 'lotto_ticket';
  timestamp: string; // ISO 8601 date-time
  ticketType: 'LOTTO_TICKET';
  games: Array<{
    away: string;
    home: string;
    startTime: string; // ISO 8601 date-time
  }>;
  legs: Array<{
    selection: string; // Player or team picked
    market: string; // Bet description
    odds: number; // Signed odds
  }>;
  parlayOdds: number; // Combined parlay odds
  notes?: string; // Optional notes about the ticket
  analysis: string; // Full multi-paragraph hype-driven analysis text
  assets?: {
    imageUrl?: string; // URL or attachment ID of the bet-slip image
  };
}

/**
 * Union type for all message types
 */
export type BettingMessage = VIPPlayMessage | FreePlayMessage | LottoTicketMessage; 