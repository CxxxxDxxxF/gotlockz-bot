import OpenAI from 'openai';
import { getEnv } from '../utils/env';
import { BetSlip, GameData } from '../types';

/**
 * Generate AI analysis for a bet slip
 */
export async function generateAnalysis(
  betSlip: BetSlip,
  gameData: GameData,
  weather?: any
): Promise<string> {
  const { OPENAI_API_KEY } = getEnv();
  
  if (!OPENAI_API_KEY) {
    return "⚠️ AI analysis unavailable - OpenAI API key not configured.";
  }

  try {
    const openai = new OpenAI({ apiKey: OPENAI_API_KEY });
    const prompt = buildPrompt(betSlip, gameData, weather);
    
    const completion = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [{ role: "user", content: prompt }],
      max_tokens: 500,
      temperature: 0.7,
    });

    return completion.choices[0]?.message?.content || "❌ Failed to generate analysis.";
  } catch (error) {
    console.error('OpenAI API error:', error);
    return "❌ AI analysis failed. Please try again later.";
  }
}

/**
 * Build analysis prompt for OpenAI
 */
export function buildPrompt(
  betSlip: BetSlip,
  gameData: GameData,
  weather?: any
): string {
  const firstLeg = betSlip.legs[0];
  if (!firstLeg) {
    return "❌ No bet legs found in slip.";
  }
  
  const weatherInfo = weather ? `\nWeather: ${weather.temperature}°F, ${weather.condition}` : '';
  
  return `Analyze this MLB betting pick:

Game: ${gameData.teams[0]} vs ${gameData.teams[1]}
Bet: ${firstLeg.teamA} ${firstLeg.odds > 0 ? '+' : ''}${firstLeg.odds}
Units: ${betSlip.units}${weatherInfo}

Provide a concise, professional analysis focusing on:
1. Key factors supporting this pick
2. Potential risks
3. Confidence level

Keep it under 200 words and use a confident but measured tone.`;
} 