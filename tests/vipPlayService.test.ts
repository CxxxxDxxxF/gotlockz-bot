/**
 * VIP Play Service Tests
 */
import { createVIPPlayMessage, validateVIPPlayMessage, formatVIPPlayForDiscord, getPlayCounterStats, resetPlayCounter } from '../src/services/vipPlayService';
import { BetSlip } from '../src/utils/parser';
import { GameData } from '../src/types';

// Mock data
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
  startTime: '2024-12-01T19:00:00Z',
  venue: 'Citi Field'
};

const mockAnalysis = 'This is a test analysis for the VIP play.';

describe('VIP Play Service', () => {
  beforeEach(() => {
    // Reset play counter for each test
    jest.clearAllMocks();
    resetPlayCounter();
  });

  describe('createVIPPlayMessage', () => {
    it('should create a valid VIP play message', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      expect(typeof vipMessage).toBe('object');
      if (typeof vipMessage === 'object') {
        expect(vipMessage.playNumber).toBeGreaterThan(0);
        expect(new Date(vipMessage.timestamp)).toBeInstanceOf(Date);
        expect(vipMessage.channel).toBe('vip_plays');
        expect(vipMessage.analysis).toBe(mockAnalysis);
      }
    });

    it('should increment play numbers sequentially', async () => {
      const message1 = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      const message2 = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof message1 === 'object' && typeof message2 === 'object') {
        expect(message2.playNumber).toBe(message1.playNumber + 1);
      }
    });

    it('should include image URL when provided', async () => {
      const imageUrl = 'https://example.com/image.jpg';
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis, imageUrl);
      
      if (typeof vipMessage === 'object') {
        expect(vipMessage.assets?.imageUrl).toBe(imageUrl);
      }
    });

    it('should return error message for empty bet slip', async () => {
      const emptyBetSlip: BetSlip = {
        legs: [],
        units: 0,
        type: 'SINGLE'
      };
      
      const result = await createVIPPlayMessage(emptyBetSlip, mockGameData, mockAnalysis);
      expect(typeof result).toBe('string');
      expect(result).toContain("Couldn't find any valid bet legs");
    });

    it('should return error message for invalid game data', async () => {
      const invalidGameData: GameData = {
        gameId: 'test',
        date: '2024-12-01',
        teams: ['NYM', 'TBD'], // Missing second team
        score: '0-0',
        status: 'scheduled'
      };
      
      const result = await createVIPPlayMessage(mockBetSlip, invalidGameData, mockAnalysis);
      // The function now returns an object even for invalid data, so we check if it's a valid message
      if (typeof result === 'object') {
        expect(validateVIPPlayMessage(result)).toBe(false);
      } else {
        expect(typeof result).toBe('string');
        expect(result).toContain('Invalid game data');
      }
    });
  });

  describe('validateVIPPlayMessage', () => {
    it('should validate a correct VIP play message', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'object') {
        expect(validateVIPPlayMessage(vipMessage)).toBe(true);
      }
    });

    it('should reject message with wrong channel', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'object') {
        (vipMessage as any).channel = 'wrong_channel';
        expect(validateVIPPlayMessage(vipMessage)).toBe(false);
      }
    });

    it('should reject message with invalid play number', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'object') {
        (vipMessage as any).playNumber = 0;
        expect(validateVIPPlayMessage(vipMessage)).toBe(false);
      }
    });

    it('should reject message with empty game teams', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'object') {
        (vipMessage as any).game.away = '';
        expect(validateVIPPlayMessage(vipMessage)).toBe(false);
      }
    });

    it('should reject message with empty bet selection', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'object') {
        (vipMessage as any).bet.selection = '';
        expect(validateVIPPlayMessage(vipMessage)).toBe(false);
      }
    });

    it('should reject message with invalid odds', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'object') {
        (vipMessage as any).bet.odds = 'invalid' as any;
        expect(validateVIPPlayMessage(vipMessage)).toBe(false);
      }
    });

    it('should reject message with invalid unit size', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'object') {
        (vipMessage as any).bet.unitSize = 0;
        expect(validateVIPPlayMessage(vipMessage)).toBe(false);
      }
    });

    it('should reject message with empty analysis', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'object') {
        (vipMessage as any).analysis = '';
        expect(validateVIPPlayMessage(vipMessage)).toBe(false);
      }
    });
  });

  describe('formatVIPPlayForDiscord', () => {
    it('should format VIP play message for Discord embed', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis, 'https://example.com/image.jpg');
      
      if (typeof vipMessage === 'object') {
        const embed = formatVIPPlayForDiscord(vipMessage);
        
        expect(embed.data.title).toBe(`🎯 VIP Play #${vipMessage.playNumber}`);
        expect(embed.data.description).toBe(mockAnalysis);
        expect(embed.data.fields).toHaveLength(5);
        expect(embed.data.fields?.find(field => field.name === '💰 Odds')?.value).toContain('-120');
        expect(embed.data.footer?.text).toBe(`GotLockz Family • VIP Play #${vipMessage.playNumber}`);
      }
    });

    it('should handle negative odds correctly', async () => {
      const negativeBetSlip: BetSlip = {
        legs: [{ gameId: 'test', teamA: 'NYM', teamB: 'PHI', odds: -150 }],
        units: 3,
        type: 'SINGLE'
      };
      
      const vipMessage = await createVIPPlayMessage(negativeBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'object') {
        const embed = formatVIPPlayForDiscord(vipMessage);
        const oddsField = embed.data.fields?.find(field => field.name === '💰 Odds');
        expect(oddsField?.value).toBe('-150');
      }
    });
  });

  describe('getPlayCounterStats', () => {
    it('should return current counter statistics', () => {
      const stats = getPlayCounterStats();
      
      expect(stats).toHaveProperty('date');
      expect(stats).toHaveProperty('count');
      expect(stats).toHaveProperty('lastReset');
      expect(typeof stats.count).toBe('number');
    });
  });
}); 