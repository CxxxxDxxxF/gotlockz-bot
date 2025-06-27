import { buildPrompt } from '../../src/services/analysisService';
import { BetSlip } from '../../src/utils/parser';
import { GameStats } from '../../src/services/mlbService';

describe('Analysis Prompt Builder', () => {
  it('includes key stats for each leg', () => {
    const slip: BetSlip = {
      type: 'PARLAY',
      units: 2,
      legs: [
        {
          gameId: 'YANKEES_RED SOX_1234567890',
          teamA: 'YANKEES',
          teamB: 'RED SOX',
          odds: 150
        },
        {
          gameId: 'DODGERS_GIANTS_1234567890',
          teamA: 'DODGERS',
          teamB: 'GIANTS',
          odds: 120
        }
      ]
    };
    const gameDatas: GameStats[] = [
      {
        gameId: 'YANKEES_RED SOX_1234567890',
        date: '2024-01-15',
        teams: ['YANKEES', 'RED SOX'],
        score: '5-3',
        status: 'final',
        keyStats: {
          homeTeam: { batting_avg: '0.250', runs: '5', hits: '8', home_runs: '2', rbis: '5', era: '3.50', wins: '10', losses: '5', saves: '2', strikeouts: '9' },
          awayTeam: { batting_avg: '0.240', runs: '3', hits: '7', home_runs: '1', rbis: '3', era: '4.10', wins: '8', losses: '7', saves: '1', strikeouts: '8' }
        }
      },
      {
        gameId: 'DODGERS_GIANTS_1234567890',
        date: '2024-01-15',
        teams: ['DODGERS', 'GIANTS'],
        score: '2-1',
        status: 'final',
        keyStats: {
          homeTeam: { batting_avg: '0.260', runs: '2', hits: '6', home_runs: '1', rbis: '2', era: '3.20', wins: '12', losses: '3', saves: '3', strikeouts: '10' },
          awayTeam: { batting_avg: '0.230', runs: '1', hits: '5', home_runs: '0', rbis: '1', era: '4.50', wins: '7', losses: '8', saves: '0', strikeouts: '7' }
        }
      }
    ];
    const edge = 0.12;
    const weather = 'Clear skies, 75F';

    const prompt = buildPrompt(slip, gameDatas, edge, weather);
    expect(prompt).toContain('Game Data:');
    expect(prompt).toContain('5-3');
    expect(prompt).toContain('2-1');
    expect(prompt).toContain('batting_avg');
    expect(prompt).toContain('Clear skies');
  });
}); 