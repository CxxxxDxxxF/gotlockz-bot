import Tesseract from 'tesseract.js';
import sharp from 'sharp';
import axios from 'axios';
import { logger } from '../utils/logger.js';

/**
 * OCR Service - Optimized for Fanatics Sportsbook bet slips
 * Extracts: Team names, spreads, odds, bet types
 */
class OCRService {
  constructor() {
    // Team name mappings - full names preferred per user preference
    this.teamMappings = {
      // MLB Teams
      'NYM': 'New York Mets', 'METS': 'New York Mets', 'NEW YORK METS': 'New York Mets',
      'NYY': 'New York Yankees', 'YANKEES': 'New York Yankees', 'NEW YORK YANKEES': 'New York Yankees',
      'ATL': 'Atlanta Braves', 'BRAVES': 'Atlanta Braves', 'ATLANTA BRAVES': 'Atlanta Braves',
      'BOS': 'Boston Red Sox', 'RED SOX': 'Boston Red Sox', 'BOSTON RED SOX': 'Boston Red Sox',
      'CHC': 'Chicago Cubs', 'CUBS': 'Chicago Cubs', 'CHICAGO CUBS': 'Chicago Cubs',
      'CHW': 'Chicago White Sox', 'WHITE SOX': 'Chicago White Sox', 'CHICAGO WHITE SOX': 'Chicago White Sox',
      'LAD': 'Los Angeles Dodgers', 'DODGERS': 'Los Angeles Dodgers', 'LOS ANGELES DODGERS': 'Los Angeles Dodgers',
      'LAA': 'Los Angeles Angels', 'ANGELS': 'Los Angeles Angels', 'LOS ANGELES ANGELS': 'Los Angeles Angels',
      'SF': 'San Francisco Giants', 'GIANTS': 'San Francisco Giants', 'SAN FRANCISCO GIANTS': 'San Francisco Giants',
      'SD': 'San Diego Padres', 'PADRES': 'San Diego Padres', 'SAN DIEGO PADRES': 'San Diego Padres',
      'PHI': 'Philadelphia Phillies', 'PHILLIES': 'Philadelphia Phillies', 'PHILADELPHIA PHILLIES': 'Philadelphia Phillies',
      'MIA': 'Miami Marlins', 'MARLINS': 'Miami Marlins', 'MIAMI MARLINS': 'Miami Marlins',
      'WSH': 'Washington Nationals', 'NATIONALS': 'Washington Nationals', 'WASHINGTON NATIONALS': 'Washington Nationals',
      'ARI': 'Arizona Diamondbacks', 'DIAMONDBACKS': 'Arizona Diamondbacks', 'ARIZONA DIAMONDBACKS': 'Arizona Diamondbacks',
      'COL': 'Colorado Rockies', 'ROCKIES': 'Colorado Rockies', 'COLORADO ROCKIES': 'Colorado Rockies',
      'HOU': 'Houston Astros', 'ASTROS': 'Houston Astros', 'HOUSTON ASTROS': 'Houston Astros',
      'TEX': 'Texas Rangers', 'RANGERS': 'Texas Rangers', 'TEXAS RANGERS': 'Texas Rangers',
      'OAK': 'Oakland Athletics', 'ATHLETICS': 'Oakland Athletics', 'OAKLAND ATHLETICS': 'Oakland Athletics',
      'SEA': 'Seattle Mariners', 'MARINERS': 'Seattle Mariners', 'SEATTLE MARINERS': 'Seattle Mariners',
      'MIN': 'Minnesota Twins', 'TWINS': 'Minnesota Twins', 'MINNESOTA TWINS': 'Minnesota Twins',
      'CLE': 'Cleveland Guardians', 'GUARDIANS': 'Cleveland Guardians', 'CLEVELAND GUARDIANS': 'Cleveland Guardians',
      'DET': 'Detroit Tigers', 'TIGERS': 'Detroit Tigers', 'DETROIT TIGERS': 'Detroit Tigers',
      'KC': 'Kansas City Royals', 'ROYALS': 'Kansas City Royals', 'KANSAS CITY ROYALS': 'Kansas City Royals',
      'TB': 'Tampa Bay Rays', 'RAYS': 'Tampa Bay Rays', 'TAMPA BAY RAYS': 'Tampa Bay Rays',
      'BAL': 'Baltimore Orioles', 'ORIOLES': 'Baltimore Orioles', 'BALTIMORE ORIOLES': 'Baltimore Orioles',
      'TOR': 'Toronto Blue Jays', 'BLUE JAYS': 'Toronto Blue Jays', 'TORONTO BLUE JAYS': 'Toronto Blue Jays',
      'CIN': 'Cincinnati Reds', 'REDS': 'Cincinnati Reds', 'CINCINNATI REDS': 'Cincinnati Reds',
      'MIL': 'Milwaukee Brewers', 'BREWERS': 'Milwaukee Brewers', 'MILWAUKEE BREWERS': 'Milwaukee Brewers',
      'PIT': 'Pittsburgh Pirates', 'PIRATES': 'Pittsburgh Pirates', 'PITTSBURGH PIRATES': 'Pittsburgh Pirates',
      'STL': 'St. Louis Cardinals', 'CARDINALS': 'St. Louis Cardinals', 'ST. LOUIS CARDINALS': 'St. Louis Cardinals',
      
      // NFL Teams
      'KC': 'Kansas City Chiefs', 'CHIEFS': 'Kansas City Chiefs', 'KANSAS CITY CHIEFS': 'Kansas City Chiefs',
      'BUF': 'Buffalo Bills', 'BILLS': 'Buffalo Bills', 'BUFFALO BILLS': 'Buffalo Bills',
      'MIA': 'Miami Dolphins', 'DOLPHINS': 'Miami Dolphins', 'MIAMI DOLPHINS': 'Miami Dolphins',
      'NE': 'New England Patriots', 'PATRIOTS': 'New England Patriots', 'NEW ENGLAND PATRIOTS': 'New England Patriots',
      'NYJ': 'New York Jets', 'JETS': 'New York Jets', 'NEW YORK JETS': 'New York Jets',
      'NYG': 'New York Giants', 'GIANTS': 'New York Giants', 'NEW YORK GIANTS': 'New York Giants',
      'BAL': 'Baltimore Ravens', 'RAVENS': 'Baltimore Ravens', 'BALTIMORE RAVENS': 'Baltimore Ravens',
      'CIN': 'Cincinnati Bengals', 'BENGALS': 'Cincinnati Bengals', 'CINCINNATI BENGALS': 'Cincinnati Bengals',
      'CLE': 'Cleveland Browns', 'BROWNS': 'Cleveland Browns', 'CLEVELAND BROWNS': 'Cleveland Browns',
      'PIT': 'Pittsburgh Steelers', 'STEELERS': 'Pittsburgh Steelers', 'PITTSBURGH STEELERS': 'Pittsburgh Steelers',
      'HOU': 'Houston Texans', 'TEXANS': 'Houston Texans', 'HOUSTON TEXANS': 'Houston Texans',
      'IND': 'Indianapolis Colts', 'COLTS': 'Indianapolis Colts', 'INDIANAPOLIS COLTS': 'Indianapolis Colts',
      'JAX': 'Jacksonville Jaguars', 'JAGUARS': 'Jacksonville Jaguars', 'JACKSONVILLE JAGUARS': 'Jacksonville Jaguars',
      'TEN': 'Tennessee Titans', 'TITANS': 'Tennessee Titans', 'TENNESSEE TITANS': 'Tennessee Titans',
      'DEN': 'Denver Broncos', 'BRONCOS': 'Denver Broncos', 'DENVER BRONCOS': 'Denver Broncos',
      'LV': 'Las Vegas Raiders', 'RAIDERS': 'Las Vegas Raiders', 'LAS VEGAS RAIDERS': 'Las Vegas Raiders',
      'LAC': 'Los Angeles Chargers', 'CHARGERS': 'Los Angeles Chargers', 'LOS ANGELES CHARGERS': 'Los Angeles Chargers',
      'DAL': 'Dallas Cowboys', 'COWBOYS': 'Dallas Cowboys', 'DALLAS COWBOYS': 'Dallas Cowboys',
      'PHI': 'Philadelphia Eagles', 'EAGLES': 'Philadelphia Eagles', 'PHILADELPHIA EAGLES': 'Philadelphia Eagles',
      'WAS': 'Washington Commanders', 'COMMANDERS': 'Washington Commanders', 'WASHINGTON COMMANDERS': 'Washington Commanders',
      'CHI': 'Chicago Bears', 'BEARS': 'Chicago Bears', 'CHICAGO BEARS': 'Chicago Bears',
      'DET': 'Detroit Lions', 'LIONS': 'Detroit Lions', 'DETROIT LIONS': 'Detroit Lions',
      'GB': 'Green Bay Packers', 'PACKERS': 'Green Bay Packers', 'GREEN BAY PACKERS': 'Green Bay Packers',
      'MIN': 'Minnesota Vikings', 'VIKINGS': 'Minnesota Vikings', 'MINNESOTA VIKINGS': 'Minnesota Vikings',
      'ATL': 'Atlanta Falcons', 'FALCONS': 'Atlanta Falcons', 'ATLANTA FALCONS': 'Atlanta Falcons',
      'CAR': 'Carolina Panthers', 'PANTHERS': 'Carolina Panthers', 'CAROLINA PANTHERS': 'Carolina Panthers',
      'NO': 'New Orleans Saints', 'SAINTS': 'New Orleans Saints', 'NEW ORLEANS SAINTS': 'New Orleans Saints',
      'TB': 'Tampa Bay Buccaneers', 'BUCCANEERS': 'Tampa Bay Buccaneers', 'TAMPA BAY BUCCANEERS': 'Tampa Bay Buccaneers',
      'ARI': 'Arizona Cardinals', 'CARDINALS': 'Arizona Cardinals', 'ARIZONA CARDINALS': 'Arizona Cardinals',
      'LAR': 'Los Angeles Rams', 'RAMS': 'Los Angeles Rams', 'LOS ANGELES RAMS': 'Los Angeles Rams',
      'SF': 'San Francisco 49ers', '49ERS': 'San Francisco 49ers', 'SAN FRANCISCO 49ERS': 'San Francisco 49ers',
      'SEA': 'Seattle Seahawks', 'SEAHAWKS': 'Seattle Seahawks', 'SEATTLE SEAHAWKS': 'Seattle Seahawks'
    };

    // Lines to ignore from Fanatics bet slips
    this.ignorePatterns = [
      /fanatics\s*sportsbook/i,
      /must\s*be\s*21\+/i,
      /gambling\s*problem/i,
      /1-800-gambler/i,
      /bet\s*id/i,
      /^\s*$/
    ];
  }

  async analyzeImage(imageUrl, debug = false) {
    const startTime = Date.now();

    try {
      logger.info('Starting OCR analysis', { imageUrl, debug });

      // Download and preprocess image
      const imageBuffer = await this.downloadImage(imageUrl);
      const processedBuffer = await this.preprocessImage(imageBuffer, debug);

      // Run Tesseract OCR
      const ocrResult = await this.runTesseract(processedBuffer, debug);

      if (!ocrResult || ocrResult.confidence < 0.3) {
        throw new Error('OCR confidence too low');
      }

      // Parse Fanatics bet slip format
      const betSlip = this.parseFanaticsBetSlip(ocrResult.text, debug);

      const time = Date.now() - startTime;

      logger.info('OCR analysis completed', {
        confidence: ocrResult.confidence,
        time: `${time}ms`,
        textLength: ocrResult.text.length
      });

      return {
        success: true,
        data: betSlip,
        confidence: ocrResult.confidence,
        time: time,
        rawText: ocrResult.text
      };

    } catch (error) {
      logger.error('OCR analysis failed:', error);
      return {
        success: false,
        error: error.message,
        time: Date.now() - startTime
      };
    }
  }

  async downloadImage(imageUrl) {
    const response = await axios.get(imageUrl, {
      responseType: 'arraybuffer',
      timeout: 15000
    });
    return Buffer.from(response.data);
  }

  async preprocessImage(imageBuffer, debug = false) {
    try {
      const processed = await sharp(imageBuffer)
        .resize(1400, null, { withoutEnlargement: true })
        .grayscale()
        .normalize()
        .sharpen()
        .png()
        .toBuffer();

      return processed;
    } catch (error) {
      logger.warn('Image preprocessing failed, using original:', error.message);
      return imageBuffer;
    }
  }

  async runTesseract(imageBuffer, debug = false) {
    const worker = await Tesseract.createWorker('eng');

    await worker.setParameters({
      tessedit_char_whitelist: '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-+/.()$%@ ',
      preserve_interword_spaces: '1'
    });

    const result = await worker.recognize(imageBuffer);
    await worker.terminate();

    if (debug) {
      logger.info('Tesseract raw result:', { text: result.data.text });
    }

    return {
      text: result.data.text,
      confidence: result.data.confidence / 100
    };
  }

  /**
   * Parse Fanatics Sportsbook bet slip format
   * Expected structure:
   * Line 1: "New York Mets -0.5" (team + spread)
   * Line 2: "Run Line - First 5 Innings" (bet type)
   * Line 3: "Atlanta Braves at New York Mets" (matchup)
   * Right side: "-160" (odds)
   */
  parseFanaticsBetSlip(text, debug = false) {
    const lines = text.split('\n')
      .map(line => line.trim())
      .filter(line => {
        // Skip empty lines and ignored patterns
        if (!line) return false;
        for (const pattern of this.ignorePatterns) {
          if (pattern.test(line)) return false;
        }
        return true;
      });

    if (debug) {
      logger.info('Filtered lines:', { lines });
    }

    const betSlip = {
      legs: [],
      rawLines: lines
    };

    // Look for odds pattern (+/-XXX)
    let odds = null;
    const oddsPattern = /([+-]\d{2,4})/;
    
    for (const line of lines) {
      const oddsMatch = line.match(oddsPattern);
      if (oddsMatch) {
        odds = oddsMatch[1];
      }
    }

    // Look for matchup pattern "Team at Team" or "Team vs Team"
    let matchup = null;
    let awayTeam = null;
    let homeTeam = null;
    
    const matchupPattern = /(.+?)\s+(?:at|@|vs\.?)\s+(.+)/i;
    
    for (const line of lines) {
      const matchupMatch = line.match(matchupPattern);
      if (matchupMatch && !line.includes('-') && !line.includes('+')) {
        // This is likely the matchup line (no spread numbers)
        awayTeam = this.normalizeTeamName(matchupMatch[1].trim());
        homeTeam = this.normalizeTeamName(matchupMatch[2].trim());
        matchup = `${awayTeam} @ ${homeTeam}`;
        break;
      }
    }

    // Look for pick line (team with spread/line) and bet type
    let pickLine = null;
    let betType = null;
    
    // First, look for bet type keywords in all lines
    const betTypeKeywords = [
      { pattern: /money\s*line/i, type: 'Money Line' },
      { pattern: /moneyline/i, type: 'Money Line' },
      { pattern: /run\s*line/i, type: 'Run Line' },
      { pattern: /spread/i, type: 'Spread' },
      { pattern: /first\s*5\s*innings/i, type: 'First 5 Innings' },
      { pattern: /first\s*half/i, type: 'First Half' },
      { pattern: /over\s+\d/i, type: 'Over' },
      { pattern: /under\s+\d/i, type: 'Under' },
      { pattern: /total/i, type: 'Total' },
      { pattern: /ml/i, type: 'Money Line' }
    ];
    
    for (const line of lines) {
      for (const { pattern, type } of betTypeKeywords) {
        if (pattern.test(line)) {
          betType = line.trim();
          break;
        }
      }
      if (betType) break;
    }
    
    // If no bet type found and we have just odds (no spread), it's a money line
    const hasSpread = lines.some(l => /[+-]\d+\.5/.test(l));
    if (!betType && !hasSpread) {
      betType = 'Money Line';
    }
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      
      // Check if line has a team name with a spread (e.g., "New York Mets -0.5")
      const spreadPattern = /(.+?)\s+([+-]?\d+\.?\d*)\s*$/;
      const spreadMatch = line.match(spreadPattern);
      
      if (spreadMatch) {
        const teamPart = spreadMatch[1].trim();
        const spreadPart = spreadMatch[2];
        
        // If spread is a whole number or has .5, it's a spread/run line
        if (/\.5/.test(spreadPart)) {
          pickLine = this.normalizeTeamName(teamPart) + ' ' + spreadPart;
          if (!betType) betType = 'Run Line';
        } else {
          pickLine = this.normalizeTeamName(teamPart) + ' ' + spreadPart;
        }
        break;
      }
      
      // Also check for moneyline (just team name with no spread but has odds)
      if (this.isTeamName(line) && !spreadPattern.test(line) && !matchupPattern.test(line)) {
        pickLine = this.normalizeTeamName(line);
        if (!betType) betType = 'Money Line';
        break;
      }
    }

    // Build the leg
    if (pickLine || matchup) {
      betSlip.legs.push({
        pickLine: pickLine || 'Pick not detected',
        betType: betType || '',
        matchup: matchup || 'Matchup not detected',
        awayTeam: awayTeam || 'Away Team',
        homeTeam: homeTeam || 'Home Team',
        odds: odds || 'N/A',
        fullPick: pickLine && betType 
          ? `${pickLine} ${betType} (${odds || 'N/A'})`
          : pickLine 
            ? `${pickLine} (${odds || 'N/A'})`
            : 'Pick not detected'
      });
    } else {
      // Fallback - couldn't parse properly
      betSlip.legs.push({
        pickLine: 'Could not parse pick',
        betType: '',
        matchup: 'Could not parse matchup',
        awayTeam: 'Team A',
        homeTeam: 'Team B',
        odds: odds || 'N/A',
        fullPick: 'Could not parse - check image quality',
        rawText: lines.join(' | ')
      });
    }

    if (debug) {
      logger.info('Parsed bet slip:', { betSlip });
    }

    return betSlip;
  }

  normalizeTeamName(name) {
    if (!name) return name;
    
    const upperName = name.toUpperCase().trim();
    
    // Check exact mapping first
    if (this.teamMappings[upperName]) {
      return this.teamMappings[upperName];
    }
    
    // Check partial matches
    for (const [key, fullName] of Object.entries(this.teamMappings)) {
      if (upperName.includes(key) || key.includes(upperName)) {
        return fullName;
      }
    }
    
    // Return original with proper casing
    return name.trim();
  }

  isTeamName(text) {
    if (!text) return false;
    const upperText = text.toUpperCase().trim();
    
    for (const key of Object.keys(this.teamMappings)) {
      if (upperText.includes(key)) {
        return true;
      }
    }
    return false;
  }
}

export const ocrService = new OCRService();
export const analyzeImage = (imageUrl, debug) => ocrService.analyzeImage(imageUrl, debug);
