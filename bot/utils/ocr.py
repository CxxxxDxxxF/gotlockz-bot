#!/usr/bin/env python3
"""
OCR (Optical Character Recognition) utilities for parsing betting slips.
Updated: 2025-06-23 - Force redeploy to ensure latest improvements are used

Extract text from betting slip images using OCR with maximum reliability.
"""
import logging
import io
from typing import Dict, Any, Optional
from PIL import Image
import pytesseract
import shutil
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class OCRParser:
    """
    OCR parser for extracting betting information from images.
    Handles team names, odds, bet types, and other betting details.
    """

    def __init__(self):
        """Initialize the OCR parser."""
        self.team_mapping = {
            # AL East
            'boston red sox': 'Boston Red Sox',
            'red sox': 'Boston Red Sox',
            'sox': 'Boston Red Sox',
            'bos': 'Boston Red Sox',
            'new york yankees': 'New York Yankees',
            'yankees': 'New York Yankees',
            'nyy': 'New York Yankees',
            'tampa bay rays': 'Tampa Bay Rays',
            'rays': 'Tampa Bay Rays',
            'tb': 'Tampa Bay Rays',
            'toronto blue jays': 'Toronto Blue Jays',
            'blue jays': 'Toronto Blue Jays',
            'tor': 'Toronto Blue Jays',
            'baltimore orioles': 'Baltimore Orioles',
            'orioles': 'Baltimore Orioles',
            'bal': 'Baltimore Orioles',
            
            # AL Central
            'chicago white sox': 'Chicago White Sox',
            'white sox': 'Chicago White Sox',
            'cws': 'Chicago White Sox',
            'cleveland guardians': 'Cleveland Guardians',
            'guardians': 'Cleveland Guardians',
            'cle': 'Cleveland Guardians',
            'detroit tigers': 'Detroit Tigers',
            'tigers': 'Detroit Tigers',
            'det': 'Detroit Tigers',
            'kansas city royals': 'Kansas City Royals',
            'royals': 'Kansas City Royals',
            'kc': 'Kansas City Royals',
            'minnesota twins': 'Minnesota Twins',
            'twins': 'Minnesota Twins',
            'min': 'Minnesota Twins',
            
            # AL West
            'houston astros': 'Houston Astros',
            'astros': 'Houston Astros',
            'hou': 'Houston Astros',
            'los angeles angels': 'Los Angeles Angels',
            'angels': 'Los Angeles Angels',
            'laa': 'Los Angeles Angels',
            'oakland athletics': 'Oakland Athletics',
            'athletics': 'Oakland Athletics',
            'oak': 'Oakland Athletics',
            'seattle mariners': 'Seattle Mariners',
            'mariners': 'Seattle Mariners',
            'sea': 'Seattle Mariners',
            'texas rangers': 'Texas Rangers',
            'rangers': 'Texas Rangers',
            'tex': 'Texas Rangers',
            
            # NL East
            'atlanta braves': 'Atlanta Braves',
            'braves': 'Atlanta Braves',
            'atl': 'Atlanta Braves',
            'miami marlins': 'Miami Marlins',
            'marlins': 'Miami Marlins',
            'mia': 'Miami Marlins',
            'new york mets': 'New York Mets',
            'mets': 'New York Mets',
            'nym': 'New York Mets',
            'philadelphia phillies': 'Philadelphia Phillies',
            'phillies': 'Philadelphia Phillies',
            'phi': 'Philadelphia Phillies',
            'washington nationals': 'Washington Nationals',
            'nationals': 'Washington Nationals',
            'was': 'Washington Nationals',
            
            # NL Central
            'chicago cubs': 'Chicago Cubs',
            'cubs': 'Chicago Cubs',
            'chc': 'Chicago Cubs',
            'cincinnati reds': 'Cincinnati Reds',
            'reds': 'Cincinnati Reds',
            'cin': 'Cincinnati Reds',
            'milwaukee brewers': 'Milwaukee Brewers',
            'brewers': 'Milwaukee Brewers',
            'mil': 'Milwaukee Brewers',
            'pittsburgh pirates': 'Pittsburgh Pirates',
            'pirates': 'Pittsburgh Pirates',
            'pit': 'Pittsburgh Pirates',
            'st. louis cardinals': 'St. Louis Cardinals',
            'cardinals': 'St. Louis Cardinals',
            'stl': 'St. Louis Cardinals',
            
            # NL West
            'arizona diamondbacks': 'Arizona Diamondbacks',
            'diamondbacks': 'Arizona Diamondbacks',
            'ari': 'Arizona Diamondbacks',
            'colorado rockies': 'Colorado Rockies',
            'rockies': 'Colorado Rockies',
            'col': 'Colorado Rockies',
            'los angeles dodgers': 'Los Angeles Dodgers',
            'dodgers': 'Los Angeles Dodgers',
            'lad': 'Los Angeles Dodgers',
            'san diego padres': 'San Diego Padres',
            'padres': 'San Diego Padres',
            'sd': 'San Diego Padres',
            'san francisco giants': 'San Francisco Giants',
            'giants': 'San Francisco Giants',
            'sf': 'San Francisco Giants',
            'san fra': 'San Francisco Giants',
            'san fran': 'San Francisco Giants',
        }
        
        self.bet_types = [
            'money line', 'moneyline', 'ml',
            'run line', 'runline', 'rl',
            'total', 'over', 'under', 'o/u',
            'player props', 'player prop',
            'team total', 'team totals',
            'first inning', 'first 5 innings',
            'game total', 'game totals'
        ]

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
        """Parse betting details from OCR text with improved logic."""
        try:
            # Initialize default values
            bet_data = {
                'teams': ['TBD', 'TBD'],
                'player': 'TBD',
                'description': 'TBD',
                'odds': 'TBD',
                'units': '1',
                'game_time': 'TBD',
                'game_date': None,  # Add game date
                'sport': 'MLB'
            }

            # Clean and normalize text
            text = text.strip()
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            logger.info(f"Processing {len(lines)} lines of OCR text")
            
            # Extract teams first (most important)
            teams = self._extract_teams_improved(text, lines)
            if teams:
                bet_data['teams'] = teams
            
            # Extract game date
            game_date = self._extract_game_date(text, lines)
            if game_date:
                bet_data['game_date'] = game_date
            
            # Extract bet information
            bet_info = self._extract_bet_info_improved(text, lines)
            if bet_info:
                bet_data.update(bet_info)
            
            # Extract odds
            odds = self._extract_odds_improved(text, lines)
            if odds:
                bet_data['odds'] = odds
            
            # Extract units
            units = self._extract_units_improved(text, lines)
            if units:
                bet_data['units'] = units
            
            # Extract game time
            game_time = self._extract_game_time_improved(text, lines)
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
                'game_date': None,
                'sport': 'MLB'
            }

    def _extract_teams_improved(self, text: str, lines: list) -> Optional[list]:
        """Extract team names with improved logic."""
        # Look for "at" pattern first (most common in betting slips)
        at_pattern = r'(\w+(?:\s+\w+)*)\s+at\s+(\w+(?:\s+\w+)*)'
        match = re.search(at_pattern, text, re.IGNORECASE)
        if match:
            away_team = match.group(1).strip()
            home_team = match.group(2).strip()
            
            # Clean up team names
            away_team = self._clean_team_name(away_team)
            home_team = self._clean_team_name(home_team)
            
            return [away_team, home_team]
        
        # Look for "vs" pattern
        vs_pattern = r'(\w+(?:\s+\w+)*)\s+vs\s+(\w+(?:\s+\w+)*)'
        match = re.search(vs_pattern, text, re.IGNORECASE)
        if match:
            team1 = match.group(1).strip()
            team2 = match.group(2).strip()
            
            team1 = self._clean_team_name(team1)
            team2 = self._clean_team_name(team2)
            
            return [team1, team2]
        
        # Look for team names in individual lines
        team_names = []
        for line in lines:
            # Skip lines that are clearly not team names
            if any(skip in line.lower() for skip in ['sportsbook', 'money', 'line', 'odds', 'units', 'time']):
                continue
                
            # Look for potential team names
            if len(line.split()) >= 2 and not line.isdigit():
                team_names.append(line.strip())
        
        if len(team_names) >= 2:
            return [self._clean_team_name(team_names[0]), self._clean_team_name(team_names[1])]
        
        return None

    def _extract_bet_info_improved(self, text: str, lines: list) -> Optional[Dict[str, str]]:
        """Extract bet type and description with improved logic."""
        # Look for common bet types
        for bet_type in self.bet_types:
            if bet_type in text.lower():
                return {
                    'description': text.strip(),
                    'player': 'TBD'  # No player for team bets
                }
        
        # Look for player props
        for line in lines:
            # Skip lines that are clearly not player names
            if any(skip in line.lower() for skip in ['sportsbook', 'money', 'line', 'odds', 'units', 'time']):
                continue
                
            # If line looks like a player name (2-3 words, no numbers)
            words = line.split()
            if 2 <= len(words) <= 3 and not any(word.isdigit() for word in words):
                # Look for the next line as description
                line_index = lines.index(line)
                if line_index + 1 < len(lines):
                    description = lines[line_index + 1]
                    return {
                        'player': line.strip(),
                        'description': description.strip()
                    }
        
        return None

    def _extract_odds_improved(self, text: str, lines: list) -> Optional[str]:
        """Extract odds with improved logic."""
        # Look for odds patterns
        odds_patterns = [
            r'([+-]\d+)',  # +150, -110
            r'odds?\s*:?\s*([+-]\d+)',
            r'([+-]\d+)\s*odds?'
        ]
        
        for pattern in odds_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                odds = match.group(1) if len(match.groups()) > 0 else match.group(0)
                return odds
        
        # Look in individual lines
        for line in lines:
            match = re.search(r'([+-]\d+)', line)
            if match:
                return match.group(1)
        
        return None

    def _extract_units_improved(self, text: str, lines: list) -> Optional[str]:
        """Extract unit size with improved logic."""
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
        
        # Look in individual lines
        for line in lines:
            if 'unit' in line.lower():
                match = re.search(r'(\d+(?:\.\d+)?)', line)
                if match:
                    return match.group(1)
        
        return None

    def _extract_game_time_improved(self, text: str, lines: list) -> Optional[str]:
        """Extract game time with improved logic."""
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
        
        # Look in individual lines
        for line in lines:
            if any(time_word in line.lower() for time_word in ['am', 'pm', 'est', 'pst']):
                match = re.search(r'(\d{1,2}:\d{2})', line)
                if match:
                    return match.group(1)
        
        return None

    def _extract_game_date(self, text: str, lines: list) -> Optional[str]:
        """Extract game date from OCR text."""
        try:
            # Look for date patterns
            date_patterns = [
                r'(\d{1,2})/(\d{1,2})/(\d{2,4})',  # MM/DD/YY or MM/DD/YYYY
                r'(\d{1,2})-(\d{1,2})-(\d{2,4})',  # MM-DD-YY or MM-DD-YYYY
                r'(\d{4})-(\d{1,2})-(\d{1,2})',    # YYYY-MM-DD
                r'(\w{3})\s+(\d{1,2}),?\s+(\d{4})', # Jan 15, 2024
                r'(\d{1,2})\s+(\w{3})\s+(\d{4})',   # 15 Jan 2024
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    match = matches[0]
                    if len(match) == 3:
                        # Handle different date formats
                        if len(match[0]) == 4:  # YYYY-MM-DD
                            year, month, day = match
                        elif len(match[2]) == 4:  # MM/DD/YYYY or MM-DD-YYYY
                            month, day, year = match
                        else:  # MM/DD/YY
                            month, day, year = match
                            year = '20' + year if len(year) == 2 else year
                        
                        # Validate and format
                        try:
                            month = int(month)
                            day = int(day)
                            year = int(year)
                            
                            if 1 <= month <= 12 and 1 <= day <= 31 and 2020 <= year <= 2030:
                                return f"{year:04d}-{month:02d}-{day:02d}"
                        except ValueError:
                            continue
            
            # Look for relative dates
            text_lower = text.lower()
            today = datetime.now()
            
            if 'yesterday' in text_lower:
                yesterday = today - timedelta(days=1)
                return yesterday.strftime("%Y-%m-%d")
            elif 'today' in text_lower:
                return today.strftime("%Y-%m-%d")
            elif 'tomorrow' in text_lower:
                tomorrow = today + timedelta(days=1)
                return tomorrow.strftime("%Y-%m-%d")
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting game date: {e}")
            return None

    def _clean_team_name(self, team_name: str) -> str:
        """Clean and normalize team names."""
        # Remove common prefixes/suffixes
        team_name = team_name.strip()
        
        # Map common abbreviations to full names
        team_lower = team_name.lower()
        for abbrev, full_name in self.team_mapping.items():
            if team_lower == abbrev or team_lower in abbrev or abbrev in team_lower:
                return full_name
        
        # Handle partial team names by checking if they start with known prefixes
        if team_lower.startswith('san fra'):
            return 'San Francisco Giants'
        elif team_lower.startswith('san die'):
            return 'San Diego Padres'
        elif team_lower.startswith('los ang'):
            return 'Los Angeles Dodgers'
        elif team_lower.startswith('new york'):
            return 'New York Yankees'
        elif team_lower.startswith('chicago'):
            return 'Chicago Cubs'
        elif team_lower.startswith('boston'):
            return 'Boston Red Sox'
        
        # If no mapping found, return the original name
        return team_name


# Create a global instance
ocr_parser = OCRParser()
