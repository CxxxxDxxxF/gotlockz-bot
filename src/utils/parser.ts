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
  
  // Detect if this is a parlay
  const isParlay = text.includes('PARLAY') || text.includes('MULTIPLE') || text.includes('LEG');
  console.log('🎯 Is parlay:', isParlay);
  
  // Extract units (bet amount)
  const unitsMatch = text.match(/(\d+(?:\.\d+)?)\s*(?:UNIT|U|DOLLAR|USD|\$)/i);
  const units = unitsMatch && unitsMatch[1] ? parseFloat(unitsMatch[1]) : 1;
  console.log('💰 Units found:', units);
  
  // Extract legs
  const legs: BetLeg[] = [];
  
  if (isParlay) {
    // Parse parlay legs
    const legMatches = text.match(/(\d+\)|LEG\s*\d+)[:\s]*([^+]+)\s*\+\s*(\d+)/g);
    console.log('🎲 Parlay leg matches:', legMatches);
    if (legMatches) {
      for (const match of legMatches) {
        const leg = parseLeg(match);
        if (leg) legs.push(leg);
      }
    }
  } else {
    // Parse single bet
    const singleMatch = text.match(/([^+]+)\s*\+\s*(\d+)/);
    console.log('🎲 Single bet match:', singleMatch);
    if (singleMatch) {
      const leg = parseLeg(singleMatch[0]);
      if (leg) legs.push(leg);
    }
  }
  
  console.log('🎯 Legs found:', legs.length);
  
  // If no legs found, try alternative parsing
  if (legs.length === 0) {
    console.log('🔄 No legs found, trying fallback parsing...');
    const fallbackLeg = parseFallbackLeg(textLines);
    if (fallbackLeg) {
      legs.push(fallbackLeg);
      console.log('✅ Fallback leg found:', fallbackLeg);
    } else {
      console.log('❌ No fallback leg found');
    }
  }
  
  const result = {
    legs,
    units,
    type: legs.length > 1 ? 'PARLAY' : 'SINGLE'
  };
  
  console.log('📊 Final parsed result:', result);
  return result;
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
  console.log('🔄 Starting fallback parsing...');
  
  for (const line of textLines) {
    console.log('📄 Processing line:', line);
    
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
      
      console.log('✅ Fallback leg created:', leg);
      return leg;
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
      
      console.log('✅ Alternative fallback leg created:', leg);
      return leg;
    }
  }
  
  console.log('❌ No fallback leg patterns found');
  return null;
} 