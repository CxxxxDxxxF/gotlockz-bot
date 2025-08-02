// MLB team mapping (name, abbr, city)
export const MLB_TEAMS = [
  { name: 'Los Angeles Angels', abbr: 'LAA', city: 'Anaheim' },
  { name: 'Oakland Athletics', abbr: 'OAK', city: 'Oakland' },
  { name: 'New York Yankees', abbr: 'NYY', city: 'New York' },
  { name: 'Boston Red Sox', abbr: 'BOS', city: 'Boston' },
  { name: 'Houston Astros', abbr: 'HOU', city: 'Houston' },
  { name: 'Los Angeles Dodgers', abbr: 'LAD', city: 'Los Angeles' },
  { name: 'San Francisco Giants', abbr: 'SF', city: 'San Francisco' },
  { name: 'Colorado Rockies', abbr: 'COL', city: 'Denver' },
  { name: 'Chicago Cubs', abbr: 'CHC', city: 'Chicago' },
  { name: 'Chicago White Sox', abbr: 'CWS', city: 'Chicago' },
  { name: 'Cleveland Guardians', abbr: 'CLE', city: 'Cleveland' },
  { name: 'Detroit Tigers', abbr: 'DET', city: 'Detroit' },
  { name: 'Kansas City Royals', abbr: 'KC', city: 'Kansas City' },
  { name: 'Minnesota Twins', abbr: 'MIN', city: 'Minneapolis' },
  { name: 'Baltimore Orioles', abbr: 'BAL', city: 'Baltimore' },
  { name: 'Tampa Bay Rays', abbr: 'TB', city: 'Tampa Bay' },
  { name: 'Toronto Blue Jays', abbr: 'TOR', city: 'Toronto' },
  { name: 'Atlanta Braves', abbr: 'ATL', city: 'Atlanta' },
  { name: 'Miami Marlins', abbr: 'MIA', city: 'Miami' },
  { name: 'New York Mets', abbr: 'NYM', city: 'New York' },
  { name: 'Philadelphia Phillies', abbr: 'PHI', city: 'Philadelphia' },
  { name: 'Washington Nationals', abbr: 'WSH', city: 'Washington' },
  { name: 'Arizona Diamondbacks', abbr: 'ARI', city: 'Phoenix' },
  { name: 'San Diego Padres', abbr: 'SD', city: 'San Diego' },
  { name: 'Seattle Mariners', abbr: 'SEA', city: 'Seattle' },
  { name: 'Texas Rangers', abbr: 'TEX', city: 'Arlington' },
  { name: 'Cincinnati Reds', abbr: 'CIN', city: 'Cincinnati' },
  { name: 'Milwaukee Brewers', abbr: 'MIL', city: 'Milwaukee' },
  { name: 'Pittsburgh Pirates', abbr: 'PIT', city: 'Pittsburgh' },
  { name: 'St. Louis Cardinals', abbr: 'STL', city: 'St. Louis' },
];

/**
 * Attempts to match a string to an MLB team (by name or abbreviation).
 * @param {string} text
 * @returns {object|null} Team object or null
 */
export function matchMLBTeam(text) {
  const cleaned = text.trim().toLowerCase();
  return (
    MLB_TEAMS.find(t =>
      cleaned === t.name.toLowerCase() ||
      cleaned === t.abbr.toLowerCase() ||
      cleaned.includes(t.name.toLowerCase()) ||
      cleaned.includes(t.abbr.toLowerCase())
    ) || null
  );
}

// Example list of common bet types (expand as needed)
export const BET_TYPES = [
  'ML', 'RL', 'O/U', 'OU', 'UNDER', 'OVER', 'TOTAL', 'SPREAD', 'ALT', 'PROP', 'HITS', 'HR', 'RBI', 'RUNS', 'STRIKEOUTS', 'WALKS', 'STEALS', 'WIN', 'SAVE', 'NO-HITTER', 'SHUTOUT'
];

/**
 * Attempts to extract player names from OCR text.
 * @param {string} ocrText
 * @returns {string[]} Array of player names (best effort)
 */
export function extractPlayers(ocrText) {
  // This is a placeholder. You may want to use a list of MLB players or regex for capitalized words.
  // Example: Find capitalized words not matching teams or bet types.
  const words = ocrText.split(/\s+/);
  const teamAbbrs = MLB_TEAMS.map(t => t.abbr);
  const betTypes = BET_TYPES.map(t => t.toUpperCase());
  return words.filter(w => {
    if (w.length < 3) return false;
    if (teamAbbrs.includes(w)) return false;
    if (betTypes.includes(w.toUpperCase())) return false;
    // Heuristic: likely a player if capitalized and not a team/bet type
    return /^[A-Z][a-z]+$/.test(w);
  });
}

/**
 * Attempts to extract bet units (e.g., 1u, 2U, 0.5u, 5 units) from OCR text.
 * @param {string} ocrText
 * @returns {number|null} Units wagered, or null if not found
 */
export function extractUnits(ocrText) {
  // Look for patterns like 1u, 2U, 0.5u, 5 units
  const match = ocrText.match(/(\d+(?:\.\d+)?)[ ]?(u|units)/i);
  if (match) return parseFloat(match[1]);
  return null;
}

/**
 * Parses OCR text into structured bet slip data.
 * Extracts teams, odds, bet type, home/away, players, and units.
 * @param {string} ocrText - The OCR text to parse
 * @returns {object} Parsed bet slip info
 */
export function parseBetSlip(ocrText) {
  // Handle null/undefined input
  if (!ocrText) {
    return {
      teams: [],
      odds: null,
      betType: null,
      homeTeam: null,
      awayTeam: null,
      players: [],
      units: null,
      playerProp: null
    };
  }

  // Unwanted phrases to filter out
  const UNWANTED_PHRASES = [
    'fanatics sportsbook',
    'fanatics',
    'sportsbook',
    'bet id',
    'must be 21+',
    'gambling problem',
    'call',
    '1-800-gambler',
    'rg'
  ];

  // Normalize and split lines, filter unwanted
  const lines = ocrText
    .split(/\r?\n/)
    .map(l => l.trim())
    .filter(Boolean)
    .filter(line => !UNWANTED_PHRASES.some(phrase => line.toLowerCase().includes(phrase)));

  let teams = [];
  let odds = null;
  let betType = null;
  let homeTeam = null;
  let awayTeam = null;
  let players = extractPlayers(ocrText);
  let units = extractUnits(ocrText);
  let playerProp = null;

  // Helper to get full team name from abbr or name
  function getFullTeamName(str) {
    const cleaned = str.trim().toLowerCase();
    const team = MLB_TEAMS.find(t =>
      cleaned === t.abbr.toLowerCase() ||
      cleaned === t.name.toLowerCase() ||
      cleaned.includes(t.abbr.toLowerCase()) ||
      cleaned.includes(t.name.toLowerCase())
    );
    return team ? team.name : str;
  }

  // Try to find teams by matching known names/abbreviations
  for (const line of lines) {
    for (const team of MLB_TEAMS) {
      if (
        line.includes(team.abbr) ||
        line.toLowerCase().includes(team.name.toLowerCase())
      ) {
        const fullName = team.name;
        if (!teams.includes(fullName)) teams.push(fullName);
      }
    }
  }

  // Odds: look for patterns like -120, +150, etc.
  const oddsMatch = ocrText.match(/([+-]?\d{3,4})/);
  if (oddsMatch) odds = parseInt(oddsMatch[1], 10);

  // Bet type: look for any in BET_TYPES
  for (const type of BET_TYPES) {
    const regex = new RegExp(`\\b${type.replace(/\//g, '[\\/]')}\\b`, 'i');
    if (regex.test(ocrText)) {
      betType = type;
      break;
    }
  }

  // Home/Away: look for 'at', then 'vs' or '@'
  for (const line of lines) {
    if (/\bat\b/i.test(line)) {
      const [a, b] = line.split(/\bat\b/i).map(s => s.trim());
      awayTeam = getFullTeamName(a) || null;
      homeTeam = getFullTeamName(b) || null;
    } else if (line.includes('vs')) {
      const [a, b] = line.split('vs').map(s => s.trim());
      homeTeam = getFullTeamName(b) || null;
      awayTeam = getFullTeamName(a) || null;
    } else if (line.includes('@')) {
      const [a, b] = line.split('@').map(s => s.trim());
      homeTeam = getFullTeamName(b) || null;
      awayTeam = getFullTeamName(a) || null;
    }
  }

  // Player prop extraction: look for lines like 'Cristopher Sanchez 6+ Strikeouts' or 'ALT Strikeouts'
  for (const line of lines) {
    // Player prop pattern: [Player Name] [Number][+] [Stat/Prop]
    const playerPropMatch = line.match(/([A-Z][a-z]+(?: [A-Z][a-z]+)+)\s+(\d+\+?)\s+([A-Za-z ]+)/);
    if (playerPropMatch) {
      playerProp = {
        player: playerPropMatch[1].trim(),
        value: playerPropMatch[2].trim(),
        stat: playerPropMatch[3].trim()
      };
      break;
    }
    // ALT Strikeouts pattern (e.g., 'ALT Strikeouts')
    if (/ALT Strikeouts/i.test(line)) {
      if (!playerProp) playerProp = {};
      playerProp.stat = 'Strikeouts';
    }
  }

  return {
    teams,
    odds,
    betType,
    homeTeam,
    awayTeam,
    players,
    units,
    playerProp
  };
} 