# tests/test_data_enrichment.py

"""
Tests for data enrichment functionality.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from bot.utils.data_enrichment import DataEnrichment, enrich_bet_analysis


class TestDataEnrichment:
    """Test cases for data enrichment functions."""
    
    @pytest.mark.asyncio
    async def test_enrich_bet_analysis_moneyline(self):
        """Test enriching moneyline bet analysis."""
        bet_details = {
            "type": "moneyline",
            "away": "Yankees",
            "home": "Red Sox",
            "bet": "Yankees Moneyline",
            "odds": "+150"
        }
        
        with patch('bot.utils.data_enrichment.DataEnrichment') as mock_de_class:
            mock_de = AsyncMock()
            mock_de_class.return_value.__aenter__.return_value = mock_de
            
            mock_de.get_game_info.return_value = {
                "game_time": "2024-05-15 19:00",
                "venue": "Fenway Park",
                "weather": {"temperature": "72°F", "conditions": "Clear"}
            }
            
            mock_de.get_h2h_stats.return_value = {
                "team1_wins": 3,
                "team2_wins": 2
            }
            
            mock_de.calculate_edge.return_value = {
                "edge_percentage": 3.5,
                "recommendation": "Bet"
            }
            
            result = await enrich_bet_analysis(bet_details)
            
            assert result["type"] == "moneyline"
            assert "game_info" in result
            assert "h2h_stats" in result
            assert "edge_analysis" in result
    
    @pytest.mark.asyncio
    async def test_enrich_bet_analysis_player_prop(self):
        """Test enriching player prop bet analysis."""
        bet_details = {
            "type": "player_prop",
            "player": "Aaron Judge",
            "bet": "Over 1.5 Hits",
            "odds": "-120"
        }
        
        with patch('bot.utils.data_enrichment.DataEnrichment') as mock_de_class:
            mock_de = AsyncMock()
            mock_de_class.return_value.__aenter__.return_value = mock_de
            
            mock_de.get_player_stats.return_value = {
                "AVG": ".285",
                "H": "45",
                "AB": "158"
            }
            
            mock_de.calculate_edge.return_value = {
                "edge_percentage": 2.1,
                "recommendation": "Bet"
            }
            
            result = await enrich_bet_analysis(bet_details)
            
            assert result["type"] == "player_prop"
            assert "player_stats" in result
            assert "edge_analysis" in result
    
    @pytest.mark.asyncio
    async def test_data_enrichment_context_manager(self):
        """Test DataEnrichment as async context manager."""
        async with DataEnrichment() as de:
            assert de.session is not None
            assert isinstance(de.cache, dict)
            assert de.cache_ttl == 300
