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
        """Parse betting data from extracted text. Handles all Fanatics MLB slip types, with improved SGP/parlay leg extraction."""
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

            lines = [l.strip() for l in text.splitlines() if l.strip()]
            logger.info(f"Non-empty OCR lines: {lines}")

            # Improved SGP/parlay leg extraction
            legs = []
            i = 0
            while i < len(lines):
                # Look for a player prop or over/under leg
                player_match = re.match(r'^([A-Z][a-z]+(?: [A-Z][a-z]+)* ?\d*\+?)$', lines[i])
                ou_match = re.match(r'^(Over|Under) ?([\d\.]+)', lines[i])
                if player_match:
                    player = player_match.group(1)
                    desc = ''
                    teams = []
                    odds = None
                    # Next line: prop/description?
                    if i+1 < len(lines) and not re.search(r'at', lines[i+1], re.IGNORECASE):
                        desc = lines[i+1]
                        i += 1
                    # Next line: matchup?
                    if i+1 < len(lines) and re.search(r'at', lines[i+1], re.IGNORECASE):
                        matchup = lines[i+1]
                        matchup_teams = re.findall(r'([A-Za-z ]+) at ([A-Za-z ]+)', matchup)
                        if matchup_teams:
                            teams = [self._resolve_team_name(matchup_teams[0][0].strip()), self._resolve_team_name(matchup_teams[0][1].strip())]
                        i += 1
                    # Next line: odds?
                    if i+1 < len(lines) and re.match(r'^[+-]\d{2,4}$', lines[i+1]):
                        odds = lines[i+1]
                        i += 1
                    leg = {'player': player}
                    if desc:
                        leg['description'] = desc
                    if teams:
                        leg['teams'] = teams
                    if odds:
                        leg['odds'] = odds
                    legs.append(leg)
                elif ou_match:
                    desc = f"{ou_match.group(1)} {ou_match.group(2)}"
                    teams = []
                    odds = None
                    # Next line: player/prop?
                    if i+1 < len(lines) and not re.search(r'at', lines[i+1], re.IGNORECASE):
                        desc += f" {lines[i+1]}"
                        i += 1
                    # Next line: matchup?
                    if i+1 < len(lines) and re.search(r'at', lines[i+1], re.IGNORECASE):
                        matchup = lines[i+1]
                        matchup_teams = re.findall(r'([A-Za-z ]+) at ([A-Za-z ]+)', matchup)
                        if matchup_teams:
                            teams = [self._resolve_team_name(matchup_teams[0][0].strip()), self._resolve_team_name(matchup_teams[0][1].strip())]
                        i += 1
                    # Next line: odds?
                    if i+1 < len(lines) and re.match(r'^[+-]\d{2,4}$', lines[i+1]):
                        odds = lines[i+1]
                        i += 1
                    leg = {'description': desc}
                    if teams:
                        leg['teams'] = teams
                    if odds:
                        leg['odds'] = odds
                    legs.append(leg)
                else:
                    i += 1
            # If we found multiple legs, treat as parlay/SGP
            if len(legs) > 1:
                bet_data['is_parlay'] = True
                bet_data['legs'] = legs
                # Set teams as all unique teams from legs
                all_teams = []
                for leg in legs:
                    if 'teams' in leg:
                        all_teams.extend(leg['teams'])
                unique_teams = list(dict.fromkeys([t for t in all_teams if t and t != 'TBD']))
                if len(unique_teams) >= 2:
                    bet_data['teams'] = [unique_teams[0], unique_teams[1]]  # type: ignore
                elif len(unique_teams) == 1:
                    bet_data['teams'] = [unique_teams[0], unique_teams[0]]  # type: ignore
                else:
                    bet_data['teams'] = ['TBD', 'TBD']  # type: ignore
                # Description: SGP summary
                leg_descs = []
                for leg in legs:
                    if 'player' in leg and 'description' in leg:
                        leg_descs.append(f"{leg['player']} {leg['description']}")
                    elif 'player' in leg:
                        leg_descs.append(leg['player'])
                    elif 'description' in leg:
                        leg_descs.append(leg['description'])
                if leg_descs:
                    bet_data['description'] = f"{len(legs)} Leg SGP: {', '.join(leg_descs)}"
            else:
                # Fallback to original parsing for single-leg bets
                # 1. Extract odds (top right or keyword lines)
                odds = None
                odds_patterns = [
                    r'^([+-]\d{2,4})$'  # Only accept lines that are just odds
                ]
                skip_keywords = ['gambler', '1-800', 'bet id', 'call']
                valid_odds_lines = []
                for line in lines:
                    line_stripped = line.strip()
                    if any(k in line_stripped.lower() for k in skip_keywords):
                        continue
                    # Only consider lines that are just a valid odds value
                    if re.match(r'^[+-]\d{2,4}$', line_stripped):
                        # Explicitly ignore -800 (phone number)
                        if line_stripped == '-800':
                            continue
                        valid_odds_lines.append(line_stripped)
                if valid_odds_lines:
                    odds = valid_odds_lines[-1]  # Pick the last valid odds line
                # Fallback: previous logic if nothing found
                if not odds:
                    for line in lines:
                        if any(k in line.lower() for k in skip_keywords):
                            continue
                        for pattern in [r'(?i)odds[:\s]*([+-]?\d{2,4})', r'(?i)line[:\s]*([+-]?\d{2,4})', r'(?i)price[:\s]*([+-]?\d{2,4})', r'\b([+-]\d{3,4})\b', r'\b([+-]\d{2,3})\b']:
                            match = re.search(pattern, line)
                            if match and self._is_valid_odds(match.group(1)) and match.group(1) != '-800':
                                odds = match.group(1)
                                break
                        if odds:
                            break
                if odds:
                    bet_data['odds'] = odds
                    logger.info(f"Extracted odds: {odds}")
                else:
                    logger.info("No valid odds found.")
                # 4. Extract all team matchups (e.g., New York Yankees at Cincinnati Reds)
                matchup_pattern = r'([A-Za-z ]+) at ([A-Za-z ]+)'  # e.g., New York Yankees at Cincinnati Reds
                matchups = re.findall(matchup_pattern, text)
                teams_found = []
                if matchups:
                    main_matchup = matchups[0]
                    teams_found = [self._resolve_team_name(main_matchup[0].strip()), self._resolve_team_name(main_matchup[1].strip())]
                    bet_data['teams'] = teams_found
                    logger.info(f"Extracted teams: {bet_data['teams']}")
                # 2. Extract bet description
                bet_keywords = ['over', 'under', 'money line', 'no', 'yes', 'parlay', 'inning', 'earned runs', 'alt', 'hits', 'runs', 'rbis', '+', '-']
                branding_keywords = ['fanatics sportsbook', 'fanatics', 'sportsbook']
                def is_team_line(line):
                    line_lower = line.lower()
                    return any(team.lower() in line_lower for team in teams_found if team and team != 'TBD')
                description = None
                for i, line in enumerate(lines):
                    line_lower = line.lower()
                    if any(b in line_lower for b in branding_keywords):
                        continue
                    if is_team_line(line):
                        continue
                    if 'money line' in line_lower:
                        pick_team = None
                        for candidate in lines:
                            candidate_lower = candidate.lower()
                            if any(b in candidate_lower for b in branding_keywords):
                                continue
                            if candidate and candidate != line and not candidate.isdigit() and not candidate.startswith('-') and not candidate.startswith('+'):
                                pick_team = candidate.strip()
                                break
                        if pick_team:
                            description = f"{pick_team} Money Line"
                        else:
                            description = line.strip()
                        logger.info(f"Selected bet description as Money Line (top team): {description}")
                        break
                    player_prop_match = re.match(r'([A-Z][a-z]+(?: [A-Z][a-z]+)*)(?: - )?([A-Za-z ]+)?', line)
                    if player_prop_match and player_prop_match.group(2):
                        description = f"{player_prop_match.group(1).strip()} {player_prop_match.group(2).strip()}"
                        logger.info(f"Selected bet description as player prop: {description}")
                        break
                    if any(k in line_lower for k in bet_keywords) or re.search(r'\d+\+', line):
                        description = line.strip()
                        logger.info(f"Selected bet description by keyword: {description}")
                        break
                if not description:
                    for line in lines:
                        line_lower = line.lower()
                        if any(b in line_lower for b in branding_keywords):
                            continue
                        if is_team_line(line):
                            continue
                        description = line.strip()
                        logger.info(f"Selected bet description by fallback: {description}")
                        break
                if description:
                    bet_data['description'] = description
                logger.info(f"Extracted bet type/description: {bet_data['description']}")
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