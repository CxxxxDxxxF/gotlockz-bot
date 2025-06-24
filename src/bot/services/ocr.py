"""
OCR Service - Image processing and text extraction
"""
import re
import logging
import aiohttp
import os
from typing import Dict, Any, Optional
from PIL import Image
import io

logger = logging.getLogger(__name__)


class OCRService:
    """Service for OCR processing of betting slip images."""
    
    def __init__(self):
        """Initialize OCR service."""
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
        self.ocr_space_api_key = os.getenv('OCR_SPACE_API_KEY', 'K87115193688957')
        self.ocr_space_url = 'https://api.ocr.space/parse/image'
    
    async def extract_bet_data(self, image_bytes: bytes) -> Dict[str, Any]:
        """Extract betting data from image bytes using OCR.space."""
        try:
            # Extract text using OCR.space
            text = await self._extract_text_ocr_space(image_bytes)
            logger.info(f"OCR.space result: {text}")
            
            # Parse betting data
            bet_data = await self._parse_bet_data(text)
            logger.info(f"Parsed bet data: {bet_data}")
            
            return bet_data
            
        except Exception as e:
            logger.error(f"Error extracting bet data: {e}")
            return self._get_default_bet_data()
    
    async def _extract_text_ocr_space(self, image_bytes: bytes) -> str:
        """Extract text using OCR.space API."""
        try:
            # Prepare the image for OCR.space
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            async with aiohttp.ClientSession() as session:
                form_data = aiohttp.FormData()
                form_data.add_field('apikey', self.ocr_space_api_key)
                form_data.add_field('language', 'eng')
                form_data.add_field('isOverlayRequired', 'false')
                form_data.add_field('filetype', 'png')
                form_data.add_field('detectOrientation', 'true')
                form_data.add_field('scale', 'true')
                form_data.add_field('OCREngine', '2')
                form_data.add_field('image', img_byte_arr, filename='bet_slip.png', content_type='image/png')
                
                async with session.post(self.ocr_space_url, data=form_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get('IsErroredOnProcessing'):
                            logger.error(f"OCR.space error: {result.get('ErrorMessage')}")
                            return ""
                        
                        parsed_results = result.get('ParsedResults', [])
                        if parsed_results:
                            extracted_text = parsed_results[0].get('ParsedText', '')
                            logger.info(f"OCR.space extracted text: {extracted_text}")
                            return extracted_text
                        else:
                            logger.warning("OCR.space returned no parsed results")
                            return ""
                    else:
                        logger.error(f"OCR.space API error: {response.status}")
                        return ""
                        
        except Exception as e:
            logger.error(f"Error with OCR.space API: {e}")
            return ""
    
    async def _parse_bet_data(self, text: str) -> Dict[str, Any]:
        """Parse betting data from extracted text."""
        try:
            bet_data = {
                'teams': ['TBD', 'TBD'],
                'description': 'TBD',
                'odds': 'TBD',
                'units': '1',
                'is_parlay': False,
                'player': None,
                'legs': []
            }
            logger.info(f"Parsing OCR text: {text}")

            # 1. Extract odds (e.g., -170, +347, -165, -80, +150)
            odds_patterns = [
                r'(?i)odds[:\s]*([+-]?\d{2,4})',  # Odds: -110 or odds -110
                r'(?i)line[:\s]*([+-]?\d{2,4})',  # Line: -110 or line -110
                r'(?i)price[:\s]*([+-]?\d{2,4})', # Price: -110 or price -110
                r'\b([+-]\d{3,4})\b',            # -110, +2000 (word boundary, 3-4 digits)
                r'\b([+-]\d{2,3})\b',            # -110, +200 (word boundary, 2-3 digits)
            ]
            odds = None
            lines = text.splitlines()
            
            # Priority 1: Look for lines with odds-related keywords
            for line in lines:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in ['odds', 'line', 'price', 'bet']):
                    for pattern in odds_patterns:
                        match = re.search(pattern, line)
                        if match:
                            potential_odds = match.group(1).strip()
                            # Validate it's actually odds (not a score or other number)
                            if self._is_valid_odds(potential_odds):
                                odds = potential_odds
                                break
                    if odds:
                        break
            
            # Priority 2: Look at bottom lines (where odds usually appear)
            if not odds:
                for line in reversed(lines):
                    for pattern in odds_patterns:
                        match = re.search(pattern, line)
                        if match:
                            potential_odds = match.group(1).strip()
                            if self._is_valid_odds(potential_odds):
                                odds = potential_odds
                                break
                    if odds:
                        break
            
            # Priority 3: Search whole text for any valid odds
            if not odds:
                for pattern in odds_patterns:
                    match = re.search(pattern, text)
                    if match:
                        potential_odds = match.group(1).strip()
                        if self._is_valid_odds(potential_odds):
                            odds = potential_odds
                            break
            
            if odds:
                bet_data['odds'] = odds
                logger.info(f"Extracted odds: {bet_data['odds']}")
            else:
                logger.info("No valid odds found.")

            # 2. Extract all team matchups (e.g., Arizona Diamondbacks at Colorado Rockies)
            matchup_pattern = r'([A-Za-z ]+) at ([A-Za-z ]+)'  # e.g., Arizona Diamondbacks at Colorado Rockies
            matchups = re.findall(matchup_pattern, text)
            if matchups:
                # Use the first matchup for main bet, others for SGP legs
                main_matchup = matchups[0]
                bet_data['teams'] = [self._resolve_team_name(main_matchup[0].strip()), self._resolve_team_name(main_matchup[1].strip())]
                logger.info(f"Extracted teams: {bet_data['teams']}")
                # For SGPs, collect all matchups
                if len(matchups) > 1:
                    bet_data['is_parlay'] = True
                    for m in matchups:
                        bet_data['legs'].append({'teams': [self._resolve_team_name(m[0].strip()), self._resolve_team_name(m[1].strip())]})

            # 3. Extract player props (e.g., Ketel Marte 3+, Shohei Ohtani 2+)
            player_prop_pattern = r'([A-Z][a-z]+(?: [A-Z][a-z]+)* \d+\+)'  # e.g., Ketel Marte 3+
            player_props = re.findall(player_prop_pattern, text)
            if player_props:
                # Remove duplicates while preserving order
                unique_player_props = []
                for prop in player_props:
                    if prop not in unique_player_props:
                        unique_player_props.append(prop)
                
                bet_data['player'] = unique_player_props[0]
                bet_data['description'] = unique_player_props[0]
                logger.info(f"Extracted player prop: {bet_data['player']}")
                # For SGPs, collect all unique player props
                if len(unique_player_props) > 1:
                    bet_data['is_parlay'] = True
                    for p in unique_player_props:
                        bet_data['legs'].append({'player': p})

            # 4. Extract bet types (e.g., Money Line, ALT Hits + Runs + RBIs, Over 1.5)
            # Try to find a line with 'Over', 'Under', 'Money Line', or 'ALT'
            bet_type = None
            for line in text.splitlines():
                if not isinstance(line, str):
                    continue
                line_lower = line.lower()
                if any(kw in line_lower for kw in ['over', 'under', 'money line', 'alt', 'stack']):
                    bet_type = line.strip()
                    break
            if bet_type:
                bet_data['description'] = bet_type
                logger.info(f"Extracted bet type: {bet_type}")

            # 5. If SGP stack, extract all legs
            if 'sgp stack' in text.lower() or 'leg' in text.lower():
                bet_data['is_parlay'] = True
                # Try to extract each leg as a block
                leg_pattern = r'([A-Z][a-z]+(?: [A-Z][a-z]+)* \d+\+).*?([A-Za-z ]+ at [A-Za-z ]+)'  # Player prop + matchup
                legs = re.findall(leg_pattern, text, re.DOTALL)
                for leg in legs:
                    bet_data['legs'].append({'player': leg[0].strip(), 'teams': [self._resolve_team_name(t.strip()) for t in leg[1].split(' at ')]})
                # Also try to extract Over/Under legs
                ou_leg_pattern = r'(Over|Under) ([\d\.]+).*?([A-Za-z ]+ at [A-Za-z ]+)'  # Over/Under + value + matchup
                ou_legs = re.findall(ou_leg_pattern, text, re.DOTALL)
                for ou_leg in ou_legs:
                    bet_data['legs'].append({'description': f"{ou_leg[0]} {ou_leg[1]}", 'teams': [self._resolve_team_name(t.strip()) for t in ou_leg[2].split(' at ')]})
                logger.info(f"Extracted SGP legs: {bet_data['legs']}")

            # 6. Parlay detection
            if (isinstance(text, str) and 'parlay' in text.lower()) or (isinstance(bet_data['description'], str) and 'parlay' in bet_data['description'].lower()):
                bet_data['is_parlay'] = True

            # 7. Fallback: If no player or bet type, use first non-empty line as description
            if bet_data['description'] == 'TBD':
                lines = [l for l in text.splitlines() if isinstance(l, str) and l.strip()]
                if lines:
                    bet_data['description'] = lines[0].strip()
                    logger.info(f"Fallback description: {bet_data['description']}")

            logger.info(f"Final parsed bet data: {bet_data}")
            return bet_data
        except Exception as e:
            logger.error(f"Error parsing bet data: {e}")
            return self._get_default_bet_data()
    
    def _extract_teams(self, text: str) -> Optional[list]:
        """Extract team names from text."""
        try:
            # Look for team patterns
            team_patterns = [
                r'([A-Za-z ]+) at ([A-Za-z ]+)',  # e.g., Arizona Diamondbacks at Colorado Rockies
                r'([A-Za-z ]+) vs ([A-Za-z ]+)',
                r'([A-Za-z ]+) @ ([A-Za-z ]+)',
            ]
            
            for pattern in team_patterns:
                match = re.search(pattern, text)
                if match:
                    team1_raw = match.group(1)
                    team2_raw = match.group(2)
                    team1 = self._resolve_team_name(team1_raw.strip() if isinstance(team1_raw, str) else "TBD")
                    team2 = self._resolve_team_name(team2_raw.strip() if isinstance(team2_raw, str) else "TBD")
                    logger.info(f"Extracted teams: {team1}, {team2}")
                    return [team1, team2]
            logger.warning("No teams matched in OCR text.")
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
                    odds_val = match.group(1)
                    if isinstance(odds_val, str):
                        return odds_val
            return None
            
        except Exception as e:
            logger.error(f"Error extracting odds: {e}")
            return None
    
    def _extract_description(self, text: str) -> Optional[str]:
        """Extract bet description from text."""
        try:
            # Try to find a line with 'Over' or 'Under' or similar
            for line in text.splitlines():
                if not isinstance(line, str) or not line:
                    logger.debug(f"Skipping line in description extraction (not a string or empty): {repr(line)} type={type(line)}")
                    continue
                try:
                    line_lower = line.lower()
                except Exception as e:
                    logger.error(f"Error calling lower() on line: {repr(line)} type={type(line)}: {e}")
                    continue
                if "over" in line_lower or "under" in line_lower:
                    return line.strip()
            # Fallback: return first non-empty line
            lines = [l for l in text.splitlines() if isinstance(l, str) and l.strip()]
            if lines:
                return lines[0].strip()
            return None
        except Exception as e:
            logger.error(f"Error extracting description: {e}")
            return None
    
    def _resolve_team_name(self, name: str) -> str:
        """Resolve team name from abbreviation or full name."""
        try:
            if not name or not isinstance(name, str):
                return "TBD"
            name_upper = name.upper().strip()
            return self.team_abbreviations.get(name_upper, name.title().strip())
        except Exception as e:
            logger.error(f"Error resolving team name: {e}")
            return "TBD"
    
    def _get_default_bet_data(self) -> Dict[str, Any]:
        """Get default bet data when parsing fails."""
        return {
            'teams': ['TBD', 'TBD'],
            'description': 'TBD',
            'odds': 'TBD',
            'units': '1',
            'is_parlay': False
        }

    def _is_valid_odds(self, odds: str) -> bool:
        """Validate if a given string is a valid odds format."""
        try:
            if not odds or not isinstance(odds, str):
                return False
            # Check if the string is a valid odds format
            if len(odds) >= 3 and (odds.startswith('+') or odds.startswith('-')) and odds[1:].isdigit():
                return True
            return False
        except Exception as e:
            logger.error(f"Error validating odds: {e}")
            return False 