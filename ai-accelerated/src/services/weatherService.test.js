import axios from 'axios';
import { getWeatherData, analyzeWeatherImpact } from './weatherService.js';

// Mock axios
jest.mock('axios');

describe('WeatherService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getWeatherData', () => {
    test('should return weather data from OpenMeteo API', async () => {
      // Mock geocoding response
      axios.get.mockResolvedValueOnce({
        data: [{
          lat: '40.7128',
          lon: '-74.0060'
        }]
      });

      // Mock OpenMeteo response
      axios.get.mockResolvedValueOnce({
        data: {
          current: {
            temperature_2m: 72,
            relative_humidity_2m: 65,
            wind_speed_10m: 8,
            weather_code: 2
          }
        }
      });

      const result = await getWeatherData('New York');

      expect(result).toEqual({
        temperature: 72,
        humidity: 65,
        windSpeed: 8,
        condition: 'Partly cloudy',
        location: 'New York',
        source: 'OpenMeteo',
        timestamp: expect.any(String)
      });
    });

    test('should return fallback weather when APIs fail', async () => {
      axios.get.mockRejectedValue(new Error('API Error'));

      const result = await getWeatherData('Unknown City');

      expect(result).toEqual({
        temperature: 72,
        humidity: 50,
        windSpeed: 8,
        condition: 'Partly cloudy',
        location: 'Unknown City',
        source: 'Fallback',
        timestamp: expect.any(String)
      });
    });

    test('should use cached data when available', async () => {
      // Mock successful API call first time
      axios.get.mockResolvedValueOnce({
        data: [{
          lat: '40.7128',
          lon: '-74.0060'
        }]
      });

      axios.get.mockResolvedValueOnce({
        data: {
          current: {
            temperature_2m: 72,
            relative_humidity_2m: 65,
            wind_speed_10m: 8,
            weather_code: 2
          }
        }
      });

      // First call
      await getWeatherData('New York');

      // Second call should use cache (no additional API calls)
      const result = await getWeatherData('New York');

      expect(result).toEqual({
        temperature: 72,
        humidity: 65,
        windSpeed: 8,
        condition: 'Partly cloudy',
        location: 'New York',
        source: 'OpenMeteo',
        timestamp: expect.any(String)
      });

      // Should only have made 2 API calls total (not 4)
      expect(axios.get).toHaveBeenCalledTimes(2);
    });
  });

  describe('analyzeWeatherImpact', () => {
    test('should return neutral impact for normal conditions', () => {
      const weatherData = {
        temperature: 70,
        windSpeed: 5,
        condition: 'Clear sky'
      };

      const impact = analyzeWeatherImpact(weatherData);

      expect(impact).toEqual({
        level: 'neutral',
        factors: [],
        recommendation: 'Weather conditions are normal for play'
      });
    });

    test('should detect high temperature impact', () => {
      const weatherData = {
        temperature: 90,
        windSpeed: 5,
        condition: 'Clear sky'
      };

      const impact = analyzeWeatherImpact(weatherData);

      expect(impact.level).toBe('moderate');
      expect(impact.factors).toContain('High temperature may favor hitters');
    });

    test('should detect cold weather impact', () => {
      const weatherData = {
        temperature: 35,
        windSpeed: 5,
        condition: 'Clear sky'
      };

      const impact = analyzeWeatherImpact(weatherData);

      expect(impact.level).toBe('moderate');
      expect(impact.factors).toContain('Cold weather may affect ball movement');
    });

    test('should detect high wind impact', () => {
      const weatherData = {
        temperature: 70,
        windSpeed: 20,
        condition: 'Clear sky'
      };

      const impact = analyzeWeatherImpact(weatherData);

      expect(impact.level).toBe('high');
      expect(impact.factors).toContain('Strong winds may affect ball trajectory');
    });

    test('should detect rain impact', () => {
      const weatherData = {
        temperature: 70,
        windSpeed: 5,
        condition: 'Light rain'
      };

      const impact = analyzeWeatherImpact(weatherData);

      expect(impact.level).toBe('high');
      expect(impact.factors).toContain('Rain may delay or cancel game');
    });

    test('should provide appropriate recommendations', () => {
      const weatherData = {
        temperature: 90,
        windSpeed: 20,
        condition: 'Light rain'
      };

      const impact = analyzeWeatherImpact(weatherData);

      expect(impact.recommendation).toBe('Weather may significantly impact game - monitor conditions');
    });
  });
}); 