// Admin Command Tests
import { execute, data } from './admin.js';

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
    }
  };
}

// Test admin command functionality
function testAdminCommand() {
  console.log('  Testing Admin Command...');

  // Test 1: Should have correct command structure
  expect(data.name).toBe('admin');
  expect(data.description).toBe('Admin commands for bot management');
  expect(data.options).toHaveLength(4);

  const subcommandNames = data.options.map(option => option.name);
  expect(subcommandNames).toContain('ping');
  expect(subcommandNames).toContain('status');
  expect(subcommandNames).toContain('stats');
  expect(subcommandNames).toContain('restart');

  // Test 2: Should have execute function
  expect(typeof execute).toBe('function');

  console.log('  ✅ Admin Command tests passed');
}

// Run all tests
function runTests() {
  try {
    testAdminCommand();
    return true;
  } catch (error) {
    console.error('  ❌ Test failed:', error.message);
    return false;
  }
}

// Export for our test runner
export default runTests; 