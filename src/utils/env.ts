export function getEnv() {
  const DISCORD_BOT_TOKEN = process.env['DISCORD_BOT_TOKEN'];
  const OPENAI_API_KEY = process.env['OPENAI_API_KEY'];
  const OCR_SPACE_API_KEY = process.env['OCR_SPACE_API_KEY'];
  
  if (!DISCORD_BOT_TOKEN) throw new Error('Missing DISCORD_BOT_TOKEN');
  if (!OPENAI_API_KEY) throw new Error('Missing OPENAI_API_KEY');
  
  return { DISCORD_BOT_TOKEN, OPENAI_API_KEY, OCR_SPACE_API_KEY };
} 