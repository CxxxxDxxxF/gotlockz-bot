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

const mockParlayBetSlip: BetSlip = {
  legs: [
    {
      gameId: 'NYM_PHI_20241201',
      teamA: 'NYM',
      teamB: 'PHI',
      odds: -120
    },
    {
      gameId: 'LAD_SF_20241201',
      teamA: 'LAD',
      teamB: 'SF',
      odds: 110
    }
  ],
  units: 3,
  type: 'PARLAY'
};

const mockAnalysis = 'This is a test analysis for the betting play.';

describe('Betting Message Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
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
  });

  describe('createFreePlayMessage', () => {
    it('should create a valid free play message', async () => {
      const freePlayMessage = await createFreePlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      expect(freePlayMessage.playNumber).toBeGreaterThan(0);
      expect(new Date(freePlayMessage.timestamp)).toBeInstanceOf(Date);
      expect(freePlayMessage.channel).toBe('free_plays');
      expect(freePlayMessage.analysis).toBe(mockAnalysis);
    });

    it('should include image URL when provided', async () => {
      const imageUrl = 'https://example.com/image.jpg';
      const freePlayMessage = await createFreePlayMessage(mockBetSlip, mockGameData, mockAnalysis, imageUrl);
      
      expect(freePlayMessage.assets?.imageUrl).toBe(imageUrl);
    });

    it('should throw error for empty bet slip', async () => {
      const emptyBetSlip: BetSlip = {
        legs: [],
        units: 0,
        type: 'SINGLE'
      };
      
      await expect(createFreePlayMessage(emptyBetSlip, mockGameData, mockAnalysis))
        .rejects.toThrow('Free play must have at least 1 leg');
    });
  });

  describe('createLottoTicketMessage', () => {
    it('should create a valid lotto ticket message', async () => {
      const lottoMessage = await createLottoTicketMessage(mockParlayBetSlip, mockGameData, mockAnalysis);
      
      expect(lottoMessage.ticketNumber).toBeGreaterThan(0);
      expect(new Date(lottoMessage.timestamp)).toBeInstanceOf(Date);
      expect(lottoMessage.channel).toBe('lotto_ticket');
      expect(lottoMessage.analysis).toBe(mockAnalysis);
    });

    it('should include notes when provided', async () => {
      const notes = 'This is a test note for the lotto ticket.';
      const lottoMessage = await createLottoTicketMessage(mockParlayBetSlip, mockGameData, mockAnalysis, undefined, notes);
      
      expect(lottoMessage.notes).toBe(notes);
    });

    it('should throw error for single leg bet slip', async () => {
      await expect(createLottoTicketMessage(mockBetSlip, mockGameData, mockAnalysis))
        .rejects.toThrow('Lotto ticket must have at least 2 legs');
    });
  });

  describe('validateBettingMessage', () => {
    it('should validate a correct VIP play message', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'object') {
        expect(validateBettingMessage(vipMessage)).toBe(true);
      }
    });

    it('should validate a correct free play message', async () => {
      const freePlayMessage = await createFreePlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      expect(validateBettingMessage(freePlayMessage)).toBe(true);
    });

    it('should validate a correct lotto ticket message', async () => {
      const lottoMessage = await createLottoTicketMessage(mockParlayBetSlip, mockGameData, mockAnalysis);
      expect(validateBettingMessage(lottoMessage)).toBe(true);
    });

    it('should reject message with wrong channel', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'object') {
        (vipMessage as any).channel = 'wrong_channel';
        expect(validateBettingMessage(vipMessage)).toBe(false);
      }
    });

    it('should reject message with invalid play number', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'object') {
        (vipMessage as any).playNumber = 0;
        expect(validateBettingMessage(vipMessage)).toBe(false);
      }
    });

    it('should reject message with empty game teams', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'object') {
        (vipMessage as any).game.away = '';
        expect(validateBettingMessage(vipMessage)).toBe(false);
      }
    });

    it('should reject message with empty bet selection', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'object') {
        (vipMessage as any).bet.selection = '';
        expect(validateBettingMessage(vipMessage)).toBe(false);
      }
    });

    it('should reject message with invalid odds', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'object') {
        (vipMessage as any).bet.odds = 'invalid' as any;
        expect(validateBettingMessage(vipMessage)).toBe(false);
      }
    });

    it('should reject message with invalid unit size', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'object') {
        (vipMessage as any).bet.unitSize = 0;
        expect(validateBettingMessage(vipMessage)).toBe(false);
      }
    });

    it('should reject message with empty analysis', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'object') {
        (vipMessage as any).analysis = '';
        expect(validateBettingMessage(vipMessage)).toBe(false);
      }
    });
  });

  describe('formatBettingMessageForDiscord', () => {
    it('should format VIP play message for Discord embed', async () => {
      const vipMessage = await createVIPPlayMessage(mockBetSlip, mockGameData, mockAnalysis, 'https://example.com/image.jpg');
      
      if (typeof vipMessage === 'object') {
        const embed = formatBettingMessageForDiscord(vipMessage);
        
        expect(embed.data.title).toBe(`🎯 VIP Play #${vipMessage.playNumber}`);
        expect(embed.data.description).toBe(mockAnalysis);
        expect(embed.data.fields).toHaveLength(5);
        expect(embed.data.fields?.find(field => field.name === '💰 Odds')?.value).toContain('-120');
        expect(embed.data.footer?.text).toBe(`GotLockz Family • VIP Play #${vipMessage.playNumber}`);
      }
    });

    it('should format free play message for Discord embed', async () => {
      const freePlayMessage = await createFreePlayMessage(mockBetSlip, mockGameData, mockAnalysis, 'https://example.com/image.jpg');
      const embed = formatBettingMessageForDiscord(freePlayMessage);
      
      expect(embed.data.title).toBe('🎁 Free Play is Here!');
      expect(embed.data.description).toBe(mockAnalysis);
      expect(embed.data.fields).toHaveLength(4);
      expect(embed.data.fields?.find(field => field.name === '💰 Odds')?.value).toContain('-120');
      expect(embed.data.footer?.text).toBe('GotLockz Family • Free Play');
    });

    it('should format lotto ticket message for Discord embed', async () => {
      const notes = 'This is a test note for the lotto ticket.';
      const lottoMessage = await createLottoTicketMessage(mockParlayBetSlip, mockGameData, mockAnalysis, 'https://example.com/image.jpg', notes);
      const embed = formatBettingMessageForDiscord(lottoMessage);
      
      expect(embed.data.title).toBe('🎰 Lotto Ticket Alert!');
      expect(embed.data.description).toBe(mockAnalysis);
      expect(embed.data.fields).toHaveLength(6); // Including notes field
      expect(embed.data.fields?.find(field => field.name === '💰 Odds')?.value).toBeDefined();
      expect(embed.data.fields?.find(field => field.name === '📝 Notes')?.value).toBe(notes);
      expect(embed.data.footer?.text).toBe('GotLockz Family • Lotto Ticket');
    });

    it('should handle negative odds correctly', async () => {
      const negativeBetSlip: BetSlip = {
        legs: [{ gameId: 'test', teamA: 'NYM', teamB: 'PHI', odds: -150 }],
        units: 3,
        type: 'SINGLE'
      };
      
      const vipMessage = await createVIPPlayMessage(negativeBetSlip, mockGameData, mockAnalysis);
      
      if (typeof vipMessage === 'object') {
        const embed = formatBettingMessageForDiscord(vipMessage);
        const oddsField = embed.data.fields?.find(field => field.name === '💰 Odds');
        expect(oddsField?.value).toBe('-150');
      }
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