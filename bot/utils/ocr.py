#!/usr/bin/env python3
"""
ocr_parser.py - OCR Image Processing

Extract text from betting slip images using OCR.
"""
import logging
import io
from typing import Dict, Any, Optional
from PIL import Image
import pytesseract
import shutil
import asyncio

logger = logging.getLogger(__name__)


class OCRParser:
    """Parse betting slip images using OCR."""

    def __init__(self):
        # Configure Tesseract path if needed
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
        pass

    async def extract_text_from_image(self, image_bytes: bytes) -> str:
        """Extract text from image using OCR with preprocessing for better accuracy."""
        if not shutil.which('tesseract'):
            error_msg = "Tesseract OCR engine is not installed or not in your system's PATH."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
            
        try:
            # Wrap OCR processing in a timeout
            return await asyncio.wait_for(
                self._perform_ocr(image_bytes), 
                timeout=5.0  # 5 second timeout for OCR
            )
        except asyncio.TimeoutError:
            logger.error("OCR processing timed out")
            return ""
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""

    async def _perform_ocr(self, image_bytes: bytes) -> str:
        """Perform the actual OCR processing."""
        image = Image.open(io.BytesIO(image_bytes))
        
        # --- Image Preprocessing for improved OCR accuracy ---
        # 1. Convert to grayscale
        image = image.convert('L')
        
        # 2. Apply a threshold to get a binary image. This helps with contrast.
        image = image.point(lambda x: 0 if x < 127 else 255, '1')

        # 3. Use Tesseract with a specific Page Segmentation Mode (PSM)
        # PSM 6: Assume a single uniform block of text, which is good for snippets.
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, config=custom_config)
        
        logger.info(f"OCR extracted text (post-processing): {text.strip()}")
        return text

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results."""
        try:
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')

            # Resize if too small
            if image.size[0] < 800 or image.size[1] < 600:
                image = image.resize(
                    (image.size[0] * 2, image.size[1] * 2), Image.Resampling.LANCZOS)

            # Enhance contrast
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)

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
                'game_date': None,
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

            # Extract game date
            game_date = self._extract_date(text)
            if game_date:
                bet_data['game_date'] = game_date

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
                'game_date': None,
                'sport': 'MLB'
            }

    def _extract_teams(self, text: str) -> Optional[list[str]]:
        """Extract teams from OCR text."""
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

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract game date from text and return in YYYY-MM-DD format."""
        import re
        # Look for MM/DD/YY or MM/DD/YYYY, common in bet slips
        match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', text)
        if match:
            month, day, year = match.groups()
            if len(year) == 2:
                year = f"20{year}"  # Assume 21st century for 2-digit years
            
            # Format to YYYY-MM-DD for the stats API
            return f"{year}-{int(month):02d}-{int(day):02d}"
        return None


# Global instance
ocr_parser = OCRParser()
