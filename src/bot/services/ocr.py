"""
OCR Service - Image processing and text extraction
"""
import re
import logging
import aiohttp
import os
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import io
from datetime import datetime

logger = logging.getLogger(__name__)


class OCRService:
    """Service for parsing betting slips from OCR text."""
    
    def __init__(self):
        """Initialize OCR service."""
        self.team_mappings = {
            # MLB Teams
            'nyy': 'New York Yankees', 'yankees': 'New York Yankees',
            'bos': 'Boston Red Sox', 'red sox': 'Boston Red Sox',
            'tor': 'Toronto Blue Jays', 'blue jays': 'Toronto Blue Jays',
            'tb': 'Tampa Bay Rays', 'rays': 'Tampa Bay Rays',
            'bal': 'Baltimore Orioles', 'orioles': 'Baltimore Orioles',
            'cle': 'Cleveland Guardians', 'guardians': 'Cleveland Guardians',
            'min': 'Minnesota Twins', 'twins': 'Minnesota Twins',
            'det': 'Detroit Tigers', 'tigers': 'Detroit Tigers',
            'kc': 'Kansas City Royals', 'royals': 'Kansas City Royals',
            'chw': 'Chicago White Sox', 'white sox': 'Chicago White Sox',
            'hou': 'Houston Astros', 'astros': 'Houston Astros',
            'tex': 'Texas Rangers', 'rangers': 'Texas Rangers',
            'oak': 'Oakland Athletics', 'athletics': 'Oakland Athletics',
            'laa': 'Los Angeles Angels', 'angels': 'Los Angeles Angels',
            'sea': 'Seattle Mariners', 'mariners': 'Seattle Mariners',
            'atl': 'Atlanta Braves', 'braves': 'Atlanta Braves',
            'nym': 'New York Mets', 'mets': 'New York Mets',
            'phi': 'Philadelphia Phillies', 'phillies': 'Philadelphia Phillies',
            'was': 'Washington Nationals', 'nationals': 'Washington Nationals',
            'mia': 'Miami Marlins', 'marlins': 'Miami Marlins',
            'chc': 'Chicago Cubs', 'cubs': 'Chicago Cubs',
            'mil': 'Milwaukee Brewers', 'brewers': 'Milwaukee Brewers',
            'cin': 'Cincinnati Reds', 'reds': 'Cincinnati Reds',
            'pit': 'Pittsburgh Pirates', 'pirates': 'Pittsburgh Pirates',
            'stl': 'St. Louis Cardinals', 'cardinals': 'St. Louis Cardinals',
            'ari': 'Arizona Diamondbacks', 'diamondbacks': 'Arizona Diamondbacks',
            'col': 'Colorado Rockies', 'rockies': 'Colorado Rockies',
            'sf': 'San Francisco Giants', 'giants': 'San Francisco Giants',
            'sd': 'San Diego Padres', 'padres': 'San Diego Padres',
            'lad': 'Los Angeles Dodgers', 'dodgers': 'Los Angeles Dodgers'
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
            bet_data = self.parse_betting_slip(text)
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
    
    def parse_betting_slip(self, text: str) -> Dict[str, Any]:
        """Parse betting data from extracted text. Handles all Fanatics MLB slip types, with improved SGP/parlay leg extraction."""

        if not text or not isinstance(text, str):
            logger.warning("Invalid text input for parsing")
            return {}

        try:
            # Clean and normalize text
            text = text.strip().lower()
            lines = [line.strip() for line in text.splitlines() if line.strip()]

            # Extract basic slip info
            slip_info = self._extract_slip_info(lines)
            if not slip_info:
                return {}

            # Extract teams and matchups
            teams = self._extract_teams(lines)
            if not teams or len(teams) < 2:
                logger.warning("Could not extract teams from slip")
                return {}

            # Extract bet details
            bet_details = self._extract_bet_details(lines, teams)

            # Combine all extracted data
            result = {
                'teams': teams,
                'bet_type': slip_info.get('bet_type', 'Unknown'),
                'bet_amount': slip_info.get('bet_amount'),
                'potential_payout': slip_info.get('potential_payout'),
                'odds': slip_info.get('odds'),
                'description': bet_details.get('description', ''),
                'legs': bet_details.get('legs', []),
                'parlay_type': slip_info.get('parlay_type'),
                'timestamp': datetime.now().isoformat(),
                'raw_text': text[:500]  # Store first 500 chars for debugging
            }

            logger.info(f"Successfully parsed betting slip: {result['bet_type']} - {teams[0]} vs {teams[1]}")
            return result

        except Exception as e:
            logger.error(f"Error parsing betting slip: {e}")
            return {}

    def _extract_slip_info(self, lines: List[str]) -> Dict[str, Any]:
        """Extract basic slip information."""
        try:
            info = {}
            branding_keywords = [
                'fanatics sportsbook', 'fanatics', 'sportsbook', 'fcash', 
                'bet id', 'must be 21+', 'gambling problem', 'call', 
                '1-800-gambler', 'rg'
            ]

            # Determine bet type
            for line in lines:
                if any(keyword in line for keyword in branding_keywords):
                    continue

                if 'parlay' in line:
                    info['bet_type'] = 'Parlay'
                    if 'same game' in line or 'sgp' in line:
                        info['parlay_type'] = 'Same Game Parlay'
                    else:
                        info['parlay_type'] = 'Multi-Game Parlay'
                    break
                elif 'straight' in line or 'single' in line:
                    info['bet_type'] = 'Straight'
                    break
                elif 'teaser' in line:
                    info['bet_type'] = 'Teaser'
                    break

            # Extract bet amount and payout
            for line in lines:
                # Look for bet amount patterns
                bet_match = re.search(r'bet[:\s]*\$?(\d+(?:\.\d{2})?)', line)
                if bet_match:
                    info['bet_amount'] = float(bet_match.group(1))

                # Look for payout patterns
                payout_match = re.search(r'(?:payout|win|to win)[:\s]*\$?(\d+(?:\.\d{2})?)', line)
                if payout_match:
                    info['potential_payout'] = float(payout_match.group(1))

                # Look for odds
                odds_match = re.search(r'([+-]\d{3,4})', line)
                if odds_match:
                    info['odds'] = odds_match.group(1)

            return info

        except Exception as e:
            logger.error(f"Error extracting slip info: {e}")
            return {}

    def _extract_teams(self, lines: List[str]) -> List[str]:
        """Extract team names from text."""
        try:
            teams_found = []
            team_patterns = [
                r'(\w+(?:\s+\w+)*)\s+@\s+(\w+(?:\s+\w+)*)',  # Team @ Team
                r'(\w+(?:\s+\w+)*)\s+vs\s+(\w+(?:\s+\w+)*)',  # Team vs Team
                r'(\w+(?:\s+\w+)*)\s+-\s+(\w+(?:\s+\w+)*)'   # Team - Team
            ]

            for line in lines:
                for pattern in team_patterns:
                    matches = re.findall(pattern, line, re.IGNORECASE)
                    if matches:
                        for matchup_teams in matches:
                            if len(matchup_teams) == 2:
                                team1 = self._resolve_team_name(matchup_teams[0].strip())
                                team2 = self._resolve_team_name(matchup_teams[1].strip())
                                if team1 and team2:
                                    teams_found = [team1, team2]
                                    break

                if teams_found:
                    break

            # If no pattern match, try direct team name matching
            if not teams_found:
                for line in lines:
                    for team_key, team_name in self.team_mappings.items():
                        if team_key in line.lower():
                            if team_name not in teams_found:
                                teams_found.append(team_name)
                            if len(teams_found) == 2:
                                break

            return teams_found[:2]  # Return max 2 teams

        except Exception as e:
            logger.error(f"Error extracting teams: {e}")
            return []

    def _extract_bet_details(self, lines: List[str], teams: List[str]) -> Dict[str, Any]:
        """Extract detailed bet information including legs for parlays."""

        def leg_signature(leg):
            """Create a unique signature for a bet leg."""
            return f"{leg.get('team', '')}-{leg.get('type', '')}-{leg.get('value', '')}"

        try:
            details = {'description': '', 'legs': []}
            seen_legs = set()

            for line in lines:
                # Skip branding and metadata lines
                if any(keyword in line for keyword in ['fanatics', 'bet id', 'gambling']):
                    continue

                # Look for over/under patterns
                over_under_match = re.search(r'(\w+)\s+(over|under)\s+(\d+(?:\.\d)?)', line, re.IGNORECASE)
                if over_under_match:
                    team, direction, value = over_under_match.groups()
                    team_name = self._resolve_team_name(team)
                    if team_name:
                        leg = {
                            'team': team_name,
                            'type': f'{direction.lower()}_total',
                            'value': float(value),
                            'description': f"{team_name} {direction.title()} {value}"
                        }
                        leg_sig = leg_signature(leg)
                        if leg_sig not in seen_legs:
                            details['legs'].append(leg)
                            seen_legs.add(leg_sig)

                # Look for moneyline patterns
                moneyline_match = re.search(r'(\w+)\s+ml\s*([+-]\d{3,4})', line, re.IGNORECASE)
                if moneyline_match:
                    team, odds = moneyline_match.groups()
                    team_name = self._resolve_team_name(team)
                    if team_name:
                        leg = {
                            'team': team_name,
                            'type': 'moneyline',
                            'value': odds,
                            'description': f"{team_name} ML {odds}"
                        }
                        leg_sig = leg_signature(leg)
                        if leg_sig not in seen_legs:
                            details['legs'].append(leg)
                            seen_legs.add(leg_sig)

                # Look for player props
                player_match = re.search(r'(\w+\s+\w+)\s+(hits|runs|rbis|strikeouts)\s+(over|under)\s+(\d+(?:\.\d)?)', line, re.IGNORECASE)
                if player_match:
                    player, prop_type, direction, value = player_match.groups()
                    leg = {
                        'player': player.title(),
                        'type': f'{prop_type.lower()}_{direction.lower()}',
                        'value': float(value),
                        'description': f"{player.title()} {prop_type.title()} {direction.title()} {value}"
                    }
                    leg_sig = leg_signature(leg)
                    if leg_sig not in seen_legs:
                        details['legs'].append(leg)
                        seen_legs.add(leg_sig)

            # Build description from legs
            if details['legs']:
                descriptions = [leg['description'] for leg in details['legs']]
                details['description'] = ' | '.join(descriptions)
            else:
                # Fallback: try to extract any betting line
                for line in lines:
                    bet_keywords = [
                        'over', 'under', 'money line', 'no', 'yes', 'parlay', 
                        'inning', 'earned runs', 'alt', 'hits', 'runs', 'rbis', '+', '-'
                    ]

                    def is_team_line(line):
                        """Check if line contains team betting info."""
                        return any(keyword in line.lower() for keyword in bet_keywords)

                    if is_team_line(line):
                        # Clean up the line for description
                        clean_line = re.sub(r'[^\w\s@\-+.]', ' ', line)
                        clean_line = ' '.join(clean_line.split())
                        if clean_line and len(clean_line) > 5:
                            candidate = clean_line.strip()
                            if candidate and candidate != line and not candidate.isdigit() and not candidate.startswith('-') and not candidate.startswith('+'):
                                details['description'] = candidate
                                break

            return details

        except Exception as e:
            logger.error(f"Error extracting bet details: {e}")
            return {'description': '', 'legs': []}

    def _resolve_team_name(self, team_text: str) -> Optional[str]:
        """Resolve team name from various formats."""
        try:
            if not team_text:
                return None

            # Clean the team text
            team_text = team_text.strip().lower()
            team_text = re.sub(r'[^\w\s]', '', team_text)

            # Direct mapping lookup
            if team_text in self.team_mappings:
                return self.team_mappings[team_text]

            # Partial matching
            for key, value in self.team_mappings.items():
                if key in team_text or team_text in key:
                    return value

            # Handle common variations
            variations = {
                'ny': 'New York Yankees',
                'nyc': 'New York Yankees',
                'la': 'Los Angeles Dodgers',
                'sf': 'San Francisco Giants',
                'sd': 'San Diego Padres',
                'chicago': 'Chicago Cubs',
                'cubs': 'Chicago Cubs',
                'sox': 'Chicago White Sox',
                'white sox': 'Chicago White Sox'
            }

            if team_text in variations:
                return variations[team_text]

            return None

        except Exception as e:
            logger.error(f"Error resolving team name '{team_text}': {e}")
            return None

    def _extract_description_from_lines(self, lines: List[str]) -> str:
        """Extract betting description from lines."""
        try:
            description_parts = []
            for line in lines:
                if isinstance(line, str) and line.strip():
                    # Skip metadata lines
                    if any(keyword in line.lower() for keyword in ['fanatics', 'bet id', 'gambling', 'call']):
                        continue

                    # Clean up the line
                    clean_line = re.sub(r'[^\w\s@\-+.]', ' ', line)
                    clean_line = ' '.join(clean_line.split())
                    
                    if clean_line and len(clean_line) > 3:
                        description_parts.append(clean_line)

            return ' | '.join(description_parts[:3])  # Limit to 3 parts

        except Exception as e:
            logger.debug(f"Skipping line in description extraction (not a string or empty): {repr(line)} type={type(line)}")
            return ""

    def _is_valid_betting_line(self, line: str) -> bool:
        """Check if a line contains valid betting information."""
        try:
            if not line or not isinstance(line, str):
                return False

            # Skip metadata lines
            metadata_keywords = ['fanatics', 'bet id', 'gambling', 'call', '1-800']
            if any(keyword in line.lower() for keyword in metadata_keywords):
                return False

            # Look for betting indicators
            betting_indicators = ['over', 'under', 'ml', 'money', 'parlay', 'teaser', '+', '-']
            return any(indicator in line.lower() for indicator in betting_indicators)

        except Exception as e:
            logger.error(f"Error checking betting line validity: {e}")
            return False

    def _get_default_bet_data(self) -> Dict[str, Any]:
        """Return default bet data when parsing fails."""
        return {
            'teams': ['Unknown Team 1', 'Unknown Team 2'],
            'bet_type': 'Unknown',
            'bet_amount': None,
            'potential_payout': None,
            'odds': None,
            'description': 'Unable to parse betting slip',
            'legs': [],
            'parlay_type': None,
            'timestamp': datetime.now().isoformat(),
            'raw_text': ''
        } 