// Logger Tests
import { logger } from './logger.js';

// Simple expect function
function expect(actual) {
  return {
    toBe(expected) {
      if (actual !== expected) {
        throw new Error(`Expected ${actual} to be ${expected}`);
      }
    }
  };
}

// Test logger functionality
function testLogger() {
  console.log('  Testing Logger...');

  // Test 1: Should have required methods
  expect(typeof logger.info).toBe('function');
  expect(typeof logger.error).toBe('function');
  expect(typeof logger.warn).toBe('function');
  expect(typeof logger.debug).toBe('function');

  // Test 2: Should be able to call methods without errors
  try {
    logger.info('Test info message');
    logger.warn('Test warning message');
    logger.error('Test error message');
    console.log('  ✅ Logger method calls successful');
  } catch (error) {
    throw new Error(`Logger method call failed: ${error.message}`);
  }

  console.log('  ✅ Logger tests passed');
}

// Run all tests
function runTests() {
  try {
    testLogger();
    return true;
  } catch (error) {
    console.error('  ❌ Test failed:', error.message);
    return false;
  }
}

// Export for our test runner
export default runTests; 