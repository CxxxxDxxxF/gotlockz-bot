/**
 * Betting Message Service Tests
 */
import { 
  createVIPPlayMessage, 
  createFreePlayMessage, 
  createLottoTicketMessage,
  validateBettingMessage,
  formatBettingMessageForDiscord,
  getVIPPlayCounterStats 
} from '../src/services/bettingMessageService';
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

const mockParlayBetSlip: BetSlip = {
  type: 'PARLAY',
  units: 1.0,
  legs: [
    {
      gameId: 'YANKEES_RED SOX_1234567890',
      teamA: 'YANKEES',
      teamB: 'RED SOX',
      odds: 150
    },
    {
      gameId: 'DODGERS_GIANTS_1234567891',
      teamA: 'DODGERS',
      teamB: 'GIANTS',
      odds: -110
    },
    {
      gameId: 'ASTROS_RANGERS_1234567892',
      teamA: 'ASTROS',
      teamB: 'RANGERS',
      odds: 200
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

describe('Betting Message Service', () => {
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

      if (typeof vipMessage === 'string') {
        throw new Error('Expected VIP Play message to be object, not error string');
      }

      expect(vipMessage.playNumber).toBeGreaterThan(0);
      expect(new Date(vipMessage.timestamp)).toBeInstanceOf(Date);
    });

    it('increments play number for each call', async () => {
      const message1 = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      const message2 = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);

      // Check that both messages are valid objects (not error strings)
      if (typeof message1 === 'string' || typeof message2 === 'string') {
        throw new Error('Expected VIP Play messages to be objects, not error strings');
      }

      expect(message2.playNumber).toBe(message1.playNumber + 1);
    });

    it('includes image URL when provided', async () => {
      const imageUrl = 'https://example.com/betslip.png';
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis, imageUrl);

      if (typeof vipMessage === 'string') {
        throw new Error('Expected VIP Play message to be object, not error string');
      }

      expect(vipMessage.assets).toEqual({ imageUrl });
    });
  });

  describe('createFreePlayMessage', () => {
    it('creates a valid Free Play message', async () => {
      const freePlayMessage = await createFreePlayMessage(mockBetSlip, mockGameData, mockAnalysis);

      expect(freePlayMessage).toMatchObject({
        channel: 'free_plays',
        playType: 'FREE_PLAY',
        game: {
          away: 'YANKEES',
          home: 'RED SOX',
          startTime: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/)
        },
        bet: {
          selection: 'YANKEES',
          market: 'YANKEES vs RED SOX',
          odds: 150
        },
        analysis: mockAnalysis
      });

      expect(new Date(freePlayMessage.timestamp)).toBeInstanceOf(Date);
    });

    it('includes image URL when provided', async () => {
      const imageUrl = 'https://example.com/betslip.png';
      const freePlayMessage = await createFreePlayMessage(mockBetSlip, mockGameData, mockAnalysis, imageUrl);

      expect(freePlayMessage.assets).toEqual({ imageUrl });
    });
  });

  describe('createLottoTicketMessage', () => {
    it('creates a valid Lotto Ticket message', async () => {
      const lottoMessage = await createLottoTicketMessage(mockParlayBetSlip, mockGameData, mockAnalysis);

      expect(lottoMessage).toMatchObject({
        channel: 'lotto_ticket',
        ticketType: 'LOTTO_TICKET',
        games: expect.arrayContaining([
          expect.objectContaining({
            away: 'YANKEES',
            home: 'RED SOX'
          }),
          expect.objectContaining({
            away: 'DODGERS',
            home: 'GIANTS'
          }),
          expect.objectContaining({
            away: 'ASTROS',
            home: 'RANGERS'
          })
        ]),
        legs: expect.arrayContaining([
          expect.objectContaining({
            selection: 'YANKEES',
            market: 'YANKEES vs RED SOX',
            odds: 150
          }),
          expect.objectContaining({
            selection: 'DODGERS',
            market: 'DODGERS vs GIANTS',
            odds: -110
          }),
          expect.objectContaining({
            selection: 'ASTROS',
            market: 'ASTROS vs RANGERS',
            odds: 200
          })
        ]),
        parlayOdds: expect.any(Number),
        analysis: mockAnalysis
      });

      expect(lottoMessage.games).toHaveLength(3);
      expect(lottoMessage.legs).toHaveLength(3);
      expect(new Date(lottoMessage.timestamp)).toBeInstanceOf(Date);
    });

    it('includes notes when provided', async () => {
      const notes = 'This is a high-risk, high-reward parlay!';
      const lottoMessage = await createLottoTicketMessage(mockParlayBetSlip, mockGameData, mockAnalysis, undefined, notes);

      expect(lottoMessage.notes).toBe(notes);
    });

    it('throws error when bet slip has less than 2 legs', async () => {
      await expect(createLottoTicketMessage(mockBetSlip, mockGameData, mockAnalysis))
        .rejects.toThrow('Lotto ticket must have at least 2 legs');
    });
  });

  describe('validateBettingMessage', () => {
    it('validates a correct VIP Play message', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'string') {
        throw new Error('Expected VIP Play message to be object, not error string');
      }
      
      expect(validateBettingMessage(vipMessage)).toBe(true);
    });

    it('validates a correct Free Play message', async () => {
      const freePlayMessage = await createFreePlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      expect(validateBettingMessage(freePlayMessage)).toBe(true);
    });

    it('validates a correct Lotto Ticket message', async () => {
      const lottoMessage = await createLottoTicketMessage(mockParlayBetSlip, mockGameData, mockAnalysis);
      expect(validateBettingMessage(lottoMessage)).toBe(true);
    });

    it('rejects message with invalid channel', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'string') {
        throw new Error('Expected VIP Play message to be object, not error string');
      }
      
      (vipMessage as any).channel = 'wrong_channel';
      expect(validateBettingMessage(vipMessage as any)).toBe(false);
    });

    it('rejects message with empty analysis', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'string') {
        throw new Error('Expected VIP Play message to be object, not error string');
      }
      
      vipMessage.analysis = '';
      expect(validateBettingMessage(vipMessage)).toBe(false);
    });
  });

  describe('formatBettingMessageForDiscord', () => {
    it('formats VIP Play message as Discord embed', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'string') {
        throw new Error('Expected VIP Play message to be object, not error string');
      }
      
      const embed = formatBettingMessageForDiscord(vipMessage);

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

    it('formats Free Play message as Discord embed', async () => {
      const freePlayMessage = await createFreePlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      const embed = formatBettingMessageForDiscord(freePlayMessage);

      expect(embed).toMatchObject({
        title: '🎁 Free Play is Here!',
        description: mockAnalysis,
        color: 0x0099ff,
        fields: expect.arrayContaining([
          expect.objectContaining({ name: '🏟️ Game', value: 'YANKEES @ RED SOX' }),
          expect.objectContaining({ name: '🎲 Bet', value: 'YANKEES - YANKEES vs RED SOX' }),
          expect.objectContaining({ name: '💰 Odds', value: '+150' })
        ]),
        footer: expect.objectContaining({
          text: 'GotLockz Family • Free Play'
        })
      });
    });

    it('formats Lotto Ticket message as Discord embed', async () => {
      const lottoMessage = await createLottoTicketMessage(mockParlayBetSlip, mockGameData, mockAnalysis);
      const embed = formatBettingMessageForDiscord(lottoMessage);

      expect(embed).toMatchObject({
        title: '🎰 Lotto Ticket Alert!',
        description: mockAnalysis,
        color: 0xff6600,
        fields: expect.arrayContaining([
          expect.objectContaining({ name: '🎮 Games' }),
          expect.objectContaining({ name: '🎲 Legs' }),
          expect.objectContaining({ name: '💰 Parlay Odds' })
        ]),
        footer: expect.objectContaining({
          text: 'GotLockz Family • Lotto Ticket'
        })
      });
    });

    it('includes notes field for Lotto Ticket with notes', async () => {
      const notes = 'High-risk parlay!';
      const lottoMessage = await createLottoTicketMessage(mockParlayBetSlip, mockGameData, mockAnalysis, undefined, notes);
      const embed = formatBettingMessageForDiscord(lottoMessage);

      const notesField = embed.fields.find((field: any) => field.name === '📝 Notes');
      expect(notesField?.value).toBe(notes);
    });

    it('throws error for unknown message channel', async () => {
      const invalidMessage = { channel: 'unknown' } as any;
      expect(() => formatBettingMessageForDiscord(invalidMessage)).toThrow('Unknown message channel: unknown');
    });
  });

  describe('getVIPPlayCounterStats', () => {
    it('returns current VIP play counter stats', () => {
      const stats = getVIPPlayCounterStats();
      
      expect(stats).toMatchObject({
        date: expect.stringMatching(/^\d{4}-\d{2}-\d{2}$/),
        count: expect.any(Number),
        lastReset: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/)
      });
    });
  });
}); 