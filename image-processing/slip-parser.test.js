import { parseBetSlip } from './slip-parser.js';

const TEST_CASES = [
  {
    desc: 'ML bet with odds and units',
    input: 'NYM vs PHI ML -120 5u',
    expect: {
      teams: ['New York Mets', 'Philadelphia Phillies'],
      odds: -120,
      betType: 'ML',
      homeTeam: 'Philadelphia Phillies',
      awayTeam: 'New York Mets',
      units: 5
    }
  },
  {
    desc: 'Player prop with player name and decimal units',
    input: 'Aaron Judge OVER 1.5 HITS +150 2.5u',
    expect: {
      teams: [],
      odds: 150,
      betType: 'OVER',
      players: ['Aaron', 'Judge'],
      units: 2.5
    }
  },
  {
    desc: 'Spread bet with @ for home/away',
    input: 'LAD @ SF RL +110 1u',
    expect: {
      teams: ['Los Angeles Dodgers', 'San Francisco Giants'],
      odds: 110,
      betType: 'RL',
      homeTeam: 'San Francisco Giants',
      awayTeam: 'Los Angeles Dodgers',
      units: 1
    }
  },
  {
    desc: 'Multi-word team names',
    input: 'Boston Red Sox vs New York Yankees ML -130 3 units',
    expect: {
      teams: ['New York Yankees', 'Boston Red Sox'],
      odds: -130,
      betType: 'ML',
      homeTeam: 'New York Yankees',
      awayTeam: 'Boston Red Sox',
      units: 3
    }
  }
];

function normalizeResult(result, expect) {
  // Ensure all expected keys are present in the result, even if undefined
  const normalized = { ...result };
  for (const k in expect) {
    if (!(k in normalized)) normalized[k] = undefined;
  }
  return normalized;
}

function shallowMatch(obj, expect) {
  for (const k in expect) {
    if (Array.isArray(expect[k])) {
      if (!Array.isArray(obj[k]) || expect[k].join(',') !== obj[k].join(',')) return false;
    } else if (expect[k] !== undefined && obj[k] !== expect[k]) {
      return false;
    }
  }
  return true;
}

function printDiff(obj, expect) {
  for (const k in expect) {
    if (Array.isArray(expect[k])) {
      if (!Array.isArray(obj[k]) || expect[k].join(',') !== obj[k].join(',')) {
        console.log(`  Key: ${k}\n    Expected: ${JSON.stringify(expect[k])}\n    Got:      ${JSON.stringify(obj[k])}`);
      }
    } else if (expect[k] !== undefined && obj[k] !== expect[k]) {
      console.log(`  Key: ${k}\n    Expected: ${JSON.stringify(expect[k])}\n    Got:      ${JSON.stringify(obj[k])}`);
    }
  }
}

for (const test of TEST_CASES) {
  const result = parseBetSlip(test.input);
  const normalized = normalizeResult(result, test.expect);
  const pass = shallowMatch(normalized, test.expect);
  console.log(`Test: ${test.desc}\nInput: ${test.input}\nResult:`, normalized, `\nPASS: ${pass}`);
  if (!pass) {
    printDiff(normalized, test.expect);
  }
  console.log('');
} 