import { execSync } from 'child_process';
import { readdirSync } from 'fs';
import { join } from 'path';

console.log('=== GOTLOCKZ IMAGE PROCESSING - COMPLETE TEST SUITE ===\n');

const testFiles = [
  'slip-parser.test.js',
  'comprehensive-test.js',
  'ocr-test.js',
  'ocr-integration-test.js'
];

let passedTests = 0;
let totalTests = testFiles.length;

async function runTest(testFile) {
  console.log(`\n--- Running ${testFile} ---`);
  try {
    const output = execSync(`node ${testFile}`, { 
      encoding: 'utf8',
      cwd: process.cwd()
    });
    console.log(output);
    console.log(`✓ ${testFile} completed successfully`);
    passedTests++;
  } catch (error) {
    console.log(`✗ ${testFile} failed:`);
    console.log(error.stdout || error.message);
    if (error.stderr) {
      console.log('Error output:', error.stderr);
    }
  }
}

async function runAllTests() {
  console.log('Starting test suite...\n');
  
  for (const testFile of testFiles) {
    await runTest(testFile);
  }
  
  console.log('\n=== TEST SUMMARY ===');
  console.log(`Tests run: ${totalTests}`);
  console.log(`Tests passed: ${passedTests}`);
  console.log(`Tests failed: ${totalTests - passedTests}`);
  console.log(`Success rate: ${Math.round((passedTests / totalTests) * 100)}%`);
  
  if (passedTests === totalTests) {
    console.log('\n🎉 ALL TESTS PASSED! 🎉');
    console.log('The image processing code is working correctly.');
  } else {
    console.log('\n⚠️  SOME TESTS FAILED');
    console.log('Please review the failed tests above.');
  }
  
  console.log('\n=== CODE QUALITY CHECK ===');
  
  // Check if all required files exist
  const requiredFiles = [
    'slip-parser.js',
    'ocr-reader.js', 
    'utils.js',
    'package.json'
  ];
  
  console.log('\nRequired files:');
  for (const file of requiredFiles) {
    try {
      const fs = await import('fs');
      fs.accessSync(file);
      console.log(`  ✓ ${file} exists`);
    } catch {
      console.log(`  ✗ ${file} missing`);
    }
  }
  
  // Check dependencies
  console.log('\nDependencies:');
  try {
    const packageJson = JSON.parse(await import('fs').then(fs => fs.readFileSync('package.json', 'utf8')));
    const deps = Object.keys(packageJson.dependencies || {});
    console.log(`  ✓ ${deps.length} dependencies defined: ${deps.join(', ')}`);
  } catch (error) {
    console.log(`  ✗ Error reading package.json: ${error.message}`);
  }
  
  console.log('\n=== TEST SUITE COMPLETED ===');
}

runAllTests().catch(console.error); 