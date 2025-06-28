/**
 * Weather Service - Weather data and forecasts
 */

import axios from 'axios';

export interface WeatherData {
  temperature: number;
  humidity: number;
  wind_speed: number;
  wind_direction: string;
  description: string;
  city: string;
  timestamp: Date;
  conditions: {
    is_raining: boolean;
    is_snowing: boolean;
    visibility: number;
    pressure: number;
  };
}

/**
 * Get weather forecast for a specific location
 * @param location - City name or coordinates
 * @returns Promise<WeatherData> - Weather forecast data
 */
export async function getForecast(city: string): Promise<{ temp: number; wind: number } | null> {
  const apiKey = process.env['OPENWEATHERMAP_KEY'];
  if (!apiKey) {
    console.error('Missing OPENWEATHERMAP_KEY');
    return null;
  }
  if (!city) return null;

  const url = `https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(city)}&appid=${apiKey}&units=imperial`;

  try {
    const response = await axios.get(url, { timeout: 10000 });
    const data = response.data;
    return {
      temp: data.main.temp,
      wind: data.wind.speed,
    };
  } catch (err: any) {
    console.error(`Weather API error for ${city}:`, err?.response?.data || err.message || err);
    return null;
  }
} 