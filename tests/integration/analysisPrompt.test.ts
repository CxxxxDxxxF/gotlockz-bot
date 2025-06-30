/**
 * Analysis Prompt Integration Tests
 */
import { buildPrompt } from '../../src/services/analysisService';
import { BetSlip, GameData } from '../../src/types';

describe('Analysis Prompt Integration', () => {
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

  describe('buildPrompt', () => {
    it('should build comprehensive prompt with all data', () => {
      const prompt = buildPrompt(mockBetSlip, mockGameData, mockWeather);
      
      expect(prompt).toContain('NYM vs PHI');
      expect(prompt).toContain('-120');
      expect(prompt).toContain('5');
      expect(prompt).toContain('72°F');
      expect(prompt).toContain('Sunny');
      expect(prompt).toContain('MLB betting pick');
      expect(prompt).toContain('Key factors');
      expect(prompt).toContain('Potential risks');
      expect(prompt).toContain('Confidence level');
    });

    it('should build prompt without weather data', () => {
      const prompt = buildPrompt(mockBetSlip, mockGameData);
      
      expect(prompt).toContain('NYM vs PHI');
      expect(prompt).toContain('-120');
      expect(prompt).toContain('5');
      expect(prompt).not.toContain('Weather:');
    });

    it('should handle positive odds correctly', () => {
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

    it('should handle multiple legs', () => {
      const multiLegBetSlip: BetSlip = {
        legs: [
          { gameId: 'NYM_PHI_20241201', teamA: 'NYM', teamB: 'PHI', odds: -120 },
          { gameId: 'LAD_SF_20241201', teamA: 'LAD', teamB: 'SF', odds: 110 }
        ],
        units: 3,
        type: 'PARLAY'
      };
      
      const prompt = buildPrompt(multiLegBetSlip, mockGameData, mockWeather);
      expect(prompt).toContain('NYM'); // Should use first leg
      expect(prompt).toContain('-120');
    });

    it('should include professional tone instructions', () => {
      const prompt = buildPrompt(mockBetSlip, mockGameData, mockWeather);
      
      expect(prompt).toContain('concise, professional analysis');
      expect(prompt).toContain('confident but measured tone');
      expect(prompt).toContain('under 200 words');
    });
  });
}); 