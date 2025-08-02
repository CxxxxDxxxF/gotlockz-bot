# GotLockz Image Processing

This directory contains the image processing and OCR utilities for the GotLockz MLB Discord bot.

## Overview

The image processing module provides:
- **OCR (Optical Character Recognition)** for extracting text from bet slip images
- **Bet slip parsing** to extract structured data from OCR text
- **Team name matching** for MLB teams
- **Utility functions** for image processing

## Files

### Core Files
- `slip-parser.js` - Main bet slip parsing logic
- `ocr-reader.js` - OCR functionality using Tesseract.js
- `utils.js` - Utility functions for image processing
- `package.json` - Dependencies and project configuration

### Test Files
- `slip-parser.test.js` - Unit tests for bet slip parsing
- `comprehensive-test.js` - Comprehensive function testing
- `ocr-test.js` - OCR function structure testing
- `ocr-integration-test.js` - Full pipeline integration testing
- `run-all-tests.js` - Complete test suite runner

## Installation

```bash
npm install
```

This installs the required dependencies:
- `tesseract.js` - OCR engine
- `sharp` - Image processing library

## Usage

### Basic Bet Slip Parsing

```javascript
import { parseBetSlip } from './slip-parser.js';

const result = parseBetSlip('NYM vs PHI ML -120 5u');
console.log(result);
// Output:
// {
//   teams: ['New York Mets', 'Philadelphia Phillies'],
//   odds: -120,
//   betType: 'ML',
//   homeTeam: 'Philadelphia Phillies',
//   awayTeam: 'New York Mets',
//   players: [],
//   units: 5,
//   playerProp: null
// }
```

### OCR Text Extraction

```javascript
import { extractTextFromImage } from './ocr-reader.js';

const imageBuffer = // ... your image buffer
const text = await extractTextFromImage(imageBuffer);
const parsed = parseBetSlip(text);
```

### Team Matching

```javascript
import { matchMLBTeam } from './slip-parser.js';

const team = matchMLBTeam('NYY');
console.log(team.name); // 'New York Yankees'
```

## Testing

### Run All Tests
```bash
node run-all-tests.js
```

### Run Individual Tests
```bash
# Basic parsing tests
node slip-parser.test.js

# Comprehensive function tests
node comprehensive-test.js

# OCR structure tests
node ocr-test.js

# Integration tests
node ocr-integration-test.js
```

## Supported Bet Types

The parser recognizes these bet types:
- ML (Money Line)
- RL (Run Line)
- O/U, OU (Over/Under)
- OVER, UNDER
- TOTAL
- SPREAD
- ALT (Alternate)
- PROP (Player Props)
- HITS, HR, RBI, RUNS, STRIKEOUTS, WALKS, STEALS
- WIN, SAVE, NO-HITTER, SHUTOUT

## Team Support

All 30 MLB teams are supported with full names and abbreviations:
- Full names: "New York Yankees", "Los Angeles Dodgers", etc.
- Abbreviations: "NYY", "LAD", "BOS", etc.
- Case-insensitive matching

## Error Handling

The code includes comprehensive error handling:
- Null/undefined input handling
- Invalid image format detection
- Graceful degradation for OCR failures
- Structured error responses

## Performance

- OCR processing is optimized with image preprocessing
- Team matching uses efficient lookup tables
- Parser uses regex patterns for fast text extraction
- Memory-efficient buffer handling

## Dependencies

- **tesseract.js**: OCR engine for text extraction
- **sharp**: Image processing and optimization

## Development

### Adding New Bet Types
Add to the `BET_TYPES` array in `slip-parser.js`:

```javascript
export const BET_TYPES = [
  // ... existing types
  'NEW_TYPE'
];
```

### Adding Test Cases
Add to the `TEST_CASES` array in `slip-parser.test.js`:

```javascript
{
  desc: 'Description of test case',
  input: 'test input text',
  expect: {
    teams: ['Team1', 'Team2'],
    odds: 150,
    betType: 'ML',
    // ... other expected fields
  }
}
```

## Troubleshooting

### OCR Issues
- Ensure images are clear and high contrast
- Check that Tesseract.js is properly installed
- Verify image format is supported (PNG, JPEG, etc.)

### Parsing Issues
- Check that team names match the supported list
- Verify bet type abbreviations are correct
- Ensure odds format is standard (+150, -120, etc.)

### Dependencies
- Run `npm install` to ensure all dependencies are installed
- Check Node.js version compatibility (requires Node.js 14+)

## License

MIT License - see main project license 