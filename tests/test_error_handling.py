"""
Test error handling for service functions with None values and missing keys
"""
import pytest
import asyncio
import logging
from typing import Dict, Any

from bot.services.mlb_scraper import MLBScraper
from bot.services.weather_impact import WeatherImpactService
from bot.services.player_analytics import PlayerAnalyticsService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestErrorHandling:
    """Test error handling for service functions."""
    
    @pytest.fixture
    def scraper(self):
        """Create MLB scraper instance."""
        return MLBScraper()
    
    @pytest.fixture
    def weather_service(self):
        """Create weather impact service instance."""
        return WeatherImpactService()
    
    @pytest.fixture
    def analytics_service(self):
        """Create player analytics service instance."""
        return PlayerAnalyticsService()
    
    def test_mlb_scraper_none_weather_data(self, scraper):
        """Test MLB scraper with None weather data."""
        # Test _get_mock_weather with None city
        result = scraper._get_mock_weather(None)
        assert isinstance(result, dict)
        assert 'temperature' in result
        assert 'humidity' in result
        assert 'pressure' in result
        assert 'wind_speed' in result
        assert 'wind_direction' in result
        assert 'condition' in result
        assert 'source' in result
    
    def test_mlb_scraper_missing_team_stats(self, scraper):
        """Test MLB scraper with missing team stats data."""
        # Test _parse_team_stats with empty data
        empty_data = {}
        result = scraper._parse_team_stats(empty_data)
        assert isinstance(result, dict)
        assert result == {}
        
        # Test with None data
        result = scraper._parse_team_stats(None)
        assert isinstance(result, dict)
        assert result == {}
        
        # Test with missing stats key
        data_without_stats = {'some_other_key': 'value'}
        result = scraper._parse_team_stats(data_without_stats)
        assert isinstance(result, dict)
        assert result == {}
    
    def test_mlb_scraper_missing_live_scores(self, scraper):
        """Test MLB scraper with missing live scores data."""
        # Test _parse_live_scores with empty data
        empty_data = {}
        result = scraper._parse_live_scores(empty_data)
        assert isinstance(result, list)
        assert result == []
        
        # Test with None data
        result = scraper._parse_live_scores(None)
        assert isinstance(result, list)
        assert result == []
        
        # Test with missing dates key
        data_without_dates = {'some_other_key': 'value'}
        result = scraper._parse_live_scores(data_without_dates)
        assert isinstance(result, list)
        assert result == []
    
    def test_weather_impact_none_data(self, weather_service):
        """Test weather impact service with None data."""
        # Test analyze_weather_impact with None weather_data
        result = weather_service.analyze_weather_impact(None)
        assert isinstance(result, dict)
        assert 'weather_conditions' in result
        assert 'impact_factors' in result
        assert 'overall_impact' in result
        assert 'recommendations' in result
        assert 'risk_level' in result
        assert 'betting_implications' in result
        
        # Test with empty dict
        result = weather_service.analyze_weather_impact({})
        assert isinstance(result, dict)
        assert 'weather_conditions' in result
        
        # Test with None ballpark
        weather_data = {'temperature': 72, 'wind_speed': 10}
        result = weather_service.analyze_weather_impact(weather_data, None)
        assert isinstance(result, dict)
        assert 'ballpark' in result['impact_factors']
    
    def test_weather_impact_missing_keys(self, weather_service):
        """Test weather impact service with missing weather keys."""
        # Test with partial weather data
        partial_data = {'temperature': 72}  # Missing other keys
        result = weather_service.analyze_weather_impact(partial_data)
        assert isinstance(result, dict)
        assert result['weather_conditions']['temperature'] == 72
        assert result['weather_conditions']['wind_speed'] is None
        assert result['weather_conditions']['humidity'] is None
        assert result['weather_conditions']['pressure'] is None
        
        # Test with None values
        data_with_nones = {
            'temperature': None,
            'wind_speed': None,
            'humidity': None,
            'pressure': None,
            'condition': None
        }
        result = weather_service.analyze_weather_impact(data_with_nones)
        assert isinstance(result, dict)
        assert all(v is None for v in result['weather_conditions'].values())
    
    def test_weather_impact_individual_analyzers(self, weather_service):
        """Test individual weather analysis methods with None values."""
        # Test temperature analysis
        result = weather_service._analyze_temperature_impact(None)
        assert isinstance(result, dict)
        assert 'factor' in result
        assert 'description' in result
        assert 'category' in result
        
        # Test wind analysis
        result = weather_service._analyze_wind_impact(None, None)
        assert isinstance(result, dict)
        assert 'factor' in result
        assert 'description' in result
        assert 'confidence' in result
        
        # Test humidity analysis
        result = weather_service._analyze_humidity_impact(None)
        assert isinstance(result, dict)
        assert 'factor' in result
        assert 'description' in result
        assert 'category' in result
        
        # Test pressure analysis
        result = weather_service._analyze_pressure_impact(None)
        assert isinstance(result, dict)
        assert 'factor' in result
        assert 'description' in result
        assert 'category' in result
        
        # Test ballpark analysis
        result = weather_service._analyze_ballpark_impact(None)
        assert isinstance(result, dict)
        assert 'factor' in result
        assert 'description' in result
        assert 'confidence' in result
    
    def test_player_analytics_none_data(self, analytics_service):
        """Test player analytics service with None data."""
        # Test get_player_stats with None player_id
        result = analytics_service.get_player_stats(None)
        assert isinstance(result, dict)
        assert 'error' in result or 'note' in result
        
        # Test get_team_matchup with None team_ids
        result = analytics_service.get_team_matchup(None, None)
        assert isinstance(result, dict)
        assert 'error' in result or 'note' in result
        
        # Test get_key_matchups with None data
        result = analytics_service.get_key_matchups(None, None)
        assert isinstance(result, dict)
        assert 'error' in result or 'note' in result
    
    def test_player_analytics_missing_keys(self, analytics_service):
        """Test player analytics service with missing data keys."""
        # Test with empty player data
        empty_player_data = {}
        result = analytics_service._parse_player_stats(empty_player_data)
        assert isinstance(result, dict)
        assert result == {}
        
        # Test with None player data
        result = analytics_service._parse_player_stats(None)
        assert isinstance(result, dict)
        assert result == {}
        
        # Test with missing stats keys
        partial_data = {'some_other_key': 'value'}
        result = analytics_service._parse_player_stats(partial_data)
        assert isinstance(result, dict)
        assert result == {}
    
    def test_mlb_scraper_cache_handling(self, scraper):
        """Test MLB scraper cache handling with None values."""
        # Test cache with None key
        result = scraper._get_cached_team_stats(None)
        assert result is None
        
        # Test cache with invalid key
        result = scraper._get_cached_team_stats("invalid_key")
        assert result is None
        
        # Test cache timeout handling
        scraper.cache['test_key'] = (0, {'data': 'test'})  # Expired cache
        result = scraper._get_cached_team_stats('test_key')
        assert result is None
    
    def test_weather_impact_calculation_with_nones(self, weather_service):
        """Test weather impact calculation with None values."""
        # Test overall impact calculation with None factors
        result = weather_service._calculate_overall_impact(
            temp_impact=None,
            wind_impact=None,
            humidity_impact=None,
            pressure_impact=None,
            ballpark_impact=None
        )
        assert isinstance(result, dict)
        assert 'factor' in result
        assert 'category' in result
        assert 'description' in result
        
        # Test with partial None values
        temp_impact = {'factor': 1.02, 'description': 'Warm'}
        result = weather_service._calculate_overall_impact(
            temp_impact=temp_impact,
            wind_impact=None,
            humidity_impact=None,
            pressure_impact=None,
            ballpark_impact=None
        )
        assert isinstance(result, dict)
        assert result['factor'] > 1.0  # Should reflect temp impact
    
    def test_weather_impact_recommendations_with_nones(self, weather_service):
        """Test weather impact recommendations with None values."""
        # Test recommendations with None impacts
        result = weather_service._generate_recommendations(
            temp_impact=None,
            wind_impact=None,
            humidity_impact=None,
            pressure_impact=None,
            ballpark_impact=None,
            conditions=None
        )
        assert isinstance(result, list)
        assert len(result) > 0  # Should have default recommendations
        
        # Test with None conditions
        temp_impact = {'factor': 1.02, 'description': 'Warm'}
        result = weather_service._generate_recommendations(
            temp_impact=temp_impact,
            wind_impact=None,
            humidity_impact=None,
            pressure_impact=None,
            ballpark_impact=None,
            conditions=None
        )
        assert isinstance(result, list)
        assert len(result) > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 