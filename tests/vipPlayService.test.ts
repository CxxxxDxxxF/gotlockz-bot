/**
 * VIP Play Service Tests
 */
import { createVIPPlayMessage, validateVIPPlayMessage, formatVIPPlayForDiscord, getPlayCounterStats } from '../src/services/vipPlayService';
import { BetSlip } from '../src/utils/parser';
import { GameStats } from '../src/services/mlbService';

// Mock bet slip and game data
const mockBetSlip: BetSlip = {
  type: 'SINGLE',
  units: 2.5,
  legs: [
    {
      gameId: 'YANKEES_RED SOX_1234567890',
      teamA: 'YANKEES',
      teamB: 'RED SOX',
      odds: 150
    }
  ]
};

const mockGameData: GameStats = {
  gameId: 'YANKEES_RED SOX_1234567890',
  date: '2024-01-15',
  teams: ['YANKEES', 'RED SOX'],
  score: '5-3',
  status: 'scheduled',
  keyStats: {
    homeTeam: {
      batting_avg: '0.250',
      runs: '5',
      hits: '8',
      home_runs: '2',
      rbis: '5',
      era: '3.50',
      wins: '10',
      losses: '5',
      saves: '2',
      strikeouts: '9'
    },
    awayTeam: {
      batting_avg: '0.240',
      runs: '3',
      hits: '7',
      home_runs: '1',
      rbis: '3',
      era: '4.10',
      wins: '8',
      losses: '7',
      saves: '1',
      strikeouts: '8'
    }
  }
};

const mockAnalysis = 'This is a hype-driven analysis of the game. The YANKEES are looking strong today with their recent performance. The weather conditions are perfect for hitting, and the pitching matchup favors our pick. Let\'s get this bread! 💰';

describe('VIP Play Service', () => {
  beforeEach(() => {
    // Reset play counter for each test
    jest.clearAllMocks();
  });

  describe('createVIPPlayMessage', () => {
    it('creates a valid VIP Play message', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);

      expect(vipMessage).toMatchObject({
        channel: 'vip_plays',
        playNumber: expect.any(Number),
        game: {
          away: 'YANKEES',
          home: 'RED SOX',
          startTime: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/)
        },
        bet: {
          selection: 'YANKEES',
          market: 'YANKEES vs RED SOX',
          odds: 150,
          unitSize: 2.5
        },
        analysis: mockAnalysis
      });

      expect(vipMessage.playNumber).toBeGreaterThan(0);
      expect(new Date(vipMessage.timestamp)).toBeInstanceOf(Date);
    });

    it('increments play number for each call', async () => {
      const message1 = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      const message2 = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);

      expect(message2.playNumber).toBe(message1.playNumber + 1);
    });

    it('includes image URL when provided', async () => {
      const imageUrl = 'https://example.com/betslip.png';
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis, imageUrl);

      expect(vipMessage.assets).toEqual({ imageUrl });
    });

    it('throws error when no bet legs found', async () => {
      const emptyBetSlip: BetSlip = {
        type: 'SINGLE',
        units: 1,
        legs: []
      };

      await expect(createVIPPlayMessage(emptyBetSlip, mockGameData, mockAnalysis))
        .rejects.toThrow('No bet legs found in slip');
    });
  });

  describe('validateVIPPlayMessage', () => {
    it('validates a correct VIP Play message', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      expect(validateVIPPlayMessage(vipMessage)).toBe(true);
    });

    it('rejects message with invalid channel', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      vipMessage.channel = 'wrong_channel' as any;
      expect(validateVIPPlayMessage(vipMessage)).toBe(false);
    });

    it('rejects message with invalid play number', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      vipMessage.playNumber = 0;
      expect(validateVIPPlayMessage(vipMessage)).toBe(false);
    });

    it('rejects message with missing game data', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      vipMessage.game.away = '';
      expect(validateVIPPlayMessage(vipMessage)).toBe(false);
    });

    it('rejects message with missing bet data', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      vipMessage.bet.selection = '';
      expect(validateVIPPlayMessage(vipMessage)).toBe(false);
    });

    it('rejects message with invalid odds', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      vipMessage.bet.odds = 'invalid' as any;
      expect(validateVIPPlayMessage(vipMessage)).toBe(false);
    });

    it('rejects message with invalid unit size', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      vipMessage.bet.unitSize = 0;
      expect(validateVIPPlayMessage(vipMessage)).toBe(false);
    });

    it('rejects message with empty analysis', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      vipMessage.analysis = '';
      expect(validateVIPPlayMessage(vipMessage)).toBe(false);
    });
  });

  describe('formatVIPPlayForDiscord', () => {
    it('formats VIP Play message as Discord embed', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      const embed = formatVIPPlayForDiscord(vipMessage);

      expect(embed).toMatchObject({
        title: `🎯 VIP Play #${vipMessage.playNumber}`,
        description: mockAnalysis,
        color: 0x00ff00,
        fields: expect.arrayContaining([
          expect.objectContaining({ name: '🏟️ Game', value: 'YANKEES @ RED SOX' }),
          expect.objectContaining({ name: '🎲 Bet', value: 'YANKEES - YANKEES vs RED SOX' }),
          expect.objectContaining({ name: '💰 Odds', value: '+150' }),
          expect.objectContaining({ name: '📊 Units', value: '2.5' })
        ]),
        footer: expect.objectContaining({
          text: `GotLockz Family • VIP Play #${vipMessage.playNumber}`
        })
      });
    });

    it('includes image when provided', async () => {
      const imageUrl = 'https://example.com/betslip.png';
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis, imageUrl);
      const embed = formatVIPPlayForDiscord(vipMessage);

      expect((embed as any).image).toEqual({ url: imageUrl });
    });

    it('handles negative odds correctly', async () => {
      const negativeBetSlip: BetSlip = {
        ...mockBetSlip,
        legs: [{ 
          gameId: 'YANKEES_RED SOX_1234567890',
          teamA: 'YANKEES',
          teamB: 'RED SOX',
          odds: -140 
        }]
      };
      
      const vipMessage = await createVIPPlayMessage(negativeBetSlip, mockGameData, mockAnalysis);
      const embed = formatVIPPlayForDiscord(vipMessage);

      const oddsField = (embed.fields as any[]).find((field: any) => field.name === '💰 Odds');
      expect(oddsField?.value).toBe('-140');
    });
  });

  describe('getPlayCounterStats', () => {
    it('returns current play counter stats', () => {
      const stats = getPlayCounterStats();
      
      expect(stats).toMatchObject({
        date: expect.stringMatching(/^\d{4}-\d{2}-\d{2}$/),
        count: expect.any(Number),
        lastReset: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/)
      });
    });
  });
}); 