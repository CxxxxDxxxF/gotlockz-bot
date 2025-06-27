#!/usr/bin/env python3
"""
Test script to verify production logging setup
"""
import asyncio
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import setup_logging
from bot.services.mlb_scraper import MLBScraper
from bot.services.player_analytics import PlayerAnalyticsService
from bot.services.weather_impact import WeatherImpactService

async def test_production_logging():
    """Test all services with production logging"""
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=== Starting Production Logging Test ===")
    
    try:
        # Test MLB Scraper
        logger.info("Testing MLB Scraper...")
        scraper = MLBScraper()
        await scraper.initialize()
        
        game_data = await scraper.get_game_data("Los Angeles Angels", "Athletics")
        logger.info(f"MLB Scraper test completed: {len(game_data) if game_data else 0} data points")
        
        # Test Player Analytics
        logger.info("Testing Player Analytics...")
        player_service = PlayerAnalyticsService()
        
        player_stats = await player_service.get_player_stats("Mike Trout")
        logger.info(f"Player Analytics test completed: {'SUCCESS' if player_stats else 'FAILED'}")
        
        # Test Weather Impact
        logger.info("Testing Weather Impact...")
        weather_service = WeatherImpactService()
        
        weather_data = {
            'temperature': 78,
            'wind_speed': 12,
            'humidity': 65,
            'pressure': 1013,
            'conditions': 'Partly Cloudy'
        }
        
        impact = weather_service.analyze_weather_impact(weather_data, "Coors Field")
        logger.info(f"Weather Impact test completed: {'SUCCESS' if impact else 'FAILED'}")
        
        # Cleanup
        await scraper.close()
        await player_service.close()
        
        logger.info("=== All Production Logging Tests Completed Successfully ===")
        
    except Exception as e:
        logger.error(f"Production logging test failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(test_production_logging()) 