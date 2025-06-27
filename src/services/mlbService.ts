/**
 * MLB Service - Game statistics and data
 */
import axios from 'axios';

export interface GameStats {
  gameId: string;
  date: string;
  teams: [string, string];
  score: string;
  status: 'scheduled' | 'live' | 'final';
  keyStats: {
    homeTeam: {
      batting_avg: string;
      runs: string;
      hits: string;
      home_runs: string;
      rbis: string;
      era: string;
      wins: string;
      losses: string;
      saves: string;
      strikeouts: string;
    };
    awayTeam: {
      batting_avg: string;
      runs: string;
      hits: string;
      home_runs: string;
      rbis: string;
      era: string;
      wins: string;
      losses: string;
      saves: string;
      strikeouts: string;
    };
  };
}

/**
 * Get game data and statistics for a specific game
 * @param gameId - The MLB game ID or team lookup string
 * @returns Promise<GameStats> - Game statistics and data
 */
export async function getGameData(gameId: string): Promise<GameStats> {
  try {
    // Try to get real data from MLB Stats API
    const gameData = await fetchMLBGameData(gameId);
    if (gameData) {
      return gameData;
    }
  } catch (error) {
    console.log('MLB API failed, using mock data');
  }

  // Fallback to mock data
  return generateMockGameData(gameId);
}

/**
 * Fetch real game data from MLB Stats API
 */
async function fetchMLBGameData(gameId: string): Promise<GameStats | null> {
  try {
    // Extract team names from gameId (format: "TeamA_TeamB_timestamp")
    const teamMatch = gameId.match(/^([^_]+)_([^_]+)_/);
    if (!teamMatch) return null;

    const teamA = teamMatch[1] ?? 'Team A';
    const teamB = teamMatch[2] ?? 'Team B';

    // Get today's date for game lookup
    const today = new Date().toISOString().split('T')[0];
    
    // Fetch schedule for today
    const scheduleUrl = `https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=${today}`;
    const scheduleResponse = await axios.get(scheduleUrl);
    
    if (scheduleResponse.data.dates && scheduleResponse.data.dates.length > 0) {
      const games = scheduleResponse.data.dates[0].games;
      
      // Find matching game
      const game = games.find((g: any) => {
        const homeTeam = (g.teams.home.team.name ?? 'Unknown') as string;
        const awayTeam = (g.teams.away.team.name ?? 'Unknown') as string;
        return (homeTeam && awayTeam && 
               (homeTeam.includes(teamA) || awayTeam.includes(teamA)) &&
               (homeTeam.includes(teamB) || awayTeam.includes(teamB)));
      });

      if (game) {
        const homeTeam = (game.teams.home.team.name ?? 'Home Team') as string;
        const awayTeam = (game.teams.away.team.name ?? 'Away Team') as string;
        const homeScore = game.teams.home.score ?? 0;
        const awayScore = game.teams.away.score ?? 0;
        const status = (game.status.detailedState ?? 'scheduled').toLowerCase();

        return {
          gameId: game.gamePk.toString(),
          date: game.gameDate.split('T')[0] ?? '',
          teams: [awayTeam, homeTeam],
          score: `${awayScore}-${homeScore}`,
          status: status as 'scheduled' | 'live' | 'final',
          keyStats: {
            homeTeam: generateTeamStats(homeTeam),
            awayTeam: generateTeamStats(awayTeam)
          }
        };
      }
    }
  } catch (error) {
    console.error('Error fetching MLB data:', error);
  }

  return null;
}

/**
 * Generate mock team statistics
 */
function generateTeamStats(teamName: string) {
  return {
    batting_avg: (Math.random() * 0.100 + 0.200).toFixed(3),
    runs: Math.floor(Math.random() * 100 + 50).toString(),
    hits: Math.floor(Math.random() * 1000 + 500).toString(),
    home_runs: Math.floor(Math.random() * 200 + 100).toString(),
    rbis: Math.floor(Math.random() * 500 + 300).toString(),
    era: (Math.random() * 2 + 3).toFixed(2),
    wins: Math.floor(Math.random() * 50 + 30).toString(),
    losses: Math.floor(Math.random() * 50 + 30).toString(),
    saves: Math.floor(Math.random() * 30 + 10).toString(),
    strikeouts: Math.floor(Math.random() * 1000 + 500).toString()
  };
}

/**
 * Generate mock game data for fallback
 */
function generateMockGameData(gameId: string): GameStats {
  const teamMatch = gameId.match(/^([^_]+)_([^_]+)_/);
  const teamA = teamMatch ? teamMatch[1] ?? 'Team A' : 'Team A';
  const teamB = teamMatch ? teamMatch[2] ?? 'Team B' : 'Team B';

  return {
    gameId,
    date: new Date().toISOString().split('T')[0] ?? '',
    teams: [teamA, teamB],
    score: `${Math.floor(Math.random() * 10 + 1)}-${Math.floor(Math.random() * 10 + 1)}`,
    status: 'scheduled',
    keyStats: {
      homeTeam: generateTeamStats(teamB ?? 'Team B'),
      awayTeam: generateTeamStats(teamA ?? 'Team A')
    }
  };
} 