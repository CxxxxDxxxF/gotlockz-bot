/**
 * MLB Service Integration Tests
 */
import { getGameData } from '../../src/services/mlbService';

// Mock axios for API calls
jest.mock('axios', () => ({
  get: jest.fn()
}));

const mockAxios = require('axios');

describe('MLB Service Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('returns expected game data structure for valid game ID', async () => {
    // Mock successful MLB API response
    mockAxios.get.mockResolvedValueOnce({
      data: {
        dates: [{
          games: [{
            gamePk: 12345,
            gameDate: '2024-01-15T19:00:00Z',
            teams: {
              home: {
                team: { name: 'New York Yankees' },
                score: 5
              },
              away: {
                team: { name: 'Boston Red Sox' },
                score: 3
              }
            },
            status: { detailedState: 'Final' }
          }]
        }]
      }
    });

    const gameData = await getGameData('YANKEES_RED SOX_1234567890');

    expect(gameData).toEqual(
      expect.objectContaining({
        gameId: expect.any(String),
        date: expect.any(String),
        teams: expect.any(Array),
        score: expect.stringMatching(/^\d+-\d+$/),
        status: expect.any(String),
        keyStats: expect.objectContaining({
          homeTeam: expect.objectContaining({
            batting_avg: expect.any(String),
            runs: expect.any(String),
            hits: expect.any(String),
            home_runs: expect.any(String),
            rbis: expect.any(String),
            era: expect.any(String),
            wins: expect.any(String),
            losses: expect.any(String),
            saves: expect.any(String),
            strikeouts: expect.any(String)
          }),
          awayTeam: expect.objectContaining({
            batting_avg: expect.any(String),
            runs: expect.any(String),
            hits: expect.any(String),
            home_runs: expect.any(String),
            rbis: expect.any(String),
            era: expect.any(String),
            wins: expect.any(String),
            losses: expect.any(String),
            saves: expect.any(String),
            strikeouts: expect.any(String)
          })
        })
      })
    );
  });

  it('falls back to mock data when API fails', async () => {
    // Mock API failure
    mockAxios.get.mockRejectedValueOnce(new Error('API Error'));

    const gameData = await getGameData('TEAM A_TEAM B_1234567890');

    expect(gameData).toEqual(
      expect.objectContaining({
        gameId: 'TEAM A_TEAM B_1234567890',
        date: expect.any(String),
        teams: ['TEAM A', 'TEAM B'],
        score: expect.stringMatching(/^\d+-\d+$/),
        status: 'scheduled',
        keyStats: expect.objectContaining({
          homeTeam: expect.objectContaining({
            batting_avg: expect.any(String),
            runs: expect.any(String),
            hits: expect.any(String),
            home_runs: expect.any(String),
            rbis: expect.any(String),
            era: expect.any(String),
            wins: expect.any(String),
            losses: expect.any(String),
            saves: expect.any(String),
            strikeouts: expect.any(String)
          }),
          awayTeam: expect.objectContaining({
            batting_avg: expect.any(String),
            runs: expect.any(String),
            hits: expect.any(String),
            home_runs: expect.any(String),
            rbis: expect.any(String),
            era: expect.any(String),
            wins: expect.any(String),
            losses: expect.any(String),
            saves: expect.any(String),
            strikeouts: expect.any(String)
          })
        })
      })
    );
  });

  it('handles empty API response gracefully', async () => {
    // Mock empty API response
    mockAxios.get.mockResolvedValueOnce({
      data: { dates: [] }
    });

    const gameData = await getGameData('YANKEES_RED SOX_1234567890');

    expect(gameData).toEqual(
      expect.objectContaining({
        gameId: 'YANKEES_RED SOX_1234567890',
        date: expect.any(String),
        teams: ['YANKEES', 'RED SOX'],
        score: expect.stringMatching(/^\d+-\d+$/),
        status: 'scheduled'
      })
    );
  });

  it('generates consistent mock data for same team names', async () => {
    const gameData1 = await getGameData('YANKEES_RED SOX_1234567890');
    const gameData2 = await getGameData('YANKEES_RED SOX_1234567890');

    expect(gameData1.teams).toEqual(gameData2.teams);
    expect(gameData1.keyStats.homeTeam).toBeDefined();
    expect(gameData1.keyStats.awayTeam).toBeDefined();
  });

  it('handles malformed game ID gracefully', async () => {
    const gameData = await getGameData('invalid_game_id');

    expect(gameData).toEqual(
      expect.objectContaining({
        gameId: 'invalid_game_id',
        date: expect.any(String),
        teams: expect.any(Array),
        score: expect.stringMatching(/^\d+-\d+$/),
        status: 'scheduled'
      })
    );
  });
}); 