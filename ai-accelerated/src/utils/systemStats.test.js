// System Stats Tests
import { getSystemStats } from './systemStats.js';

// Simple expect function
function expect(actual) {
  return {
    toBe(expected) {
      if (actual !== expected) {
        throw new Error(`Expected ${actual} to be ${expected}`);
      }
    },
    toEqual(expected) {
      if (JSON.stringify(actual) !== JSON.stringify(expected)) {
        throw new Error(`Expected ${JSON.stringify(actual)} to equal ${JSON.stringify(expected)}`);
      }
    },
    toContain(expected) {
      if (!actual.includes(expected)) {
        throw new Error(`Expected ${actual} to contain ${expected}`);
      }
    }
  };
}

// Test system stats functionality
function testSystemStats() {
  console.log('  Testing System Stats...');

  // Test 1: Should return formatted uptime
  const stats = getSystemStats();
  expect(typeof stats.uptime).toBe('string');
  expect(stats.uptime).toContain('h');

  // Test 2: Should return formatted memory usage
  expect(typeof stats.memory).toBe('string');
  expect(stats.memory).toContain('MB');

  // Test 3: Should return formatted CPU usage
  expect(typeof stats.cpu).toBe('string');
  expect(stats.cpu).toContain('ms');

  // Test 4: Should return command count
  expect(stats.commands).toBe('2');

  // Test 5: Should return server count
  expect(stats.servers).toBe('1');

  // Test 6: Should return all stats in correct format
  expect(stats).toEqual({
    uptime: expect.any(String),
    memory: expect.any(String),
    cpu: expect.any(String),
    commands: '2',
    servers: '1'
  });

  console.log('  ✅ System Stats tests passed');
}

// Run all tests
function runTests() {
  try {
    testSystemStats();
    return true;
  } catch (error) {
    console.error('  ❌ Test failed:', error.message);
    return false;
  }
}

// Export for our test runner
export default runTests; 