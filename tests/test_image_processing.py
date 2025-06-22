# tests/test_image_processing.py

"""
Tests for image processing and OCR functionality.
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch
from bot.utils.image_processing import (
    preprocess_image, extract_text_from_image, parse_bet_details,
    calculate_implied_probability, calculate_edge
)


class TestImageProcessing:
    """Test cases for image processing functions."""
    
    def test_preprocess_image_with_bytes(self):
        """Test image preprocessing with bytes input."""
        # Create mock image bytes
        mock_bytes = b"fake_image_data"
        
        with patch('cv2.imdecode') as mock_imdecode:
            mock_imdecode.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
            
            with patch('cv2.cvtColor') as mock_cvt:
                mock_cvt.return_value = np.zeros((100, 100), dtype=np.uint8)
                
                with patch('cv2.minAreaRect') as mock_rect:
                    mock_rect.return_value = (None, None, 0)
                    
                    with patch('cv2.getRotationMatrix2D') as mock_matrix:
                        mock_matrix.return_value = np.eye(3)
                        
                        with patch('cv2.warpAffine') as mock_warp:
                            mock_warp.return_value = np.zeros((100, 100), dtype=np.uint8)
                            
                            with patch('cv2.fastNlMeansDenoising') as mock_denoise:
                                mock_denoise.return_value = np.zeros((100, 100), dtype=np.uint8)
                                
                                with patch('cv2.adaptiveThreshold') as mock_thresh:
                                    mock_thresh.return_value = np.zeros((100, 100), dtype=np.uint8)
                                    
                                    result = preprocess_image(mock_bytes)
                                    assert isinstance(result, np.ndarray)
    
    def test_calculate_implied_probability_positive_odds(self):
        """Test implied probability calculation with positive odds."""
        result = calculate_implied_probability("+150")
        expected = 100 / (150 + 100)
        assert abs(result - expected) < 0.001
    
    def test_calculate_implied_probability_negative_odds(self):
        """Test implied probability calculation with negative odds."""
        result = calculate_implied_probability("-190")
        expected = 190 / (190 + 100)
        assert abs(result - expected) < 0.001
    
    def test_calculate_implied_probability_invalid(self):
        """Test implied probability calculation with invalid odds."""
        result = calculate_implied_probability("invalid")
        assert result == 0.0
    
    def test_calculate_edge(self):
        """Test edge calculation."""
        result = calculate_edge(0.6, 0.5)
        expected = (0.5 - 0.6) * 100
        assert abs(result - expected) < 0.001
    
    def test_parse_moneyline(self):
        """Test moneyline bet parsing."""
        text = "Yankees at Red Sox +150"
        result = parse_bet_details(text)
        
        assert result is not None
        assert result["type"] == "moneyline"
        assert "Yankees" in result["away"]
        assert "Red Sox" in result["home"]
        assert result["odds"] == "+150"
    
    def test_parse_player_prop(self):
        """Test player prop bet parsing."""
        text = "Aaron Judge Over 1.5 Hits -120"
        result = parse_bet_details(text)
        
        assert result is not None
        assert result["type"] == "player_prop"
        assert "Aaron Judge" in result["player"]
        assert result["direction"] == "Over"
        assert result["value"] == "1.5"
        assert result["stat"] == "Hits"
        assert result["odds"] == "-120"
