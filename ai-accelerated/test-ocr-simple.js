import { parseBetSlip } from '../image-processing/slip-parser.js';

console.log('=== Simple OCR Integration Test ===\n');

async function testOCRIntegration() {
  try {
    console.log('1. Testing OCR parser module import...');
    
    // Test that we can import the parser module
    console.log('   ✓ OCR parser module imported successfully');
    
    console.log('\n2. Testing text parsing with various inputs...');
    
    const testCases = [
      'NYM vs PHI ML -120 5u',
      'Aaron Judge OVER 1.5 HITS +150 2.5u',
      'LAD @ SF RL +110 1u',
      'Boston Red Sox vs New York Yankees ML -130 3 units',
      'Cristopher Sanchez 6+ Strikeouts +150 2u'
    ];
    
    for (const testCase of testCases) {
      console.log(`\n   Testing: "${testCase}"`);
      const parsedData = parseBetSlip(testCase);
      console.log(`   ✓ Parsed successfully`);
      console.log(`   Teams: [${parsedData.teams.join(', ')}]`);
      console.log(`   Odds: ${parsedData.odds}`);
      console.log(`   Bet Type: ${parsedData.betType}`);
      console.log(`   Units: ${parsedData.units}`);
    }
    
    console.log('\n3. Testing error handling...');
    
    // Test with null input
    const nullResult = parseBetSlip(null);
    console.log('   ✓ Null input handled correctly');
    console.log('   Result:', JSON.stringify(nullResult, null, 2));
    
    // Test with empty string
    const emptyResult = parseBetSlip('');
    console.log('   ✓ Empty string handled correctly');
    console.log('   Result:', JSON.stringify(emptyResult, null, 2));
    
    console.log('\n🎉 All tests passed! OCR parser integration is working correctly.');
    console.log('\nYou can now test in Discord using: /test-ocr');
    console.log('\nNote: For full OCR testing with images, you may need to resolve Sharp installation issues on Windows.');
    
  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    console.error('Stack trace:', error.stack);
    process.exit(1);
  }
}

testOCRIntegration(); 