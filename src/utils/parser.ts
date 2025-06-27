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
  const text = textLines.join('\n').toUpperCase();
  
  // Detect if this is a parlay
  const isParlay = text.includes('PARLAY') || text.includes('MULTIPLE') || text.includes('LEG');
  
  // Extract units (bet amount)
  const unitsMatch = text.match(/(\d+(?:\.\d+)?)\s*(?:UNIT|U|DOLLAR|USD|\$)/i);
  const units = unitsMatch && unitsMatch[1] ? parseFloat(unitsMatch[1]) : 1;
  
  // Extract legs
  const legs: BetLeg[] = [];
  
  if (isParlay) {
    // Parse parlay legs
    const legMatches = text.match(/(\d+\)|LEG\s*\d+)[:\s]*([^+]+)\s*\+\s*(\d+)/g);
    if (legMatches) {
      for (const match of legMatches) {
        const leg = parseLeg(match);
        if (leg) legs.push(leg);
      }
    }
  } else {
    // Parse single bet
    const singleMatch = text.match(/([^+]+)\s*\+\s*(\d+)/);
    if (singleMatch) {
      const leg = parseLeg(singleMatch[0]);
      if (leg) legs.push(leg);
    }
  }
  
  // If no legs found, try alternative parsing
  if (legs.length === 0) {
    const fallbackLeg = parseFallbackLeg(textLines);
    if (fallbackLeg) legs.push(fallbackLeg);
  }
  
  return {
    legs,
    units,
    type: legs.length > 1 ? 'PARLAY' : 'SINGLE'
  };
}

/**
 * Parse a single leg from text
 */
function parseLeg(legText: string): BetLeg | null {
  // Match pattern: "Team A + Team B +150" or "Team A vs Team B +150"
  const match = legText.match(/([^+]+?)\s*(?:\+|\svs\s)\s*([^+]+?)\s*\+\s*(\d+)/);
  if (!match || !match[1] || !match[2] || !match[3]) return null;
  
  const teamA = match[1].trim();
  const teamB = match[2].trim();
  const odds = parseInt(match[3]);
  
  // Generate a game ID based on team names (will be looked up later)
  const gameId = `${teamA}_${teamB}_${Date.now()}`;
  
  return {
    gameId,
    teamA,
    teamB,
    odds
  };
}

/**
 * Fallback parsing for different text formats
 */
function parseFallbackLeg(textLines: string[]): BetLeg | null {
  for (const line of textLines) {
    // Look for team names and odds in various formats
    const teamMatch = line.match(/([A-Z\s]+)\s*(?:VS|@|\+)\s*([A-Z\s]+)/i);
    const oddsMatch = line.match(/\+(\d+)/);
    
    if (teamMatch && teamMatch[1] && teamMatch[2] && oddsMatch && oddsMatch[1]) {
      const teamA = teamMatch[1].trim();
      const teamB = teamMatch[2].trim();
      const odds = parseInt(oddsMatch[1]);
      const gameId = `${teamA}_${teamB}_${Date.now()}`;
      
      return {
        gameId,
        teamA,
        teamB,
        odds
      };
    }
  }
  
  return null;
} 