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

  getDetailedGameData (_teamId) {
    // Placeholder for detailed game data
    return {
      teams: {
        away: { name: 'Team A' },
        home: { name: 'Team B' }
      },
      venue: 'Stadium Name',
      status: 'Scheduled',
      weather: {
        temperature: 72,
        condition: 'Partly Cloudy',
        windSpeed: 8
      }
    };
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
}

export const mlbService = new MLBService();
export const { getGameData } = mlbService;
