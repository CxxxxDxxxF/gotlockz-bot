"""
OCR Service Tests
"""
import pytest
from unittest.mock import Mock, patch
import numpy as np

from src.bot.services.ocr import OCRService


class TestOCRService:
    """Test OCR service functionality."""
    
    @pytest.fixture
    def ocr_service(self):
        """Create OCR service instance."""
        return OCRService()
    
    @pytest.fixture
    def sample_image_bytes(self):
        """Create sample image bytes."""
        # Create a simple test image
        img_array = np.zeros((100, 100, 3), dtype=np.uint8)
        img_array.fill(255)  # White image
        return img_array.tobytes()
    
    def test_team_abbreviations(self, ocr_service):
        """Test team abbreviation resolution."""
        assert ocr_service._resolve_team_name("NYY") == "New York Yankees"
        assert ocr_service._resolve_team_name("YANKEES") == "New York Yankees"
        assert ocr_service._resolve_team_name("Unknown Team") == "Unknown Team"
    
    def test_extract_teams(self, ocr_service):
        """Test team extraction from text."""
        text = "New York Yankees @ Boston Red Sox"
        teams = ocr_service._extract_teams(text)
        assert teams == ["New York Yankees", "Boston Red Sox"]
        
        text = "LAD vs SF"
        teams = ocr_service._extract_teams(text)
        assert teams == ["Los Angeles Dodgers", "San Francisco Giants"]
    
    def test_extract_odds(self, ocr_service):
        """Test odds extraction from text."""
        text = "Over 8.5 +110"
        odds = ocr_service._extract_odds(text)
        assert odds == "+110"
        
        text = "Under 7.5 -120"
        odds = ocr_service._extract_odds(text)
        assert odds == "-120"
    
    def test_extract_description(self, ocr_service):
        """Test bet description extraction."""
        text = "Over 8.5 +110"
        description = ocr_service._extract_description(text)
        assert description == "Over 8.5"
        
        text = "Yankees -1.5 +150"
        description = ocr_service._extract_description(text)
        assert description == "Yankees -1.5 +150"
    
    @patch('src.bot.services.ocr.pytesseract.image_to_string')
    def test_extract_text(self, mock_tesseract, ocr_service):
        """Test text extraction from image."""
        mock_tesseract.return_value = "Yankees @ Red Sox Over 8.5 +110"
        
        # Create mock image
        mock_image = np.zeros((100, 100), dtype=np.uint8)
        
        text = ocr_service._extract_text(mock_image)
        assert "Yankees @ Red Sox Over 8.5 +110" in text
    
    def test_get_default_bet_data(self, ocr_service):
        """Test default bet data generation."""
        default_data = ocr_service._get_default_bet_data()
        
        assert default_data['teams'] == ['TBD', 'TBD']
        assert default_data['description'] == 'TBD'
        assert default_data['odds'] == 'TBD'
        assert default_data['units'] == '1'
        assert default_data['is_parlay'] is False
    
    @patch('src.bot.services.ocr.cv2.imdecode')
    @patch('src.bot.services.ocr.cv2.cvtColor')
    @patch('src.bot.services.ocr.cv2.fastNlMeansDenoising')
    @patch('src.bot.services.ocr.cv2.adaptiveThreshold')
    def test_preprocess_image(self, mock_threshold, mock_denoise, mock_cvt, mock_decode, ocr_service):
        """Test image preprocessing."""
        # Mock OpenCV functions
        mock_decode.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_cvt.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_denoise.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_threshold.return_value = np.zeros((100, 100), dtype=np.uint8)
        
        image_bytes = b"fake_image_data"
        result = ocr_service._preprocess_image(image_bytes)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (100, 100) 