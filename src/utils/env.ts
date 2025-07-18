export interface Environment {
  DISCORD_BOT_TOKEN: string;
  DISCORD_CLIENT_ID: string;
  DISCORD_GUILD_ID?: string;
  OPENAI_API_KEY: string;
  OPENWEATHER_API_KEY?: string;
  GOOGLE_APPLICATION_CREDENTIALS?: string;
  NODE_ENV: 'development' | 'production' | 'test';
  LOG_LEVEL: 'debug' | 'info' | 'warn' | 'error';
  PORT?: number;
}

export function getEnv(): Environment {
  const env = {
    DISCORD_BOT_TOKEN: process.env['DISCORD_BOT_TOKEN'],
    DISCORD_CLIENT_ID: process.env['DISCORD_CLIENT_ID'],
    DISCORD_GUILD_ID: process.env['DISCORD_GUILD_ID'],
    OPENAI_API_KEY: process.env['OPENAI_API_KEY'],
    OPENWEATHER_API_KEY: process.env['OPENWEATHER_API_KEY'],
    GOOGLE_APPLICATION_CREDENTIALS: process.env['GOOGLE_APPLICATION_CREDENTIALS'],
    NODE_ENV: (process.env['NODE_ENV'] as Environment['NODE_ENV']) || 'development',
    LOG_LEVEL: (process.env['LOG_LEVEL'] as Environment['LOG_LEVEL']) || 'info',
    PORT: process.env['PORT'] ? parseInt(process.env['PORT']) : undefined
  };

  // Validate required environment variables
  const required = ['DISCORD_BOT_TOKEN', 'DISCORD_CLIENT_ID', 'OPENAI_API_KEY'];
  for (const key of required) {
    if (!env[key as keyof Environment]) {
      throw new Error(`Missing required environment variable: ${key}`);
    }
  }

  return env as Environment;
} 