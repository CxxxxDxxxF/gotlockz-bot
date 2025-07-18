#!/usr/bin/env node

// Simple test runner for ES modules
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Test files to run
const testFiles = [
  'src/utils/simple.test.js',
  'src/utils/rateLimiter.test.js',
  'src/utils/logger.test.js',
  'src/utils/systemStats.test.js',
  'src/services/weatherService.test.js',
  'src/commands/admin.test.js'
];

let passed = 0;
let failed = 0;
let total = 0;

console.log('🧪 Running Tests...\n');

for (const testFile of testFiles) {
  const testPath = join(__dirname, testFile);
  
  if (fs.existsSync(testPath)) {
    try {
      console.log(`📁 Running ${testFile}...`);
      
      // Import and run the test
      const testModule = await import(testPath);
      
      if (testModule.default) {
        await testModule.default();
      }
      
      console.log(`✅ ${testFile} - PASSED\n`);
      passed++;
      
    } catch (error) {
      console.log(`❌ ${testFile} - FAILED: ${error.message}\n`);
      failed++;
    }
    
    total++;
  } else {
    console.log(`⚠️  ${testFile} - NOT FOUND\n`);
  }
}

console.log('📊 Test Summary:');
console.log(`   Total: ${total}`);
console.log(`   Passed: ${passed}`);
console.log(`   Failed: ${failed}`);
console.log(`   Success Rate: ${total > 0 ? Math.round((passed / total) * 100) : 0}%`);

if (failed > 0) {
  process.exit(1);
} else {
  console.log('\n🎉 All tests passed!');
} 