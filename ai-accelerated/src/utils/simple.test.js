// Simple test to verify our test runner is working
import { rateLimiter } from './rateLimiter.js';
import { logger } from './logger.js';
import { getSystemStats } from './systemStats.js';

// Test rate limiter
function testRateLimiter() {
  console.log('  Testing Rate Limiter...');
  
  // Test basic functionality
  const userId = '123456789';
  expect(rateLimiter.allow(userId)).toBe(true);
  expect(rateLimiter.allow(userId)).toBe(false);
  
  console.log('  ✅ Rate Limiter tests passed');
}

// Test logger
function testLogger() {
  console.log('  Testing Logger...');
  
  // Test that logger methods exist
  expect(typeof logger.info).toBe('function');
  expect(typeof logger.error).toBe('function');
  expect(typeof logger.warn).toBe('function');
  
  console.log('  ✅ Logger tests passed');
}

// Test system stats
function testSystemStats() {
  console.log('  Testing System Stats...');
  
  const stats = getSystemStats();
  
  expect(typeof stats.uptime).toBe('string');
  expect(typeof stats.memory).toBe('string');
  expect(typeof stats.cpu).toBe('string');
  expect(typeof stats.commands).toBe('string');
  expect(typeof stats.servers).toBe('string');
  
  console.log('  ✅ System Stats tests passed');
}

// Simple expect function
function expect(actual) {
  return {
    toBe(expected) {
      if (actual !== expected) {
        throw new Error(`Expected ${actual} to be ${expected}`);
      }
    },
    toHaveLength(expected) {
      if (actual.length !== expected) {
        throw new Error(`Expected length ${actual.length} to be ${expected}`);
      }
    }
  };
}

// Run all tests
function runTests() {
  try {
    testRateLimiter();
    testLogger();
    testSystemStats();
    return true;
  } catch (error) {
    console.error('  ❌ Test failed:', error.message);
    return false;
  }
}

// Export for our test runner
export default runTests; 