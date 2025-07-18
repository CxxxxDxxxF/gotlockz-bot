import { logger } from '../utils/logger.js';

class BettingDataFormatter {
  constructor() {
    this.initialized = false;
  }

  async initialize() {
    if (this.initialized) return;
    this.initialized = true;
    logger.info('📊 Betting data formatter initialized');
  }

  async format(jsonData) {
    try {
      await this.initialize();
      
      // Validate input data
      if (!this.isValidInput(jsonData)) {
        throw new Error('Invalid betting data structure');
      }
      
      // Format the data
      const formatted = {
        gameId: this.generateGameId(jsonData),
        awayTeam: this.formatTeamName(jsonData.awayTeam || jsonData.teams?.away),
        homeTeam: this.formatTeamName(jsonData.homeTeam || jsonData.teams?.home),
        pick: this.formatPick(jsonData.pick || jsonData.recommendation),
        odds: this.formatOdds(jsonData.odds),
        confidence: this.formatConfidence(jsonData.confidence),
        analysis: this.formatAnalysis(jsonData.analysis),
        venue: this.formatVenue(jsonData.venue),
        gameTime: this.formatGameTime(jsonData.gameTime),
        broadcast: this.formatBroadcast(jsonData.broadcast),
        awayTeamLogo: jsonData.awayTeamLogo,
        homeTeamLogo: jsonData.homeTeamLogo,
        weather: this.formatWeather(jsonData.weather),
        stats: this.formatStats(jsonData.stats),
        timestamp: new Date().toISOString()
      };
      
      logger.debug('Betting data formatted successfully', { gameId: formatted.gameId });
      return formatted;
      
    } catch (error) {
      logger.error('Error formatting betting data:', error);
      throw error;
    }
  }

  isValidInput(data) {
    if (!data || typeof data !== 'object') {
      return false;
    }
    
    // Check for required fields
    const hasTeams = (data.awayTeam && data.homeTeam) || 
                    (data.teams && data.teams.away && data.teams.home);
    const hasPick = data.pick || data.recommendation;
    const hasAnalysis = data.analysis;
    
    return hasTeams && hasPick && hasAnalysis;
  }

  generateGameId(data) {
    const away = this.formatTeamName(data.awayTeam || data.teams?.away);
    const home = this.formatTeamName(data.homeTeam || data.teams?.home);
    const date = data.gameDate || new Date().toISOString().split('T')[0];
    
    return `${away}-${home}-${date}`.toLowerCase().replace(/\s+/g, '-');
  }

  formatTeamName(teamName) {
    if (!teamName) return 'Unknown Team';
    
    // Clean up team name
    let formatted = teamName.toString().trim();
    
    // Handle common abbreviations
    const teamMap = {
      'nyy': 'Yankees',
      'ny': 'Yankees',
      'bos': 'Red Sox',
      'lad': 'Dodgers',
      'la': 'Dodgers',
      'sf': 'Giants',
      'chc': 'Cubs',
      'cws': 'White Sox',
      'nym': 'Mets',
      'phi': 'Phillies',
      'atl': 'Braves',
      'mia': 'Marlins',
      'was': 'Nationals',
      'stl': 'Cardinals',
      'pit': 'Pirates',
      'cin': 'Reds',
      'mil': 'Brewers',
      'hou': 'Astros',
      'tex': 'Rangers',
      'laa': 'Angels',
      'oak': 'Athletics',
      'sea': 'Mariners',
      'tor': 'Blue Jays',
      'bal': 'Orioles',
      'tb': 'Rays',
      'det': 'Tigers',
      'cle': 'Indians',
      'kc': 'Royals',
      'min': 'Twins',
      'col': 'Rockies',
      'ari': 'Diamondbacks',
      'sd': 'Padres'
    };
    
    const lowerTeam = formatted.toLowerCase();
    if (teamMap[lowerTeam]) {
      formatted = teamMap[lowerTeam];
    }
    
    return formatted;
  }

  formatPick(pick) {
    if (!pick) return 'No pick available';
    
    let formatted = pick.toString().trim();
    
    // Add emoji based on pick type
    if (formatted.toLowerCase().includes('over')) {
      formatted = `📈 ${formatted}`;
    } else if (formatted.toLowerCase().includes('under')) {
      formatted = `📉 ${formatted}`;
    } else if (formatted.toLowerCase().includes('ml')) {
      formatted = `💰 ${formatted}`;
    } else if (formatted.toLowerCase().includes('spread')) {
      formatted = `📊 ${formatted}`;
    } else {
      formatted = `🎯 ${formatted}`;
    }
    
    return formatted;
  }

  formatOdds(odds) {
    if (!odds) return 'TBD';
    
    let formatted = odds.toString().trim();
    
    // Add emoji
    if (formatted.startsWith('+')) {
      formatted = `🟢 ${formatted}`;
    } else if (formatted.startsWith('-')) {
      formatted = `🔴 ${formatted}`;
    } else {
      formatted = `⚪ ${formatted}`;
    }
    
    return formatted;
  }

  formatConfidence(confidence) {
    if (!confidence) return 'Medium';
    
    let formatted = confidence.toString().trim();
    const num = parseFloat(formatted);
    
    if (!isNaN(num)) {
      if (num >= 80) {
        formatted = `🔥 High (${num}%)`;
      } else if (num >= 60) {
        formatted = `⚡ Medium (${num}%)`;
      } else {
        formatted = `⚠️ Low (${num}%)`;
      }
    } else {
      // Handle text-based confidence
      const lower = formatted.toLowerCase();
      if (lower.includes('high') || lower.includes('strong')) {
        formatted = `🔥 High`;
      } else if (lower.includes('medium') || lower.includes('moderate')) {
        formatted = `⚡ Medium`;
      } else if (lower.includes('low') || lower.includes('weak')) {
        formatted = `⚠️ Low`;
      } else {
        formatted = `⚡ ${formatted}`;
      }
    }
    
    return formatted;
  }

  formatAnalysis(analysis) {
    if (!analysis) return 'Analysis not available';
    
    let formatted = analysis.toString().trim();
    
    // Clean up the analysis text
    formatted = formatted.replace(/\n+/g, '\n');
    formatted = formatted.replace(/\s+/g, ' ');
    
    // Limit length for Discord
    if (formatted.length > 1000) {
      formatted = formatted.substring(0, 997) + '...';
    }
    
    return formatted;
  }

  formatVenue(venue) {
    if (!venue) return 'TBD';
    return venue.toString().trim();
  }

  formatGameTime(gameTime) {
    if (!gameTime) return 'TBD';
    
    try {
      const date = new Date(gameTime);
      if (isNaN(date.getTime())) {
        return gameTime.toString().trim();
      }
      
      return date.toLocaleString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        timeZoneName: 'short'
      });
    } catch {
      return gameTime.toString().trim();
    }
  }

  formatBroadcast(broadcast) {
    if (!broadcast) return 'TBD';
    
    let formatted = broadcast.toString().trim();
    
    // Add network emoji
    if (formatted.toLowerCase().includes('espn')) {
      formatted = `📺 ESPN`;
    } else if (formatted.toLowerCase().includes('fox')) {
      formatted = `📺 FOX`;
    } else if (formatted.toLowerCase().includes('mlb')) {
      formatted = `📺 MLB Network`;
    } else if (formatted.toLowerCase().includes('tbs')) {
      formatted = `📺 TBS`;
    } else {
      formatted = `📺 ${formatted}`;
    }
    
    return formatted;
  }

  formatWeather(weather) {
    if (!weather) return null;
    
    if (typeof weather === 'string') {
      return weather;
    }
    
    if (typeof weather === 'object') {
      const parts = [];
      if (weather.temperature) parts.push(`${weather.temperature}°F`);
      if (weather.condition) parts.push(weather.condition);
      if (weather.wind) parts.push(`Wind: ${weather.wind}`);
      
      return parts.join(', ');
    }
    
    return weather.toString();
  }

  formatStats(stats) {
    if (!stats) return null;
    
    if (typeof stats === 'string') {
      return stats;
    }
    
    if (typeof stats === 'object') {
      return Object.entries(stats)
        .map(([key, value]) => `${key}: ${value}`)
        .join(', ');
    }
    
    return stats.toString();
  }
}

export const bettingDataFormatter = new BettingDataFormatter(); 