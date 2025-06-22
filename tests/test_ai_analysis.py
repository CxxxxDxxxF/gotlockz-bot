# tests/test_ai_analysis.py

"""
Tests for AI analysis functionality.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from bot.utils.ai_analysis import (
    analyze_bet_slip, generate_pick_summary, validate_analysis_quality,
    BettingAnalysisError
)


class TestAIAnalysis:
    """Test cases for AI analysis functions."""
    
    @pytest.mark.asyncio
    async def test_analyze_bet_slip_success(self):
        """Test successful bet slip analysis."""
        bet_details = {
            "type": "moneyline",
            "away": "Yankees",
            "home": "Red Sox",
            "bet": "Yankees Moneyline",
            "odds": "+150",
            "game": "Yankees @ Red Sox"
        }
        
        with patch('bot.utils.ai_analysis.enrich_bet_analysis') as mock_enrich:
            mock_enrich.return_value = bet_details
            
            with patch('bot.utils.ai_analysis._generate_ai_analysis') as mock_generate:
                mock_generate.return_value = {
                    "recommendation": {
                        "action": "Bet",
                        "reasoning": "Strong edge",
                        "stake_suggestion": "3%"
                    },
                    "confidence_rating": {
                        "score": 8,
                        "reasoning": "High confidence"
                    },
                    "edge_analysis": {
                        "edge_percentage": 5.2
                    }
                }
                
                result = await analyze_bet_slip(bet_details)
                
                assert result is not None
                assert "metadata" in result
                assert result["metadata"]["bet_type"] == "moneyline"
    
    @pytest.mark.asyncio
    async def test_analyze_bet_slip_error(self):
        """Test bet slip analysis with error."""
        bet_details = {"type": "invalid"}
        
        with patch('bot.utils.ai_analysis.enrich_bet_analysis', side_effect=Exception("Test error")):
            with pytest.raises(BettingAnalysisError):
                await analyze_bet_slip(bet_details)
    
    def test_validate_analysis_quality_valid(self):
        """Test validation of valid analysis."""
        analysis = {
            "risk_assessment": {"level": "Medium"},
            "edge_analysis": {"edge_percentage": 3.5},
            "confidence_rating": {"score": 7},
            "recommendation": {"action": "Bet"},
            "key_factors": ["Factor 1", "Factor 2"]
        }
        
        result = validate_analysis_quality(analysis)
        
        assert result["is_valid"] is True
        assert result["quality_score"] == 100
        assert len(result["missing_fields"]) == 0
    
    def test_validate_analysis_quality_invalid(self):
        """Test validation of invalid analysis."""
        analysis = {
            "risk_assessment": {"level": "Medium"}
            # Missing other required fields
        }
        
        result = validate_analysis_quality(analysis)
        
        assert result["is_valid"] is False
        assert result["quality_score"] == 20
        assert len(result["missing_fields"]) > 0
    
    @pytest.mark.asyncio
    async def test_generate_pick_summary(self):
        """Test pick summary generation."""
        bet_details = {
            "type": "moneyline",
            "bet": "Yankees Moneyline",
            "odds": "+150",
            "game": "Yankees @ Red Sox"
        }
        
        analysis = {
            "recommendation": {
                "action": "Bet",
                "stake_suggestion": "3%"
            },
            "confidence_rating": {
                "score": 8
            },
            "edge_analysis": {
                "edge_percentage": 5.2
            },
            "risk_assessment": {
                "level": "Medium"
            }
        }
        
        with patch('bot.utils.ai_analysis._get_next_pick_number', return_value=1):
            result = await generate_pick_summary(bet_details, analysis, "vip")
            
            assert "GOTLOCKZ VIP PICK #1" in result
            assert "Yankees Moneyline" in result
            assert "+150" in result
            assert "Bet" in result
