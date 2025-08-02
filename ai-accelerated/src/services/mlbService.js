import axios from 'axios';
import { logger } from '../utils/logger.js';

class MLBService {
  constructor () {
    this.baseUrl = 'https://statsapi.mlb.com/api/v1';
    this.cache = new Map();
    this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
  }

  async getGameData (leg) {
    try {
      const cacheKey = `${leg.teamA}-${leg.teamB}`;
      const cached = this.cache.get(cacheKey);

      if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
        logger.info('Using cached game data', { teams: cacheKey });
        return cached.data;
      }

      logger.info('Fetching game data', { teamA: leg.teamA, teamB: leg.teamB });

      // Get team IDs
      const teamAId = await this.getTeamId(leg.teamA);
      const teamBId = await this.getTeamId(leg.teamB);

      if (!teamAId || !teamBId) {
        throw new Error('Could not find team IDs');
      }

      // Get current game or recent games
      const gameData = await this.getGameInfo(teamAId, teamBId);

      // Cache the result
      this.cache.set(cacheKey, {
        data: gameData,
        timestamp: Date.now()
      });

      return gameData;

    } catch (error) {
      logger.error('Failed to get game data:', error);
      return null;
    }
  }

  async getTeamId (teamName) {
    try {
      // MLB API endpoint for teams
      const response = await axios.get(`${this.baseUrl}/teams`, {
        params: {
          sportIds: 1, // MLB
          fields: 'teams,id,name,abbreviation'
        },
        timeout: 5000
      });

      const teams = response.data.teams;

      // Try exact match first
      let team = teams.find(t =>
        t.name.toLowerCase() === teamName.toLowerCase() ||
        t.abbreviation.toLowerCase() === teamName.toLowerCase()
      );

      // Try partial match
      if (!team) {
        team = teams.find(t =>
          t.name.toLowerCase().includes(teamName.toLowerCase()) ||
          teamName.toLowerCase().includes(t.name.toLowerCase())
        );
      }

      return team ? team.id : null;

    } catch (error) {
      logger.error('Failed to get team ID:', error);
      return null;
    }
  }

  async getGameInfo (teamAId, teamBId) {
    try {
      // Get current date
      const today = new Date().toISOString().split('T')[0];

      // Get games for today
      const response = await axios.get(`${this.baseUrl}/schedule`, {
        params: {
          sportId: 1,
          date: today,
          fields: 'dates,games,gamePk,teams,away,home,status,detailedState'
        },
        timeout: 5000
      });

      const games = response.data.dates?.[0]?.games || [];

      // Find the specific game
      const game = games.find(g =>
        (g.teams.away.team.id === teamAId && g.teams.home.team.id === teamBId) ||
        (g.teams.away.team.id === teamBId && g.teams.home.team.id === teamAId)
      );

      if (game) {
        return this.getDetailedGameData(game.gamePk);
      }

      // If no current game, get recent games
      return await this.getRecentGames(teamAId, teamBId);

    } catch (error) {
      logger.error('Failed to get game info:', error);
      return null;
    }
  }

  async getRecentGames (teamAId, teamBId) {
    try {
      // Get recent games for both teams
      const response = await axios.get(`${this.baseUrl}/schedule`, {
        params: {
          sportId: 1,
          startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // Last 30 days
          endDate: new Date().toISOString().split('T')[0],
          fields: 'dates,games,gamePk,teams,away,home,status,detailedState'
        },
        timeout: 5000
      });

      const games = response.data.dates?.flatMap(date => date.games || []) || [];

      // Find games between these teams
      const teamGames = games.filter(g =>
        (g.teams.away.team.id === teamAId && g.teams.home.team.id === teamBId) ||
        (g.teams.away.team.id === teamBId && g.teams.home.team.id === teamAId)
      );

      return teamGames.slice(0, 5); // Return last 5 games

    } catch (error) {
      logger.error('Failed to get recent games:', error);
      return [];
    }
  }

  async getDetailedGameData(gamePk) {
    try {
      const response = await axios.get(`${this.baseUrl}/game/${gamePk}`);
      const gameData = response.data;
      const teams = gameData.teams || {};
      const venue = gameData.venue?.name || 'Unknown';
      const status = gameData.status?.detailedState || 'Unknown';
      const scheduledTime = gameData.gameDate || null;
      return {
        teams: {
          away: { name: teams.away?.team?.name || 'Away' },
          home: { name: teams.home?.team?.name || 'Home' }
        },
        venue,
        status,
        scheduledTime
      };
    } catch (error) {
      logger.error('Failed to fetch detailed game data:', error);
      return {
        teams: { away: { name: 'Team A' }, home: { name: 'Team B' } },
        venue: 'Stadium Name',
        status: 'Scheduled',
        scheduledTime: null
      };
    }
  }

  calculateTeamStats (games, _teamId) {
    // Calculate basic stats from recent games
    const stats = {
      wins: 0,
      losses: 0,
      runsScored: 0,
      runsAllowed: 0,
      avgRunsScored: 0,
      avgRunsAllowed: 0
    };

    if (games.length > 0) {
      // This is a simplified calculation
      // In production, you'd parse the actual game data
      stats.avgRunsScored = 4.5; // Placeholder
      stats.avgRunsAllowed = 4.2; // Placeholder
    }

    return stats;
  }

  // Get weather data for a game
  getWeatherData (_venue) {
    // This would integrate with a weather API
    // For now, return placeholder data
    return {
      temperature: 72,
      condition: 'Partly Cloudy',
      windSpeed: 8,
      humidity: 65
    };
  }

  // Get MLB player ID by name and team
  async getPlayerId(playerName, teamName) {
    try {
      const response = await axios.get(`${this.baseUrl}/people/search`, {
        params: { q: playerName },
        timeout: 5000
      });
      const people = response.data.people || [];
      // Try to match by team as well
      let player = people.find(p => p.fullName.toLowerCase() === playerName.toLowerCase() && p.currentTeam?.name?.toLowerCase() === teamName.toLowerCase());
      if (!player) {
        player = people.find(p => p.fullName.toLowerCase() === playerName.toLowerCase());
      }
      return player ? player.id : null;
    } catch (error) {
      logger.error('Failed to get player ID:', error);
      return null;
    }
  }

  // Get recent game logs for a pitcher
  async getPitcherGameLogs(playerId, numGames = 5) {
    try {
      const response = await axios.get(`${this.baseUrl}/people/${playerId}/stats`, {
        params: {
          stats: 'gameLog',
          group: 'pitching',
          season: new Date().getFullYear()
        },
        timeout: 5000
      });
      const logs = response.data.stats?.[0]?.splits || [];
      return logs.slice(0, numGames);
    } catch (error) {
      logger.error('Failed to get pitcher game logs:', error);
      return [];
    }
  }

  // Get key pitcher stats from game logs
  getPitcherStatsFromLogs(logs) {
    if (!logs.length) return null;
    let totalK = 0, totalIP = 0;
    const recentGames = logs.map(log => {
      const k = parseInt(log.stat.strikeOuts || 0, 10);
      const ip = parseFloat(log.stat.inningsPitched || 0);
      totalK += k;
      totalIP += ip;
      return {
        date: log.date,
        opponent: log.opponent?.name || '',
        strikeouts: k,
        innings: ip
      };
    });
    return {
      recentGames,
      avgK: +(totalK / logs.length).toFixed(2),
      avgIP: +(totalIP / logs.length).toFixed(2),
      totalK,
      totalIP
    };
  }

  // Get team stats for the current season
  async getTeamStats(teamId) {
    try {
      const response = await axios.get(`${this.baseUrl}/teams/${teamId}/stats`, {
        params: {
          stats: 'season',
          group: 'hitting,pitching',
          season: new Date().getFullYear()
        },
        timeout: 5000
      });
      const stats = response.data.stats || [];
      // Extract relevant stats
      const hitting = stats.find(s => s.group.displayName === 'hitting')?.splits?.[0]?.stat || {};
      const pitching = stats.find(s => s.group.displayName === 'pitching')?.splits?.[0]?.stat || {};
      return {
        hitting,
        pitching
      };
    } catch (error) {
      logger.error('Failed to get team stats:', error);
      return { hitting: {}, pitching: {} };
    }
  }

  // Get recent team game logs
  async getTeamGameLogs(teamId, numGames = 5) {
    try {
      const response = await axios.get(`${this.baseUrl}/teams/${teamId}/stats`, {
        params: {
          stats: 'gameLog',
          group: 'hitting,pitching',
          season: new Date().getFullYear()
        },
        timeout: 5000
      });
      const stats = response.data.stats || [];
      const hittingLogs = stats.find(s => s.group.displayName === 'hitting')?.splits || [];
      const pitchingLogs = stats.find(s => s.group.displayName === 'pitching')?.splits || [];
      return {
        hitting: hittingLogs.slice(0, numGames),
        pitching: pitchingLogs.slice(0, numGames)
      };
    } catch (error) {
      logger.error('Failed to get team game logs:', error);
      return { hitting: [], pitching: [] };
    }
  }

  // Get key team stats from logs
  getTeamStatsFromLogs(logs) {
    if (!logs.length) return null;
    let totalK = 0, totalPA = 0;
    logs.forEach(log => {
      const k = parseInt(log.stat.strikeOuts || 0, 10);
      const pa = parseInt(log.stat.plateAppearances || 0, 10);
      totalK += k;
      totalPA += pa;
    });
    return {
      avgK: +(totalK / logs.length).toFixed(2),
      avgPA: +(totalPA / logs.length).toFixed(2),
      kRate: totalPA ? +(totalK / totalPA * 100).toFixed(2) : null
    };
  }
}

export const mlbService = new MLBService();
export const { getGameData } = mlbService;
