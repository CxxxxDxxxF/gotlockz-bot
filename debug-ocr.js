/**
 * Debug OCR Script - Test OCR functionality locally
 */
const fs = require('fs');
const path = require('path');

// Mock the environment for testing
process.env.DISCORD_BOT_TOKEN = 'test';
process.env.DISCORD_CLIENT_ID = 'test';
process.env.OPENAI_API_KEY = 'test';
process.env.OCR_SPACE_API_KEY = process.env.OCR_SPACE_API_KEY || '';

async function testOCR() {
  console.log('🔍 Testing OCR functionality...\n');
  
  try {
    // Test 1: Mock OCR with sample text
    console.log('📝 Test 1: Mock OCR with sample betting slip text');
    const sampleText = [
      'BET SLIP',
      'YANKEES VS RED SOX',
      'YANKEES +150',
      '1 UNIT'
    ];
    
    console.log('Sample text:', sampleText);
    
    // Import the parser
    const { parseBetSlip } = require('./dist/utils/parser');
    const result = await parseBetSlip(sampleText);
    
    console.log('✅ Parser result:', JSON.stringify(result, null, 2));
    console.log('');
    
    // Test 2: Test with different text formats
    console.log('📝 Test 2: Alternative text formats');
    const altTexts = [
      ['YANKEES @ RED SOX +150'],
      ['YANKEES +150'],
      ['PARLAY BET', '1) YANKEES VS RED SOX', 'YANKEES +150', '2) DODGERS VS GIANTS', 'DODGERS +120'],
      ['INVALID TEXT', 'NO TEAMS OR ODDS']
    ];
    
    for (let i = 0; i < altTexts.length; i++) {
      console.log(`Format ${i + 1}:`, altTexts[i]);
      const altResult = await parseBetSlip(altTexts[i]);
      console.log(`Result ${i + 1}:`, JSON.stringify(altResult, null, 2));
      console.log('');
    }
    
  } catch (error) {
    console.error('❌ Error testing OCR:', error);
  }
}

// Check if TypeScript is compiled
if (!fs.existsSync('./dist')) {
  console.log('⚠️ TypeScript not compiled. Running npx tsc...');
  const { execSync } = require('child_process');
  try {
    execSync('npx tsc', { stdio: 'inherit' });
    console.log('✅ TypeScript compiled successfully');
  } catch (error) {
    console.error('❌ TypeScript compilation failed:', error.message);
    process.exit(1);
  }
}

testOCR().catch(console.error); 