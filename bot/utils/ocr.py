#!/usr/bin/env python3
"""
ocr_parser.py - Simplified OCR Image Processing

Extract text from betting slip images using OCR with maximum reliability.
"""
import logging
import io
from typing import Dict, Any, Optional
from PIL import Image
import pytesseract
import shutil

logger = logging.getLogger(__name__)


class OCRParser:
    """Parse betting slip images using OCR with simplified approach."""

    def __init__(self):
        # Check if Tesseract is available
        if not shutil.which('tesseract'):
            logger.warning("Tesseract OCR engine is not installed. OCR will not work.")
        pass

    async def extract_text_from_image(self, image_bytes: bytes) -> str:
        """Extract text from image using OCR with error handling."""
        try:
            # Check if Tesseract is available
            if not shutil.which('tesseract'):
                logger.error("Tesseract OCR engine is not installed")
                return "Tesseract not available"
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))

            # Simple preprocessing
            processed_image = self._preprocess_image_simple(image)

            # Extract text using Tesseract
            text = pytesseract.image_to_string(processed_image)

            logger.info(f"OCR extracted text: {text[:100]}...")
            return text.strip()

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return "OCR failed"

    def _preprocess_image_simple(self, image: Image.Image) -> Image.Image:
        """Simple image preprocessing for better OCR results."""
        try:
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')

            # Resize if too small
            if image.size[0] < 800 or image.size[1] < 600:
                image = image.resize(
                    (image.size[0] * 2, image.size[1] * 2), Image.Resampling.LANCZOS)

            return image

        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return image

    def parse_betting_details(self, text: str) -> Dict[str, Any]:
        """Parse betting details from OCR text."""
        try:
            # Initialize default values
            bet_data = {
                'teams': ['TBD', 'TBD'],
                'player': 'TBD',
                'description': 'TBD',
                'odds': 'TBD',
                'units': '1',
                'game_time': 'TBD',
                'sport': 'MLB'
            }

            # Extract teams (look for common patterns)
            teams = self._extract_teams(text)
            if teams:
                bet_data['teams'] = teams

            # Extract player and description
            player_info = self._extract_player_info(text)
            if player_info:
                bet_data['player'] = player_info.get('player', 'TBD')
                bet_data['description'] = player_info.get('description', 'TBD')

            # Extract odds
            odds = self._extract_odds(text)
            if odds:
                bet_data['odds'] = odds

            # Extract units
            units = self._extract_units(text)
            if units:
                bet_data['units'] = units

            # Extract game time
            game_time = self._extract_game_time(text)
            if game_time:
                bet_data['game_time'] = game_time

            logger.info(f"Parsed bet data: {bet_data}")
            return bet_data

        except Exception as e:
            logger.error(f"Error parsing betting details: {e}")
            return {
                'teams': ['TBD', 'TBD'],
                'player': 'TBD',
                'description': 'TBD',
                'odds': 'TBD',
                'units': '1',
                'game_time': 'TBD',
                'sport': 'MLB'
            }

    def _extract_teams(self, text: str) -> Optional[list]:
        """Extract team names from text."""
        import re

        # Common team patterns
        team_patterns = [
            r'(\w+)\s+(?:vs|@)\s+(\w+)',
            r'(\w+)\s+at\s+(\w+)',
            r'(\w+)\s+-\s+(\w+)'
        ]

        for pattern in team_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return [match.group(1).strip(), match.group(2).strip()]

        return None

    def _extract_player_info(self, text: str) -> Optional[Dict[str, str]]:
        """Extract player name and description from text."""
        import re

        # Look for player patterns
        player_patterns = [
            r'(\w+\s+\w+)\s*[-–]\s*(.+)',
            r'(\w+\s+\w+)\s+(.+)',
        ]

        for pattern in player_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    'player': match.group(1).strip(),
                    'description': match.group(2).strip()
                }

        return None

    def _extract_odds(self, text: str) -> Optional[str]:
        """Extract odds from text."""
        import re

        # Look for odds patterns
        odds_patterns = [
            r'[+-]\d+',
            r'odds?\s*:?\s*([+-]\d+)',
            r'([+-]\d+)\s*odds?'
        ]

        for pattern in odds_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if len(
                    match.groups()) > 0 else match.group(0)

        return None

    def _extract_units(self, text: str) -> Optional[str]:
        """Extract unit size from text."""
        import re

        # Look for unit patterns
        unit_patterns = [
            r'(\d+(?:\.\d+)?)\s*units?',
            r'units?\s*:?\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*u'
        ]

        for pattern in unit_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _extract_game_time(self, text: str) -> Optional[str]:
        """Extract game time from text."""
        import re

        # Look for time patterns
        time_patterns = [
            r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))',
            r'(\d{1,2}:\d{2})',
            r'(\d{1,2}:\d{2}\s*EST)'
        ]

        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return None


# Create a global instance
ocr_parser = OCRParser()
