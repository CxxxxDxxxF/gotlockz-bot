import axios from 'axios';
import { logger } from '../utils/logger.js';

/**
 * ESPN Service - Fetches game times and schedules
 */
class ESPNService {
  constructor() {
    this.nflUrl = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard';
    this.mlbUrl = 'https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard';
    this.cache = new Map();
    this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
  }

  async getGameTime(awayTeam, homeTeam, sport = 'auto') {
    try {
      const cacheKey = `${awayTeam}-${homeTeam}`.toLowerCase();
      const cached = this.cache.get(cacheKey);
      
      if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }

      // Try NFL first if sport is auto or nfl
      if (sport === 'auto' || sport === 'nfl') {
        const nflGame = await this.searchGames(this.nflUrl, awayTeam, homeTeam);
        if (nflGame) {
          this.cache.set(cacheKey, { data: nflGame, timestamp: Date.now() });
          return nflGame;
        }
      }

      // Try MLB if sport is auto or mlb
      if (sport === 'auto' || sport === 'mlb') {
        const mlbGame = await this.searchGames(this.mlbUrl, awayTeam, homeTeam);
        if (mlbGame) {
          this.cache.set(cacheKey, { data: mlbGame, timestamp: Date.now() });
          return mlbGame;
        }
      }

      return null;
    } catch (error) {
      logger.error('ESPN API error:', error);
      return null;
    }
  }

  async searchGames(url, awayTeam, homeTeam) {
    try {
      const response = await axios.get(url, { timeout: 10000 });
      const events = response.data.events || [];

      for (const event of events) {
        const competitors = event.competitions?.[0]?.competitors || [];
        
        if (competitors.length >= 2) {
          const teams = competitors.map(c => c.team?.displayName?.toLowerCase() || '');
          const awayLower = awayTeam.toLowerCase();
          const homeLower = homeTeam.toLowerCase();

          // Check if both teams match
          const matchesAway = teams.some(t => t.includes(awayLower) || awayLower.includes(t));
          const matchesHome = teams.some(t => t.includes(homeLower) || homeLower.includes(t));

          if (matchesAway || matchesHome) {
            const gameDate = new Date(event.date);
            const formattedDate = this.formatDateTime(gameDate);
            
            return {
              date: formattedDate.date,
              time: formattedDate.time,
              fullDateTime: formattedDate.full,
              venue: event.competitions?.[0]?.venue?.fullName || null,
              status: event.status?.type?.description || 'Scheduled',
              awayTeam: competitors.find(c => c.homeAway === 'away')?.team?.displayName,
              homeTeam: competitors.find(c => c.homeAway === 'home')?.team?.displayName
            };
          }
        }
      }

      return null;
    } catch (error) {
      logger.error('ESPN search error:', error);
      return null;
    }
  }

  formatDateTime(date) {
    const options = { 
      timeZone: 'America/New_York',
      month: 'numeric',
      day: 'numeric',
      year: '2-digit',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    };

    const formatted = date.toLocaleString('en-US', options);
    const parts = formatted.split(', ');
    
    return {
      date: parts[0] || '',
      time: (parts[1] || '').replace(' ', '') + ' EST',
      full: formatted + ' EST'
    };
  }
}

export const espnService = new ESPNService();
export const getGameTime = (awayTeam, homeTeam, sport) => 
  espnService.getGameTime(awayTeam, homeTeam, sport);

