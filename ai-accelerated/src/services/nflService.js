import axios from 'axios';
import { logger } from '../utils/logger.js';

/**
 * NFL Service - Fetches comprehensive NFL stats from ESPN API
 * Includes offense/defense rankings, player stats, and matchup data
 */
class NFLService {
  constructor() {
    this.baseUrl = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl';
    this.statsUrl = 'https://sports.core.api.espn.com/v2/sports/football/leagues/nfl';
    this.cache = new Map();
    this.cacheTimeout = 10 * 60 * 1000; // 10 minutes
  }

  async getDetailedTeamStats(teamName) {
    try {
      const cacheKey = `detailed_${teamName}`.toLowerCase();
      const cached = this.cache.get(cacheKey);
      
      if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }

      const teamId = await this.findTeamId(teamName);
      if (!teamId) {
        logger.warn(`Could not find NFL team: ${teamName}`);
        return null;
      }

      // Fetch multiple data sources in parallel
      const [teamInfo, teamStats, roster] = await Promise.all([
        this.getTeamInfo(teamId),
        this.getTeamStatistics(teamId),
        this.getKeyPlayers(teamId)
      ]);

      const stats = {
        name: teamInfo?.displayName || teamName,
        abbreviation: teamInfo?.abbreviation,
        record: teamInfo?.record,
        standings: teamInfo?.standings,
        offense: teamStats?.offense || {},
        defense: teamStats?.defense || {},
        rankings: teamStats?.rankings || {},
        statLeaders: roster || [],  // These are actual stat leaders, not just roster
        homeRecord: teamInfo?.homeRecord,
        awayRecord: teamInfo?.awayRecord
      };

      this.cache.set(cacheKey, { data: stats, timestamp: Date.now() });
      return stats;

    } catch (error) {
      logger.error('NFL detailed stats error:', error.message);
      return null;
    }
  }

  async findTeamId(teamName) {
    try {
      const teamsUrl = `${this.baseUrl}/teams`;
      const response = await axios.get(teamsUrl, { timeout: 10000 });
      
      const teams = response.data.sports?.[0]?.leagues?.[0]?.teams || [];
      const searchName = teamName.toLowerCase();
      
      for (const teamWrapper of teams) {
        const team = teamWrapper.team;
        const name = team.displayName?.toLowerCase() || '';
        const shortName = team.shortDisplayName?.toLowerCase() || '';
        const nickname = team.nickname?.toLowerCase() || '';
        const location = team.location?.toLowerCase() || '';
        
        if (name.includes(searchName) || searchName.includes(name) ||
            shortName.includes(searchName) || searchName.includes(shortName) ||
            nickname.includes(searchName) || searchName.includes(nickname) ||
            location.includes(searchName) || searchName.includes(location)) {
          return team.id;
        }
      }
      
      return null;
    } catch (error) {
      logger.error('NFL find team error:', error.message);
      return null;
    }
  }

  async getTeamInfo(teamId) {
    try {
      const url = `${this.baseUrl}/teams/${teamId}`;
      const response = await axios.get(url, { timeout: 10000 });
      const team = response.data.team;
      
      // Extract record
      let record = null;
      let homeRecord = null;
      let awayRecord = null;
      let standings = null;
      
      if (team.record?.items) {
        for (const item of team.record.items) {
          if (item.type === 'total') {
            record = item.summary;
          } else if (item.type === 'home') {
            homeRecord = item.summary;
          } else if (item.type === 'road') {
            awayRecord = item.summary;
          }
        }
      }

      if (team.standingSummary) {
        standings = team.standingSummary;
      }

      return {
        displayName: team.displayName,
        abbreviation: team.abbreviation,
        record,
        homeRecord,
        awayRecord,
        standings
      };
    } catch (error) {
      logger.error('NFL team info error:', error.message);
      return null;
    }
  }

  async getTeamStatistics(teamId) {
    try {
      const url = `${this.baseUrl}/teams/${teamId}/statistics`;
      const response = await axios.get(url, { timeout: 10000 });
      
      const stats = {
        offense: {},
        defense: {},
        rankings: {}
      };

      const categories = response.data.results?.stats?.categories || [];
      
      for (const category of categories) {
        const catName = category.name?.toLowerCase() || '';
        const catDisplayName = category.displayName || category.name;
        
        for (const stat of category.stats || []) {
          const statName = stat.displayName || stat.name;
          const value = stat.displayValue || stat.value;
          const rank = stat.rank || stat.rankDisplayValue;
          
          // Categorize stats
          if (catName.includes('passing') || catName.includes('rushing') || 
              catName.includes('receiving') || catName.includes('scoring')) {
            stats.offense[statName] = { value, rank };
          } else if (catName.includes('defense') || catName.includes('interceptions') ||
                     catName.includes('fumbles') || catName.includes('tackles')) {
            stats.defense[statName] = { value, rank };
          }
          
          // Track key rankings
          if (rank) {
            stats.rankings[`${catDisplayName} - ${statName}`] = rank;
          }
        }
      }

      return stats;
    } catch (error) {
      logger.error('NFL team statistics error:', error.message);
      return { offense: {}, defense: {}, rankings: {} };
    }
  }

  async getKeyPlayers(teamId) {
    try {
      // Get team STAT LEADERS instead of just roster
      const url = `${this.baseUrl}/teams/${teamId}`;
      const response = await axios.get(url, { timeout: 10000 });
      
      const leaders = [];
      const team = response.data.team;
      
      // Get the actual stat leaders
      if (team.leaders) {
        for (const leaderCategory of team.leaders) {
          const categoryName = leaderCategory.name; // e.g., "passingYards", "rushingYards", "receivingYards"
          const topLeader = leaderCategory.leaders?.[0];
          
          if (topLeader?.athlete) {
            leaders.push({
              category: this.formatLeaderCategory(categoryName),
              name: topLeader.athlete.displayName || topLeader.athlete.fullName,
              position: topLeader.athlete.position?.abbreviation,
              stat: topLeader.displayValue || topLeader.value,
              statLabel: leaderCategory.displayName
            });
          }
        }
      }
      
      return leaders;
    } catch (error) {
      logger.error('NFL stat leaders error:', error.message);
      return [];
    }
  }

  formatLeaderCategory(category) {
    const mapping = {
      'passingYards': 'Passing Leader',
      'passingTouchdowns': 'Passing TDs Leader',
      'rushingYards': 'Rushing Leader',
      'rushingTouchdowns': 'Rushing TDs Leader',
      'receivingYards': 'Receiving Leader',
      'receivingTouchdowns': 'Receiving TDs Leader',
      'sacks': 'Sacks Leader',
      'interceptions': 'Interceptions Leader',
      'tackles': 'Tackles Leader'
    };
    return mapping[category] || category;
  }

  async getMatchupData(awayTeam, homeTeam) {
    try {
      logger.info('Fetching comprehensive NFL matchup data', { awayTeam, homeTeam });

      // Fetch detailed stats for both teams in parallel
      const [awayStats, homeStats, gameInfo] = await Promise.all([
        this.getDetailedTeamStats(awayTeam),
        this.getDetailedTeamStats(homeTeam),
        this.getGameInfo(awayTeam, homeTeam)
      ]);

      // Build matchup analysis
      const matchup = {
        awayTeam: awayStats || { name: awayTeam },
        homeTeam: homeStats || { name: homeTeam },
        gameInfo: gameInfo,
        sportType: 'nfl',
        
        // Pre-calculate key matchups for AI
        keyMatchups: this.analyzeMatchups(awayStats, homeStats)
      };

      return matchup;

    } catch (error) {
      logger.error('NFL matchup data error:', error.message);
      return null;
    }
  }

  analyzeMatchups(awayStats, homeStats) {
    const matchups = [];
    
    try {
      // Compare passing offense vs pass defense
      const awayPassOff = awayStats?.offense?.['Passing Yards Per Game']?.value;
      const homePassDef = homeStats?.defense?.['Passing Yards Per Game']?.value;
      if (awayPassOff && homePassDef) {
        matchups.push(`${awayStats.name} passing (${awayPassOff} YPG) vs ${homeStats.name} pass defense (${homePassDef} YPG allowed)`);
      }

      // Compare rushing offense vs rush defense  
      const awayRushOff = awayStats?.offense?.['Rushing Yards Per Game']?.value;
      const homeRushDef = homeStats?.defense?.['Rushing Yards Per Game']?.value;
      if (awayRushOff && homeRushDef) {
        matchups.push(`${awayStats.name} rushing (${awayRushOff} YPG) vs ${homeStats.name} rush defense (${homeRushDef} YPG allowed)`);
      }

      // Vice versa for home team
      const homePassOff = homeStats?.offense?.['Passing Yards Per Game']?.value;
      const awayPassDef = awayStats?.defense?.['Passing Yards Per Game']?.value;
      if (homePassOff && awayPassDef) {
        matchups.push(`${homeStats.name} passing (${homePassOff} YPG) vs ${awayStats.name} pass defense (${awayPassDef} YPG allowed)`);
      }

      const homeRushOff = homeStats?.offense?.['Rushing Yards Per Game']?.value;
      const awayRushDef = awayStats?.defense?.['Rushing Yards Per Game']?.value;
      if (homeRushOff && awayRushDef) {
        matchups.push(`${homeStats.name} rushing (${homeRushOff} YPG) vs ${awayStats.name} rush defense (${awayRushDef} YPG allowed)`);
      }

    } catch (error) {
      logger.error('Matchup analysis error:', error.message);
    }

    return matchups;
  }

  async getGameInfo(awayTeam, homeTeam) {
    try {
      const scoreboardUrl = `${this.baseUrl}/scoreboard`;
      const response = await axios.get(scoreboardUrl, { timeout: 10000 });
      
      const events = response.data.events || [];
      
      for (const event of events) {
        const competitors = event.competitions?.[0]?.competitors || [];
        const teamNames = competitors.map(c => c.team?.displayName?.toLowerCase() || '');
        
        const awayLower = awayTeam.toLowerCase();
        const homeLower = homeTeam.toLowerCase();
        
        const matchesAway = teamNames.some(t => t.includes(awayLower) || awayLower.includes(t));
        const matchesHome = teamNames.some(t => t.includes(homeLower) || homeLower.includes(t));
        
        if (matchesAway || matchesHome) {
          return {
            date: event.date,
            venue: event.competitions?.[0]?.venue?.fullName,
            broadcast: event.competitions?.[0]?.broadcasts?.[0]?.names?.join(', '),
            weather: event.weather,
            odds: event.competitions?.[0]?.odds?.[0]
          };
        }
      }
      
      return null;
    } catch (error) {
      logger.error('NFL game info error:', error.message);
      return null;
    }
  }
}

export const nflService = new NFLService();
export const getMatchupData = (awayTeam, homeTeam) => nflService.getMatchupData(awayTeam, homeTeam);
