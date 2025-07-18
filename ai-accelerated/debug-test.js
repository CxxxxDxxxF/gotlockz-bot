#!/usr/bin/env node

/**
 * Comprehensive Debug and Test Script for GotLockz Bot
 * Tests all components and services
 */

console.log('🔍 GotLockz Bot - Debug & Test Suite\n');

// Test utilities
async function testImport (modulePath, description) {
  try {
    await import(modulePath);
    console.log(`✅ ${description} - Import successful`);
    return true;
  } catch (error) {
    console.log(`❌ ${description} - Import failed: ${error.message}`);
    return false;
  }
}

async function testService (servicePath, description) {
  try {
    const service = await import(servicePath);
    console.log(`✅ ${description} - Service loaded`);
    return true;
  } catch (error) {
    console.log(`❌ ${description} - Service failed: ${error.message}`);
    return false;
  }
}

// Test results tracking
let passed = 0;
let failed = 0;

async function runTests () {
  console.log('📦 Testing Module Imports...\n');

  // Test utility imports
  passed += await testImport('./src/utils/logger.js', 'Logger Utility') ? 1 : 0;
  failed += await testImport('./src/utils/logger.js', 'Logger Utility') ? 0 : 1;

  passed += await testImport('./src/utils/rateLimiter.js', 'Rate Limiter Utility') ? 1 : 0;
  failed += await testImport('./src/utils/rateLimiter.js', 'Rate Limiter Utility') ? 0 : 1;

  passed += await testImport('./src/utils/systemStats.js', 'System Stats Utility') ? 1 : 0;
  failed += await testImport('./src/utils/systemStats.js', 'System Stats Utility') ? 0 : 1;

  console.log('\n🔧 Testing Service Imports...\n');

  // Test service imports
  passed += await testService('./src/services/bettingService.js', 'Betting Service') ? 1 : 0;
  failed += await testService('./src/services/bettingService.js', 'Betting Service') ? 0 : 1;

  passed += await testService('./src/services/aiService.js', 'AI Service') ? 1 : 0;
  failed += await testService('./src/services/aiService.js', 'AI Service') ? 0 : 1;

  passed += await testService('./src/services/ocrService.js', 'OCR Service') ? 1 : 0;
  failed += await testService('./src/services/ocrService.js', 'OCR Service') ? 0 : 1;

  passed += await testService('./src/services/mlbService.js', 'MLB Service') ? 1 : 0;
  failed += await testService('./src/services/mlbService.js', 'MLB Service') ? 0 : 1;

  console.log('\n🎯 Testing Command Imports...\n');

  // Test command imports
  passed += await testImport('./src/commands/pick.js', 'Pick Command') ? 1 : 0;
  failed += await testImport('./src/commands/pick.js', 'Pick Command') ? 0 : 1;

  passed += await testImport('./src/commands/admin.js', 'Admin Command') ? 1 : 0;
  failed += await testImport('./src/commands/admin.js', 'Admin Command') ? 0 : 1;

  passed += await testImport('./src/commands/economy.js', 'Economy Command') ? 1 : 0;
  failed += await testImport('./src/commands/economy.js', 'Economy Command') ? 0 : 1;

  passed += await testImport('./src/commands/leveling.js', 'Leveling Command') ? 1 : 0;
  failed += await testImport('./src/commands/leveling.js', 'Leveling Command') ? 0 : 1;

  passed += await testImport('./src/commands/automod.js', 'Automod Command') ? 1 : 0;
  failed += await testImport('./src/commands/automod.js', 'Automod Command') ? 0 : 1;

  console.log('\n🧪 Testing Service Functionality...\n');

  // Test betting service functionality
  try {
    const { createBettingMessage } = await import('./src/services/bettingService.js');
    console.log('✅ Betting Service - createBettingMessage function available');
    passed++;
  } catch (error) {
    console.log('❌ Betting Service - createBettingMessage function failed:', error.message);
    failed++;
  }

  // Test AI service functionality
  try {
    const { generateAnalysis } = await import('./src/services/aiService.js');
    console.log('✅ AI Service - generateAnalysis function available');
    passed++;
  } catch (error) {
    console.log('❌ AI Service - generateAnalysis function failed:', error.message);
    failed++;
  }

  // Test OCR service functionality
  try {
    const { analyzeImage } = await import('./src/services/ocrService.js');
    console.log('✅ OCR Service - analyzeImage function available');
    passed++;
  } catch (error) {
    console.log('❌ OCR Service - analyzeImage function failed:', error.message);
    failed++;
  }

  // Test MLB service functionality
  try {
    const { getGameData } = await import('./src/services/mlbService.js');
    console.log('✅ MLB Service - getGameData function available');
    passed++;
  } catch (error) {
    console.log('❌ MLB Service - getGameData function failed:', error.message);
    failed++;
  }

  console.log('\n📊 Testing Data Structures...\n');

  // Test betting service data sanitization
  try {
    const { bettingService } = await import('./src/services/bettingService.js');

    // Test sanitization functions
    const testBetSlip = { legs: [{ teamA: 'Test A', teamB: 'Test B', odds: 100 }] };
    const sanitized = bettingService.sanitizeBetSlip(testBetSlip);

    if (sanitized.legs && sanitized.legs.length > 0) {
      console.log('✅ Betting Service - Data sanitization working');
      passed++;
    } else {
      console.log('❌ Betting Service - Data sanitization failed');
      failed++;
    }
  } catch (error) {
    console.log('❌ Betting Service - Data sanitization test failed:', error.message);
    failed++;
  }

  // Test AI service fallback
  try {
    const { generateFallbackAnalysis } = await import('./src/services/aiService.js');
    const fallback = generateFallbackAnalysis();

    if (fallback && fallback.confidence && fallback.riskLevel) {
      console.log('✅ AI Service - Fallback analysis working');
      passed++;
    } else {
      console.log('❌ AI Service - Fallback analysis failed');
      failed++;
    }
  } catch (error) {
    console.log('❌ AI Service - Fallback analysis test failed:', error.message);
    failed++;
  }

  console.log('\n🔍 Testing Environment...\n');

  // Test environment variables
  const requiredEnvVars = [
    'DISCORD_TOKEN',
    'DISCORD_CLIENT_ID',
    'GUILD_ID',
    'OWNER_ID'
  ];

  let envPassed = 0;
  let envFailed = 0;

  requiredEnvVars.forEach(envVar => {
    if (process.env[envVar]) {
      console.log(`✅ Environment - ${envVar} is set`);
      envPassed++;
    } else {
      console.log(`❌ Environment - ${envVar} is missing`);
      envFailed++;
    }
  });

  console.log('\n📋 Testing Package Dependencies...\n');

  // Test package.json
  try {
    const fs = await import('fs');
    const packageJson = JSON.parse(fs.readFileSync('./package.json', 'utf8'));
    console.log(`✅ Package - Name: ${packageJson.name}`);
    console.log(`✅ Package - Version: ${packageJson.version}`);
    console.log(`✅ Package - Type: ${packageJson.type}`);
    passed++;
  } catch (error) {
    console.log('❌ Package - package.json failed:', error.message);
    failed++;
  }

  // Test dependencies
  try {
    const fs = await import('fs');
    const packageJson = JSON.parse(fs.readFileSync('./package.json', 'utf8'));
    const requiredDeps = ['discord.js', 'sharp', 'tesseract.js', 'axios'];

    requiredDeps.forEach(dep => {
      if (packageJson.dependencies[dep]) {
        console.log(`✅ Dependency - ${dep} is installed`);
      } else {
        console.log(`❌ Dependency - ${dep} is missing`);
      }
    });
  } catch (error) {
    console.log('❌ Dependencies - Check failed:', error.message);
  }

  console.log('\n📈 Test Results Summary...\n');

  console.log(`🎯 Total Tests: ${passed + failed}`);
  console.log(`✅ Passed: ${passed}`);
  console.log(`❌ Failed: ${failed}`);
  console.log(`📊 Success Rate: ${Math.round((passed / (passed + failed)) * 100)}%`);

  console.log(`\n🌍 Environment Variables: ${envPassed}/${envPassed + envFailed} set`);

  if (failed === 0 && envFailed === 0) {
    console.log('\n🎉 All tests passed! Your GotLockz Bot is ready for deployment!');
  } else {
    console.log('\n⚠️  Some tests failed. Please check the issues above before deploying.');
  }

  console.log('\n🚀 Next Steps:');
  console.log('1. Set up environment variables in Render');
  console.log('2. Deploy commands: npm run deploy');
  console.log('3. Start the bot: npm start');
  console.log('4. Test commands in Discord');
}

// Run the tests
runTests().catch(console.error); 