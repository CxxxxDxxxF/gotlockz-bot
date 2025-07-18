// Rate Limiter Tests
import { rateLimiter } from './rateLimiter.js';

// Simple expect function
function expect(actual) {
  return {
    toBe(expected) {
      if (actual !== expected) {
        throw new Error(`Expected ${actual} to be ${expected}`);
      }
    },
    toBeGreaterThan(expected) {
      if (actual <= expected) {
        throw new Error(`Expected ${actual} to be greater than ${expected}`);
      }
    },
    toBeLessThanOrEqual(expected) {
      if (actual > expected) {
        throw new Error(`Expected ${actual} to be less than or equal to ${expected}`);
      }
    }
  };
}

// Test rate limiter functionality
function testRateLimiter() {
  console.log('  Testing Rate Limiter...');

  // Clear any existing state
  rateLimiter.clearAll();

  // Test 1: Should allow first request
  const userId = '123456789';
  expect(rateLimiter.allow(userId)).toBe(true);

  // Test 2: Should block subsequent requests within cooldown period
  expect(rateLimiter.allow(userId)).toBe(false);

  // Test 3: Should return correct time remaining
  const timeRemaining = rateLimiter.getTimeRemaining(userId);
  expect(timeRemaining).toBeGreaterThan(0);
  expect(timeRemaining).toBeLessThanOrEqual(12000); // 12 seconds

  // Test 4: Should clear specific user
  rateLimiter.clear(userId);
  expect(rateLimiter.allow(userId)).toBe(true);

  // Test 5: Should clear all users
  const user1 = '123456789';
  const user2 = '987654321';
  
  rateLimiter.allow(user1);
  rateLimiter.allow(user2);
  
  rateLimiter.clearAll();
  
  expect(rateLimiter.allow(user1)).toBe(true);
  expect(rateLimiter.allow(user2)).toBe(true);

  console.log('  ✅ Rate Limiter tests passed');
}

// Run all tests
function runTests() {
  try {
    testRateLimiter();
    return true;
  } catch (error) {
    console.error('  ❌ Test failed:', error.message);
    return false;
  }
}

// Export for our test runner
export default runTests; 