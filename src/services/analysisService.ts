import OpenAI from 'openai';
import { getEnv } from '../utils/env';

const cache = new Map<string, { timestamp: number; text: string }>();

export async function generateAnalysis(
  betSlip: any,
  gameData: any,
  edge: number,
  weather: any
): Promise<string> {
  const key = JSON.stringify({ betSlip, gameData, edge, weather });
  const now = Date.now();
  const entry = cache.get(key);
  if (entry && now - entry.timestamp < 1000 * 60) {
    return entry.text;
  }
  const { OPENAI_API_KEY } = getEnv();
  const client = new OpenAI({ apiKey: OPENAI_API_KEY });
  const prompt = `
  You are a hype-driven sports analyst. Given the following bet slip, game data, edge calculation, and weather, write a persuasive multi-paragraph analysis:
  
  Bet Slip:
  ${JSON.stringify(betSlip, null, 2)}

  Game Data:
  ${JSON.stringify(gameData, null, 2)}

  Calculated Edge: ${edge.toFixed(2)}%

  Weather Data:
  ${JSON.stringify(weather, null, 2)}

  Use current date and maintain a confident, stat-backed, hype tone.
  `;

  const res = await client.chat.completions.create({
    model: 'gpt-4o',
    messages: [{ role: 'system', content: 'You are a sports betting analyst.' },
               { role: 'user', content: prompt }],
    max_tokens: 600,
  });

  const analysis = res.choices[0]?.message?.content?.trim() || '';
  cache.set(key, { timestamp: now, text: analysis });
  return analysis;
}

export function buildPrompt(
  betSlip: any,
  gameData: any,
  edge: number,
  weather: any
): string {
  return `
  You are a hype-driven sports analyst. Given the following bet slip, game data, edge calculation, and weather, write a persuasive multi-paragraph analysis:
  
  Bet Slip:
  ${JSON.stringify(betSlip, null, 2)}

  Game Data:
  ${JSON.stringify(gameData, null, 2)}

  Calculated Edge: ${edge.toFixed(2)}%

  Weather Data:
  ${JSON.stringify(weather, null, 2)}

  Use current date and maintain a confident, stat-backed, hype tone.
  `;
} 