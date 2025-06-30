/**
 * Analysis Service Tests
 */

// Hoist the mock before imports
const mockCreate = jest.fn().mockResolvedValue({
  choices: [{ message: { content: 'Mock analysis response' } }]
});

jest.mock('openai', () => {
  return {
    __esModule: true,
    default: jest.fn().mockImplementation(() => ({
      chat: {
        completions: {
          create: mockCreate
        }
      }
    }))
  };
});

// Mock environment
jest.mock('../src/utils/env', () => ({
  getEnv: jest.fn().mockReturnValue({
    OPENAI_API_KEY: 'test-key'
  })
}));

import { generateAnalysis, buildPrompt } from '../src/services/analysisService';
import { BetSlip, GameData } from '../src/types';

describe('Analysis Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockCreate.mockReset();
    mockCreate.mockResolvedValue({
      choices: [{ message: { content: 'Mock analysis response' } }]
    });
  });

  const mockBetSlip: BetSlip = {
    legs: [
      {
        gameId: 'NYM_PHI_20241201',
        teamA: 'NYM',
        teamB: 'PHI',
        odds: -120
      }
    ],
    units: 5,
    type: 'SINGLE'
  };

  const mockGameData: GameData = {
    gameId: 'NYM_PHI_20241201',
    date: '2024-12-01',
    teams: ['NYM', 'PHI'],
    score: '0-0',
    status: 'scheduled',
    startTime: '2024-12-01T19:00:00Z'
  };

  const mockWeather = {
    temperature: 72,
    condition: 'Sunny',
    windSpeed: 8,
    humidity: 65
  };

  describe('generateAnalysis', () => {
    it('should generate analysis with valid inputs', async () => {
      const text = await generateAnalysis(mockBetSlip, mockGameData, mockWeather);
      expect(text).toBe('Mock analysis response');
    });

    it('should handle missing OpenAI API key', async () => {
      const { getEnv } = require('../src/utils/env');
      getEnv.mockReturnValueOnce({ OPENAI_API_KEY: undefined });
      
      const text = await generateAnalysis(mockBetSlip, mockGameData, mockWeather);
      expect(text).toContain('AI analysis unavailable');
    });

    it('should handle OpenAI API errors', async () => {
      mockCreate.mockRejectedValueOnce(new Error('API Error'));
      
      const text = await generateAnalysis(mockBetSlip, mockGameData, mockWeather);
      expect(text).toContain('AI analysis failed');
    });

    it('should handle empty response from OpenAI', async () => {
      mockCreate.mockResolvedValueOnce({
        choices: [{ message: { content: undefined } }]
      });
      
      const text = await generateAnalysis(mockBetSlip, mockGameData, mockWeather);
      expect(text).toContain('Failed to generate analysis');
    });
  });

  describe('buildPrompt', () => {
    it('should build prompt with all data', () => {
      const prompt = buildPrompt(mockBetSlip, mockGameData, mockWeather);
      
      expect(prompt).toContain('NYM vs PHI');
      expect(prompt).toContain('-120');
      expect(prompt).toContain('5');
      expect(prompt).toContain('72°F');
      expect(prompt).toContain('Sunny');
    });

    it('should build prompt without weather data', () => {
      const prompt = buildPrompt(mockBetSlip, mockGameData);
      
      expect(prompt).toContain('NYM vs PHI');
      expect(prompt).toContain('-120');
      expect(prompt).toContain('5');
      expect(prompt).not.toContain('Weather:');
    });

    it('should handle positive odds', () => {
      const positiveBetSlip: BetSlip = {
        ...mockBetSlip,
        legs: [{ 
          gameId: 'NYM_PHI_20241201',
          teamA: 'NYM',
          teamB: 'PHI',
          odds: 150 
        }]
      };
      
      const prompt = buildPrompt(positiveBetSlip, mockGameData, mockWeather);
      expect(prompt).toContain('+150');
    });
  });
}); 