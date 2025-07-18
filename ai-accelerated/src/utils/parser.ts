/**
 * Bet Slip Parser - Parse OCR text into structured betting data
 */

export interface BetLeg {
  gameId: string;
  teamA: string;
  teamB: string;
  odds: number;
}

export interface BetSlip {
  legs: BetLeg[];
  units: number;
  type: 'SINGLE' | 'PARLAY';
}

/**
 * Parse OCR text lines into a structured BetSlip
 * @param textLines - Array of text lines from OCR
 * @returns Promise<BetSlip> - Parsed betting slip data
 */
export async function parseBetSlip(textLines: string[]): Promise<BetSlip> {
  console.log('🔍 Starting bet slip parsing...');
  console.log('📄 Input text lines:', textLines);
  
  const text = textLines.join('\n').toUpperCase();
  console.log('📝 Combined text:', text);
  
  // Detect if this is a parlay/SGP
  const isParlay = text.includes('PARLAY') || text.includes('MULTIPLE') || text.includes('LEG') || text.includes('SGP');
  console.log('🎯 Is parlay:', isParlay);
  
  // Extract units (bet amount)
  const unitsMatch = text.match(/(\d+(?:\.\d+)?)\s*(?:UNIT|U|DOLLAR|USD|\$)/i);
  const units = unitsMatch && unitsMatch[1] ? parseFloat(unitsMatch[1]) : 1;
  console.log('💰 Units found:', units);
  
  // Extract legs using comprehensive parsing
  const legs: BetLeg[] = [];
  
  if (isParlay) {
    // Parse multi-leg parlay/SGP
    console.log('🎲 Parsing multi-leg parlay/SGP...');
    const parlayLegs = parseMultiLegParlay(textLines);
    legs.push(...parlayLegs);
  } else {
    // Parse single bet
    console.log('🎲 Parsing single bet...');
    const singleLeg = parseSingleBet(text);
    if (singleLeg) {
      legs.push(singleLeg);
    }
  }
  
  console.log('🎯 Legs found:', legs.length);
  
  // If no legs found, try fallback parsing
  if (legs.length === 0) {
    console.log('🔄 No legs found, trying fallback parsing...');
    const fallbackLegs = parseFallbackLegs(textLines);
    legs.push(...fallbackLegs);
    console.log('✅ Fallback legs found:', fallbackLegs.length);
  }
  
  const result: BetSlip = {
    legs,
    units,
    type: legs.length > 1 ? 'PARLAY' : 'SINGLE'
  };
  
  console.log('📊 Final parsed result:', result);
  return result;
}

/**
 * Parse multi-leg parlay/SGP from text lines
 */
function parseMultiLegParlay(textLines: string[]): BetLeg[] {
  console.log('🔍 Parsing multi-leg parlay...');
  const legs: BetLeg[] = [];
  
  // Look for parlay odds first (e.g., "2 Leg SGP +1750")
  const parlayOddsMatch = textLines.join(' ').match(/(\d+)\s*LEG\s*SGP\s*([+-]\d+)/i);
  const parlayOdds = parlayOddsMatch && parlayOddsMatch[2] ? parseInt(parlayOddsMatch[2]) : null;
  console.log('🎯 Parlay odds found:', parlayOdds);
  
  for (let i = 0; i < textLines.length; i++) {
    const line = textLines[i]?.trim() || '';
    // Player prop: e.g. "Rafael Devers 1+"
    const playerPropMatch = line.match(/^([A-Za-z .'-]+)\s+\d+\+$/);
    if (playerPropMatch && playerPropMatch[1]) {
      // Look ahead for the next game context line
      let teamB = 'TBD';
      for (let j = i + 1; j < textLines.length; j++) {
        const ctx = textLines[j]?.trim() || '';
        if (/at|vs/i.test(ctx)) {
          teamB = ctx;
          break;
        }
      }
      const leg: BetLeg = {
        gameId: `${playerPropMatch[1]}_${teamB}_${Date.now()}_${i}`,
        teamA: playerPropMatch[1],
        teamB,
        odds: parlayOdds || 0
      };
      legs.push(leg);
    }
  }
  console.log(`🎯 Total legs parsed: ${legs.length}`);
  return legs;
}

/**
 * Parse single bet from text
 */
function parseSingleBet(text: string): BetLeg | null {
  console.log('🔍 Parsing single bet...');
  // Split lines and look for ML pattern
  const lines = text.split(/\n|\r/).map(l => l.trim()).filter(Boolean);
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line) continue;
    
    const mlMatch = line.match(/^ML\s*([+-]?\d+)$/i);
    if (mlMatch && i > 0 && lines[i-1] && mlMatch[1]) {
      const teamA = lines[i-1] ?? 'TBD';
      return {
        gameId: `${teamA}_TBD_${Date.now()}`,
        teamA,
        teamB: 'TBD',
        odds: parseInt(mlMatch[1])
      };
    }
  }
  // Fallback to previous logic if not ML
  // Pattern 1: "Team A vs Team B +150"
  let match = text.match(/([A-Z\s]+)\s+VS\s+([A-Z\s]+)\s*([+-]\d+)/i);
  if (match && match[1] && match[2] && match[3]) {
    return {
      gameId: `${match[1].trim()}_${match[2].trim()}_${Date.now()}`,
      teamA: match[1].trim(),
      teamB: match[2].trim(),
      odds: parseInt(match[3])
    };
  }
  // Pattern 2: "Team A @ Team B +150"
  match = text.match(/([A-Z\s]+)\s+@\s+([A-Z\s]+)\s*([+-]\d+)/i);
  if (match && match[1] && match[2] && match[3]) {
    return {
      gameId: `${match[1].trim()}_${match[2].trim()}_${Date.now()}`,
      teamA: match[1].trim(),
      teamB: match[2].trim(),
      odds: parseInt(match[3])
    };
  }
  // Pattern 3: "Team A +150" (just team and odds)
  match = text.match(/([A-Z\s]+)\s*([+-]\d+)/i);
  if (match && match[1] && match[2]) {
    return {
      gameId: `${match[1].trim()}_TBD_${Date.now()}`,
      teamA: match[1].trim(),
      teamB: 'TBD',
      odds: parseInt(match[2])
    };
  }
  return null;
}

/**
 * Fallback parsing for different text formats
 */
function parseFallbackLegs(textLines: string[]): BetLeg[] {
  console.log('🔄 Starting fallback parsing...');
  const legs: BetLeg[] = [];
  
  for (const line of textLines) {
    console.log('📄 Processing line:', line);
    
    // Skip header and disclaimer lines
    if (line.includes('FANATICS') || line.includes('SPORTSBOOK') || 
        line.includes('MUST BE') || line.includes('GAMBLING PROBLEM') || 
        line.includes('BET ID') || line.includes('LEG SGP')) {
      continue;
    }
    
    // Look for team names and odds in various formats
    const teamMatch = line.match(/([A-Z\s]+)\s*(?:VS|@|\+)\s*([A-Z\s]+)/i);
    const oddsMatch = line.match(/\+(\d+)/);
    
    console.log('🏟️ Team match:', teamMatch);
    console.log('💰 Odds match:', oddsMatch);
    
    if (teamMatch && teamMatch[1] && teamMatch[2] && oddsMatch && oddsMatch[1]) {
      const teamA = teamMatch[1].trim();
      const teamB = teamMatch[2].trim();
      const odds = parseInt(oddsMatch[1]);
      const gameId = `${teamA}_${teamB}_${Date.now()}`;
      
      const leg = {
        gameId,
        teamA,
        teamB,
        odds
      };
      
      legs.push(leg);
      console.log('✅ Fallback leg created:', leg);
      continue;
    }
    
    // Try alternative patterns
    // Pattern: "TEAM A +150" or "TEAM A -150"
    const altMatch = line.match(/([A-Z\s]+)\s*([+-]\d+)/i);
    if (altMatch && altMatch[1] && altMatch[2]) {
      const teamA = altMatch[1].trim();
      const odds = parseInt(altMatch[2]);
      const teamB = 'TBD'; // We'll need to look this up later
      const gameId = `${teamA}_${teamB}_${Date.now()}`;
      
      const leg = {
        gameId,
        teamA,
        teamB,
        odds
      };
      
      legs.push(leg);
      console.log('✅ Alternative fallback leg created:', leg);
      continue;
    }
    
    // Try to parse player names (e.g., "Rafael Devers")
    const playerMatch = line.match(/^([A-Z\s]+)$/i);
    if (playerMatch && playerMatch[1] && playerMatch[1].trim().split(' ').length >= 2) {
      const playerName = playerMatch[1].trim();
      const gameId = `${playerName}_PROP_${Date.now()}`;
      
      const leg = {
        gameId,
        teamA: playerName,
        teamB: 'TBD',
        odds: 0
      };
      
      legs.push(leg);
      console.log('✅ Player leg created:', leg);
      continue;
    }
  }
  
  console.log(`🎯 Total fallback legs found: ${legs.length}`);
  return legs;
} 