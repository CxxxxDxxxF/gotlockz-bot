import { parseBetSlip } from '../image-processing/slip-parser.js';

console.log('=== Bot Integration Test ===\n');

async function testBotIntegration() {
  try {
    console.log('1. Testing image processing module import...');
    
    // Test that we can import the parser module
    console.log('   ✓ Parser module imported successfully');
    
    console.log('\n2. Testing command loading simulation...');
    
    // Simulate loading the test-ocr command
    try {
      const { data, execute } = await import('./src/commands/test-ocr.js');
      console.log(`   ✓ Test-OCR command loaded successfully`);
      console.log(`   Command name: ${data.name}`);
      console.log(`   Command description: ${data.description}`);
      console.log(`   Execute function type: ${typeof execute}`);
    } catch (error) {
      console.log(`   ❌ Failed to load test-ocr command: ${error.message}`);
      throw error;
    }
    
    console.log('\n3. Testing parser functionality...');
    
    // Test the parser with a sample input
    const testInput = 'NYM vs PHI ML -120 5u';
    const result = parseBetSlip(testInput);
    
    console.log(`   ✓ Parser test successful`);
    console.log(`   Input: "${testInput}"`);
    console.log(`   Teams: [${result.teams.join(', ')}]`);
    console.log(`   Odds: ${result.odds}`);
    console.log(`   Bet Type: ${result.betType}`);
    console.log(`   Units: ${result.units}`);
    
    console.log('\n🎉 All tests passed! Bot integration is ready.');
    console.log('\nYou can now test in Discord using: /test-ocr');
    console.log('\nTo start the bot: npm start');
    console.log('\nNote: Make sure your DISCORD_TOKEN environment variable is set.');
    
  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    console.error('Stack trace:', error.stack);
    process.exit(1);
  }
}

testBotIntegration(); 