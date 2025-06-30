export function getEnv() {
  // Allow either DISCORD_BOT_TOKEN or DISCORD_TOKEN for backwards compatibility
  const DISCORD_BOT_TOKEN = process.env['DISCORD_BOT_TOKEN'] ?? process.env['DISCORD_TOKEN'];
  const { DISCORD_CLIENT_ID, DISCORD_GUILD_ID, OPENAI_API_KEY, OCR_SPACE_API_KEY, GOOGLE_APPLICATION_CREDENTIALS, PORT, OPENWEATHERMAP_KEY } = process.env;
  
  if (!DISCORD_BOT_TOKEN) {
    throw new Error('Missing DISCORD_BOT_TOKEN');
  }
  if (!DISCORD_CLIENT_ID) {
    throw new Error('Missing DISCORD_CLIENT_ID');
  }
  if (!OPENAI_API_KEY) {
    throw new Error('Missing OPENAI_API_KEY');
  }
  
  return {
    DISCORD_BOT_TOKEN,
    DISCORD_CLIENT_ID,
    DISCORD_GUILD_ID,
    OPENAI_API_KEY,
    OCR_SPACE_API_KEY,
    GOOGLE_APPLICATION_CREDENTIALS,
    OPENWEATHERMAP_KEY,
    PORT: PORT ? Number(PORT) : undefined,
  };
} 