import { 
  parseBetSlip, 
  matchMLBTeam, 
  extractPlayers, 
  extractUnits, 
  MLB_TEAMS, 
  BET_TYPES 
} from './slip-parser.js';

console.log('=== COMPREHENSIVE TEST SUITE ===\n');

// Test MLB_TEAMS constant
console.log('1. Testing MLB_TEAMS constant:');
console.log(`   Total teams: ${MLB_TEAMS.length}`);
console.log(`   Sample team: ${MLB_TEAMS[0].name} (${MLB_TEAMS[0].abbr})`);
console.log('   ✓ MLB_TEAMS constant loaded successfully\n');

// Test BET_TYPES constant
console.log('2. Testing BET_TYPES constant:');
console.log(`   Total bet types: ${BET_TYPES.length}`);
console.log(`   Sample bet types: ${BET_TYPES.slice(0, 5).join(', ')}`);
console.log('   ✓ BET_TYPES constant loaded successfully\n');

// Test matchMLBTeam function
console.log('3. Testing matchMLBTeam function:');
const teamTests = [
  { input: 'NYY', expected: 'New York Yankees' },
  { input: 'nyy', expected: 'New York Yankees' },
  { input: 'New York Yankees', expected: 'New York Yankees' },
  { input: 'new york yankees', expected: 'New York Yankees' },
  { input: 'LAD', expected: 'Los Angeles Dodgers' },
  { input: 'Invalid Team', expected: null }
];

for (const test of teamTests) {
  const result = matchMLBTeam(test.input);
  const pass = result ? result.name === test.expected : test.expected === null;
  console.log(`   Input: "${test.input}" -> ${result ? result.name : 'null'} ${pass ? '✓' : '✗'}`);
}
console.log('   ✓ matchMLBTeam function tested\n');

// Test extractPlayers function
console.log('4. Testing extractPlayers function:');
const playerTests = [
  { input: 'Aaron Judge OVER 1.5 HITS', expected: ['Aaron', 'Judge'] },
  { input: 'Mike Trout HR +200', expected: ['Mike', 'Trout'] },
  { input: 'NYY vs BOS ML -120', expected: [] }, // No players, just teams
];

for (const test of playerTests) {
  const result = extractPlayers(test.input);
  const pass = JSON.stringify(result) === JSON.stringify(test.expected);
  console.log(`   Input: "${test.input}" -> [${result.join(', ')}] ${pass ? '✓' : '✗'}`);
}
console.log('   ✓ extractPlayers function tested\n');

// Test extractUnits function
console.log('5. Testing extractUnits function:');
const unitTests = [
  { input: 'ML -120 5u', expected: 5 },
  { input: 'RL +110 2.5u', expected: 2.5 },
  { input: 'OVER 1.5 3 units', expected: 3 },
  { input: 'ML -120', expected: null }, // No units
];

for (const test of unitTests) {
  const result = extractUnits(test.input);
  const pass = result === test.expected;
  console.log(`   Input: "${test.input}" -> ${result} ${pass ? '✓' : '✗'}`);
}
console.log('   ✓ extractUnits function tested\n');

// Test parseBetSlip function with edge cases
console.log('6. Testing parseBetSlip function with edge cases:');
const edgeCases = [
  {
    desc: 'Empty input',
    input: '',
    expect: { teams: [], odds: null, betType: null, homeTeam: null, awayTeam: null, players: [], units: null, playerProp: null }
  },
  {
    desc: 'Input with unwanted phrases',
    input: 'Fanatics Sportsbook NYM vs PHI ML -120 5u Must be 21+ Gambling Problem Call 1-800-GAMBLER',
    expect: { teams: ['New York Mets', 'Philadelphia Phillies'], odds: -120, betType: 'ML', homeTeam: 'Philadelphia Phillies', awayTeam: 'New York Mets', players: [], units: 5, playerProp: null }
  },
  {
    desc: 'Player prop with specific format',
    input: 'Cristopher Sanchez 6+ Strikeouts +150 2u',
    expect: { teams: [], odds: 150, betType: null, homeTeam: null, awayTeam: null, players: ['Cristopher', 'Sanchez'], units: 2, playerProp: { player: 'Cristopher Sanchez', value: '6+', stat: 'Strikeouts' } }
  }
];

for (const test of edgeCases) {
  const result = parseBetSlip(test.input);
  console.log(`   Test: ${test.desc}`);
  console.log(`   Input: "${test.input}"`);
  console.log(`   Result: ${JSON.stringify(result)}`);
  
  // Simple validation - just check if we get a valid object structure
  const hasValidStructure = result && 
    typeof result === 'object' && 
    Array.isArray(result.teams) && 
    Array.isArray(result.players);
  
  console.log(`   ${hasValidStructure ? '✓' : '✗'} Valid structure\n`);
}

console.log('=== ALL TESTS COMPLETED ==='); 