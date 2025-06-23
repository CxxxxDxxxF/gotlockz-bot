"""
OCR Service - Image processing and text extraction
"""
import logging
import re
from typing import Dict, Any, Optional
import asyncio

import cv2
import numpy as np
from PIL import Image, ImageEnhance
import pytesseract

logger = logging.getLogger(__name__)


class OCRService:
    """Service for OCR processing of betting slip images."""
    
    def __init__(self):
        self.team_abbreviations = {
            "NYY": "New York Yankees", "YANKEES": "New York Yankees",
            "BOS": "Boston Red Sox", "RED SOX": "Boston Red Sox",
            "LAD": "Los Angeles Dodgers", "DODGERS": "Los Angeles Dodgers",
            "HOU": "Houston Astros", "ASTROS": "Houston Astros",
            "ATL": "Atlanta Braves", "BRAVES": "Atlanta Braves",
            "NYM": "New York Mets", "METS": "New York Mets",
            "CHC": "Chicago Cubs", "CUBS": "Chicago Cubs",
            "CWS": "Chicago White Sox", "WHITE SOX": "Chicago White Sox",
            "SF": "San Francisco Giants", "GIANTS": "San Francisco Giants",
            "SD": "San Diego Padres", "PADRES": "San Diego Padres",
            "TB": "Tampa Bay Rays", "RAYS": "Tampa Bay Rays",
            "TOR": "Toronto Blue Jays", "BLUE JAYS": "Toronto Blue Jays",
            "BAL": "Baltimore Orioles", "ORIOLES": "Baltimore Orioles",
            "CLE": "Cleveland Guardians", "GUARDIANS": "Cleveland Guardians",
            "MIN": "Minnesota Twins", "TWINS": "Minnesota Twins",
            "DET": "Detroit Tigers", "TIGERS": "Detroit Tigers",
            "KC": "Kansas City Royals", "ROYALS": "Kansas City Royals",
            "TEX": "Texas Rangers", "RANGERS": "Texas Rangers",
            "LAA": "Los Angeles Angels", "ANGELS": "Los Angeles Angels",
            "OAK": "Oakland Athletics", "A'S": "Oakland Athletics",
            "SEA": "Seattle Mariners", "MARINERS": "Seattle Mariners",
            "COL": "Colorado Rockies", "ROCKIES": "Colorado Rockies",
            "ARI": "Arizona Diamondbacks", "DIAMONDBACKS": "Arizona Diamondbacks",
            "MIA": "Miami Marlins", "MARLINS": "Miami Marlins",
            "MIL": "Milwaukee Brewers", "BREWERS": "Milwaukee Brewers",
            "CIN": "Cincinnati Reds", "REDS": "Cincinnati Reds",
            "PIT": "Pittsburgh Pirates", "PIRATES": "Pittsburgh Pirates",
            "STL": "St. Louis Cardinals", "CARDINALS": "St. Louis Cardinals",
            "PHI": "Philadelphia Phillies", "PHILLIES": "Philadelphia Phillies",
            "WSH": "Washington Nationals", "NATIONALS": "Washington Nationals",
        }
    
    async def extract_bet_data(self, image_bytes: bytes) -> Dict[str, Any]:
        """Extract betting data from image bytes."""
        try:
            # Preprocess image
            processed_image = await self._preprocess_image(image_bytes)
            
            # Extract text
            text = await self._extract_text(processed_image)
            
            # Parse betting data
            bet_data = await self._parse_bet_data(text)
            
            logger.info(f"Extracted bet data: {bet_data}")
            return bet_data
            
        except Exception as e:
            logger.error(f"Error extracting bet data: {e}")
            return self._get_default_bet_data()
    
    async def _preprocess_image(self, image_bytes: bytes) -> np.ndarray:
        """Preprocess image for better OCR results."""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                raise ValueError("Could not decode image")
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply noise reduction
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Resize for optimal OCR
            height, width = thresh.shape
            scale = min(1.0, 1200.0 / width)
            if scale < 1.0:
                new_width = int(width * scale)
                new_height = int(height * scale)
                thresh = cv2.resize(thresh, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            return thresh
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise
    
    async def _extract_text(self, image: np.ndarray) -> str:
        """Extract text from preprocessed image."""
        try:
            # Configure Tesseract
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@.-+/\s'
            
            # Extract text
            text = pytesseract.image_to_string(image, config=custom_config)
            
            # Clean text
            text = re.sub(r'\s+', ' ', text).strip()
            
            logger.info(f"Extracted text: {text[:100]}...")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            raise
    
    async def _parse_bet_data(self, text: str) -> Dict[str, Any]:
        """Parse betting data from extracted text."""
        try:
            bet_data = {
                'teams': ['TBD', 'TBD'],
                'description': 'TBD',
                'odds': 'TBD',
                'units': '1',
                'is_parlay': False
            }
            
            # Extract teams
            teams = self._extract_teams(text)
            if teams:
                bet_data['teams'] = teams
            
            # Extract odds
            odds = self._extract_odds(text)
            if odds:
                bet_data['odds'] = odds
            
            # Extract bet description
            description = self._extract_description(text)
            if description:
                bet_data['description'] = description
            
            # Check if parlay
            if 'parlay' in text.lower() or 'parlay' in description.lower():
                bet_data['is_parlay'] = True
            
            return bet_data
            
        except Exception as e:
            logger.error(f"Error parsing bet data: {e}")
            return self._get_default_bet_data()
    
    def _extract_teams(self, text: str) -> Optional[list]:
        """Extract team names from text."""
        try:
            # Look for team patterns
            team_patterns = [
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+@\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+vs\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
            ]
            
            for pattern in team_patterns:
                match = re.search(pattern, text)
                if match:
                    team1 = self._resolve_team_name(match.group(1))
                    team2 = self._resolve_team_name(match.group(2))
                    return [team1, team2]
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting teams: {e}")
            return None
    
    def _extract_odds(self, text: str) -> Optional[str]:
        """Extract odds from text."""
        try:
            # Look for odds patterns
            odds_patterns = [
                r'([+-]\d+)',
                r'(\d+\.\d+)',
                r'(\d+:\d+)'
            ]
            
            for pattern in odds_patterns:
                match = re.search(pattern, text)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting odds: {e}")
            return None
    
    def _extract_description(self, text: str) -> Optional[str]:
        """Extract bet description from text."""
        try:
            # Look for common bet types
            bet_patterns = [
                r'(Over\s+\d+\.?\d*)',
                r'(Under\s+\d+\.?\d*)',
                r'([A-Z][a-z]+\s+[A-Z][a-z]+\s+Over\s+\d+\.?\d*)',
                r'([A-Z][a-z]+\s+[A-Z][a-z]+\s+Under\s+\d+\.?\d*)',
                r'([A-Z][a-z]+\s+[A-Z][a-z]+\s+[+-]\d+\.?\d*)'
            ]
            
            for pattern in bet_patterns:
                match = re.search(pattern, text)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting description: {e}")
            return None
    
    def _resolve_team_name(self, name: str) -> str:
        """Resolve team abbreviations to full names."""
        name_upper = name.upper()
        if name_upper in self.team_abbreviations:
            return self.team_abbreviations[name_upper]
        
        # Check if name contains team name
        for abbr, full_name in self.team_abbreviations.items():
            if name_upper in full_name.upper():
                return full_name
        
        return name
    
    def _get_default_bet_data(self) -> Dict[str, Any]:
        """Get default bet data when parsing fails."""
        return {
            'teams': ['TBD', 'TBD'],
            'description': 'TBD',
            'odds': 'TBD',
            'units': '1',
            'is_parlay': False
        } 