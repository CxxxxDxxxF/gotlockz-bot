// Weather Service Tests
import { getWeatherData, analyzeWeatherImpact } from './weatherService.js';

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

// Test weather service functionality
async function testWeatherService() {
  console.log('  Testing Weather Service...');

  // Test 1: Should analyze weather impact correctly
  const weatherData = {
    temperature: 70,
    windSpeed: 5,
    condition: 'Clear sky'
  };

  const impact = analyzeWeatherImpact(weatherData);
  expect(impact.level).toBe('neutral');
  expect(impact.factors).toEqual([]);
  expect(impact.recommendation).toBe('Weather conditions are normal for play');

  // Test 2: Should detect high temperature impact
  const hotWeather = {
    temperature: 90,
    windSpeed: 5,
    condition: 'Clear sky'
  };

  const hotImpact = analyzeWeatherImpact(hotWeather);
  expect(hotImpact.level).toBe('moderate');
  expect(hotImpact.factors).toContain('High temperature may favor hitters');

  // Test 3: Should detect rain impact
  const rainyWeather = {
    temperature: 70,
    windSpeed: 5,
    condition: 'Light rain'
  };

  const rainyImpact = analyzeWeatherImpact(rainyWeather);
  expect(rainyImpact.level).toBe('high');
  expect(rainyImpact.factors).toContain('Rain may delay or cancel game');

  console.log('  ✅ Weather Service tests passed');
}

// Run all tests
async function runTests() {
  try {
    await testWeatherService();
    return true;
  } catch (error) {
    console.error('  ❌ Test failed:', error.message);
    return false;
  }
}

// Export for our test runner
export default runTests; 