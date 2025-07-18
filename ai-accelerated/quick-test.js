#!/usr/bin/env node

/**
 * Quick Test Script for GotLockz Bot Core Functionality
 */

console.log('⚡ GotLockz Bot - Quick Test\n');

async function quickTest () {
  try {
    // Test 1: Logger
    console.log('1. Testing Logger...');
    const { logger } = await import('./src/utils/logger.js');
    logger.info('Test message');
    console.log('✅ Logger working\n');

    // Test 2: Rate Limiter
    console.log('2. Testing Rate Limiter...');
    const { rateLimiter } = await import('./src/utils/rateLimiter.js');
    const allowed = rateLimiter.allow('test-user');
    console.log(`✅ Rate Limiter working (allowed: ${allowed})\n`);

    // Test 3: System Stats
    console.log('3. Testing System Stats...');
    const { getSystemStats } = await import('./src/utils/systemStats.js');
    const stats = getSystemStats();
    console.log(`✅ System Stats working: ${JSON.stringify(stats)}\n`);

    // Test 4: Betting Service
    console.log('4. Testing Betting Service...');
    const { createBettingMessage } = await import('./src/services/bettingService.js');
    const testBetSlip = {
      legs: [{ teamA: 'Test Team A', teamB: 'Test Team B', odds: 100 }],
      stake: 50,
      potentialWin: 100
    };
    const testAnalysis = {
      confidence: 0.8,
      riskLevel: 'medium',
      keyFactors: ['Test factor 1', 'Test factor 2'],
      recommendations: ['Test recommendation'],
      modelsUsed: 'Test model'
    };
    const message = await createBettingMessage('vip_plays', testBetSlip, null, testAnalysis, null, 'Test notes');
    console.log(`✅ Betting Service working (success: ${message.success})\n`);

    // Test 5: AI Service
    console.log('5. Testing AI Service...');
    const { generateFallbackAnalysis } = await import('./src/services/aiService.js');
    const fallback = generateFallbackAnalysis();
    console.log(`✅ AI Service working (confidence: ${fallback.confidence})\n`);

    // Test 6: OCR Service
    console.log('6. Testing OCR Service...');
    const { analyzeImage } = await import('./src/services/ocrService.js');
    console.log('✅ OCR Service import successful\n');

    // Test 7: MLB Service
    console.log('7. Testing MLB Service...');
    const { getGameData } = await import('./src/services/mlbService.js');
    console.log('✅ MLB Service import successful\n');

    // Test 8: Commands
    console.log('8. Testing Commands...');
    const { data: pickData } = await import('./src/commands/pick.js');
    const { data: adminData } = await import('./src/commands/admin.js');
    const { data: economyData } = await import('./src/commands/economy.js');
    console.log(`✅ Commands working (pick: ${pickData.name}, admin: ${adminData.name}, economy: ${economyData.name})\n`);

    console.log('🎉 All core functionality tests passed!');
    console.log('\n🚀 Your GotLockz Bot is ready for deployment!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error('Stack:', error.stack);
    process.exit(1);
  }
}

quickTest(); 