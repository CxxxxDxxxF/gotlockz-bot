import axios from 'axios';
import { logger } from '../utils/logger.js';

class WeatherService {
  constructor () {
    this.cache = new Map();
    this.cacheTimeout = 10 * 60 * 1000; // 10 minutes
    this.apis = [
      {
        name: 'OpenMeteo',
        url: 'https://api.open-meteo.com/v1/forecast',
        free: true,
        rateLimit: 10000 // requests per day
      },
      {
        name: 'WeatherAPI',
        url: 'https://api.weatherapi.com/v1/current.json',
        free: true,
        rateLimit: 1000000 // requests per month
      }
    ];
  }

  async getWeatherData (location, venue = null) {
    try {
      const cacheKey = `weather_${location}`;
      const cached = this.cache.get(cacheKey);

      if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
        logger.info('Using cached weather data', { location });
        return cached.data;
      }

      logger.info('Fetching weather data', { location, venue });

      // Try multiple free APIs
      for (const api of this.apis) {
        try {
          const weatherData = await this.fetchFromAPI(api, location);

          if (weatherData) {
            // Cache the result
            this.cache.set(cacheKey, {
              data: weatherData,
              timestamp: Date.now()
            });

            return weatherData;
          }
        } catch (error) {
          logger.warn(`Weather API ${api.name} failed:`, error.message);
        }
      }

      // Fallback to basic weather data
      return this.getFallbackWeather(location);

    } catch (error) {
      logger.error('Weather service failed:', error);
      return this.getFallbackWeather(location);
    }
  }

  async fetchFromAPI (api, location) {
    switch (api.name) {
    case 'OpenMeteo':
      return await this.fetchOpenMeteo(location);
    case 'WeatherAPI':
      return await this.fetchWeatherAPI(location);
    default:
      throw new Error(`Unknown weather API: ${api.name}`);
    }
  }

  async fetchOpenMeteo (location) {
    // Get coordinates for location
    const coords = await this.getCoordinates(location);

    const response = await axios.get('https://api.open-meteo.com/v1/forecast', {
      params: {
        latitude: coords.lat,
        longitude: coords.lon,
        current: 'temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code',
        timezone: 'auto'
      },
      timeout: 5000
    });

    const current = response.data.current;

    return {
      temperature: current.temperature_2m,
      humidity: current.relative_humidity_2m,
      windSpeed: current.wind_speed_10m,
      condition: this.getWeatherCondition(current.weather_code),
      location: location,
      source: 'OpenMeteo',
      timestamp: new Date().toISOString()
    };
  }

  async fetchWeatherAPI (location) {
    const response = await axios.get('https://api.weatherapi.com/v1/current.json', {
      params: {
        key: 'free', // Use free tier
        q: location,
        aqi: 'no'
      },
      timeout: 5000
    });

    const current = response.data.current;

    return {
      temperature: current.temp_f,
      humidity: current.humidity,
      windSpeed: current.wind_mph,
      condition: current.condition.text,
      location: location,
      source: 'WeatherAPI',
      timestamp: new Date().toISOString()
    };
  }

  async getCoordinates (location) {
    // Simple geocoding - in production, use a proper geocoding service
    const response = await axios.get('https://nominatim.openstreetmap.org/search', {
      params: {
        q: location,
        format: 'json',
        limit: 1
      },
      timeout: 5000
    });

    if (response.data && response.data[0]) {
      return {
        lat: parseFloat(response.data[0].lat),
        lon: parseFloat(response.data[0].lon)
      };
    }

    // Fallback coordinates for major cities
    const fallbackCoords = {
      'New York': { lat: 40.7128, lon: -74.0060 },
      'Los Angeles': { lat: 34.0522, lon: -118.2437 },
      'Chicago': { lat: 41.8781, lon: -87.6298 },
      'Houston': { lat: 29.7604, lon: -95.3698 },
      'Phoenix': { lat: 33.4484, lon: -112.0740 }
    };

    return fallbackCoords[location] || { lat: 40.7128, lon: -74.0060 };
  }

  getWeatherCondition (code) {
    // WMO weather codes for OpenMeteo
    const conditions = {
      0: 'Clear sky',
      1: 'Mainly clear',
      2: 'Partly cloudy',
      3: 'Overcast',
      45: 'Foggy',
      48: 'Depositing rime fog',
      51: 'Light drizzle',
      53: 'Moderate drizzle',
      55: 'Dense drizzle',
      61: 'Slight rain',
      63: 'Moderate rain',
      65: 'Heavy rain',
      71: 'Slight snow',
      73: 'Moderate snow',
      75: 'Heavy snow',
      95: 'Thunderstorm'
    };

    return conditions[code] || 'Unknown';
  }

  getFallbackWeather (location) {
    // Return basic weather data when APIs fail
    return {
      temperature: 72,
      humidity: 50,
      windSpeed: 8,
      condition: 'Partly cloudy',
      location: location,
      source: 'Fallback',
      timestamp: new Date().toISOString()
    };
  }

  analyzeWeatherImpact (weatherData) {
    const { temperature, windSpeed, condition } = weatherData;

    const impact = {
      level: 'neutral',
      factors: [],
      recommendation: 'Weather conditions are normal for play'
    };

    // Temperature impact
    if (temperature > 85) {
      impact.factors.push('High temperature may favor hitters');
      impact.level = 'moderate';
    } else if (temperature < 45) {
      impact.factors.push('Cold weather may affect ball movement');
      impact.level = 'moderate';
    }

    // Wind impact
    if (windSpeed > 15) {
      impact.factors.push('Strong winds may affect ball trajectory');
      impact.level = 'high';
    }

    // Weather condition impact
    if (condition.toLowerCase().includes('rain')) {
      impact.factors.push('Rain may delay or cancel game');
      impact.level = 'high';
    } else if (condition.toLowerCase().includes('fog')) {
      impact.factors.push('Fog may affect visibility');
      impact.level = 'moderate';
    }

    // Generate recommendation
    if (impact.level === 'high') {
      impact.recommendation = 'Weather may significantly impact game - monitor conditions';
    } else if (impact.level === 'moderate') {
      impact.recommendation = 'Weather may have some impact on play';
    }

    return impact;
  }
}

const weatherService = new WeatherService();
export const { getWeatherData, analyzeWeatherImpact } = weatherService;
