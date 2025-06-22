# image_processing.py

#!/usr/bin/env python3
"""
image_processing.py

Enhanced OCR extraction and parsing of bet slip details.
Supports: moneylines, props, parlays, teasers, and more.
"""
import logging
import re
from typing import Optional, Dict, Union, List, Any

import pytesseract
from PIL import Image, ImageEnhance
import cv2
import numpy as np

logger = logging.getLogger(__name__)


def preprocess_image(image_input: Union[str, bytes]) -> np.ndarray:
    """
    Enhanced image preprocessing for better OCR accuracy:
    - Loads image
    - Converts to grayscale
    - Applies deskew correction
    - Uses adaptive thresholding
    - Applies noise reduction
    - Resizes for optimal OCR
    Returns the processed binary NumPy array.
    """
    # Load image
    if isinstance(image_input, (bytes, bytearray)):
        arr = np.frombuffer(image_input, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise FileNotFoundError("Image bytes could not be decoded.")
    else:
        img = cv2.imread(image_input)
        if img is None:
            raise FileNotFoundError(
                f"Image not found or unreadable: {image_input}")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Deskew correction
    coords = np.column_stack(np.where(gray > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = 90 + angle
    (h, w) = gray.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # Noise reduction
    denoised = cv2.fastNlMeansDenoising(rotated)

    # Adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Resize for optimal OCR (maintain aspect ratio, max width 1200px)
    h, w = thresh.shape
    scale = min(1.0, 1200.0 / w)
    if scale < 1.0:
        resized = cv2.resize(
            thresh,
            (int(w * scale), int(h * scale)),
            interpolation=cv2.INTER_CUBIC
        )
    else:
        resized = thresh

    logger.debug(
        "Image preprocessed: deskew, denoise, adaptive threshold, resize")
    return resized


def extract_text_from_image(
    image_input: Union[str, bytes],
    config: Optional[str] = None
) -> str:
    """
    Uses Tesseract OCR to extract text from the preprocessed image.
    Optimized configuration for bet slips.
    """
    if config is None:
        # Optimized config for bet slips
        config = "--psm 6 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@+-.()/: "

    try:
        bin_img = preprocess_image(image_input)
        pil_img = Image.fromarray(bin_img)

        # Enhance contrast for better OCR
        enhancer = ImageEnhance.Contrast(pil_img)
        pil_img = enhancer.enhance(1.5)

        text = pytesseract.image_to_string(pil_img, config=config)
        logger.info(f"OCR extracted {len(text)} characters")
        return text
    except Exception as e:
        logger.exception("Failed to extract text from image")
        raise


def parse_bet_details(text: str) -> Optional[Dict[str, Any]]:
    """
    Enhanced parsing for various bet types:
    - Team moneylines: "Yankees at Red Sox +150"
    - Player props: "Player Over 1.5 Hits -120"
    - Parlays: "Yankees ML + Red Sox -1.5 +200"
    - Teasers: "Yankees -2.5 + Red Sox +3.5 -110"
    Returns a dict with parsed bet details.
    """
    logger.debug("Parsing bet details from OCR text")

    # Clean and normalize text
    text = re.sub(r'\s+', ' ', text.strip())

    # Try different bet type patterns
    patterns = [
        _parse_moneyline,
        _parse_player_prop,
        _parse_parlay,
        _parse_teaser,
        _parse_totals
    ]

    for pattern_func in patterns:
        result = pattern_func(text)
        if result:
            logger.info(f"Detected bet type: {result.get('type', 'unknown')}")
            return result

    logger.warning("No valid bet details found in OCR text")
    return None


def _parse_moneyline(text: str) -> Optional[Dict[str, Any]]:
    """Parse team moneyline bets."""
    # Pattern: "Team1 at Team2 +150" or "Team1 @ Team2 -190"
    pattern = r'([A-Za-z\s]+?)\s+(?:at|@)\s+([A-Za-z\s]+?)\s+([-+]\d{2,4})'
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        team1 = match.group(1).strip()
        team2 = match.group(2).strip()
        odds = match.group(3)

        return {
            "type": "moneyline",
            "away": team1,
            "home": team2,
            "bet": f"{team1} Moneyline",
            "odds": odds,
            "game": f"{team1} @ {team2}"
        }
    return None


def _parse_player_prop(text: str) -> Optional[Dict[str, Any]]:
    """Parse player prop bets."""
    # Pattern: "Player Over/Under X.Y Stat -120"
    pattern = r'([A-Za-z\s]+?)\s+(Over|Under)\s+([\d\.]+)\s+([A-Za-z\s]+?)\s+([-+]\d{2,4})'
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        player = match.group(1).strip()
        direction = match.group(2).capitalize()
        value = match.group(3)
        stat = match.group(4).strip()
        odds = match.group(5)

        return {
            "type": "player_prop",
            "player": player,
            "bet": f"{direction} {value} {stat}",
            "odds": odds,
            "direction": direction,
            "value": value,
            "stat": stat
        }
    return None


def _parse_parlay(text: str) -> Optional[Dict[str, Any]]:
    """Parse parlay bets."""
    # Pattern: "Team1 ML + Team2 -1.5 +200" or similar
    pattern = r'(.+?)\s+([-+]\d{2,4})'
    matches = re.findall(pattern, text)

    if len(matches) >= 2:  # At least 2 legs for a parlay
        legs = [match[0].strip() for match in matches[:-1]]  # All but last
        odds = matches[-1][1]  # Last match is the parlay odds

        return {
            "type": "parlay",
            "legs": legs,
            "bet": f"Parlay: {' + '.join(legs)}",
            "odds": odds,
            "leg_count": len(legs)
        }
    return None


def _parse_teaser(text: str) -> Optional[Dict[str, Any]]:
    """Parse teaser bets."""
    # Pattern: "Team1 -2.5 + Team2 +3.5 -110"
    pattern = r'(.+?)\s+([-+]\d{2,4})'
    matches = re.findall(pattern, text)

    if len(matches) >= 2:
        legs = [match[0].strip() for match in matches[:-1]]
        odds = matches[-1][1]

        return {
            "type": "teaser",
            "legs": legs,
            "bet": f"Teaser: {' + '.join(legs)}",
            "odds": odds,
            "leg_count": len(legs)
        }
    return None


def _parse_totals(text: str) -> Optional[Dict[str, Any]]:
    """Parse over/under totals."""
    # Pattern: "Over/Under X.Y -110"
    pattern = r'(Over|Under)\s+([\d\.]+)\s+([-+]\d{2,4})'
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        direction = match.group(1).capitalize()
        total = match.group(2)
        odds = match.group(3)

        return {
            "type": "total",
            "bet": f"{direction} {total}",
            "odds": odds,
            "direction": direction,
            "total": total
        }
    return None


def calculate_implied_probability(odds: str) -> float:
    """
    Calculate implied probability from American odds.
    Returns probability as decimal (0.0 to 1.0).
    """
    try:
        odds_int = int(odds)
        if odds_int > 0:
            return 100 / (odds_int + 100)
        else:
            return abs(odds_int) / (abs(odds_int) + 100)
    except (ValueError, TypeError):
        logger.warning(f"Invalid odds format: {odds}")
        return 0.0


def calculate_edge(implied_prob: float, true_prob: float) -> float:
    """
    Calculate betting edge (difference between true and implied probability).
    Returns edge as percentage.
    """
    return (true_prob - implied_prob) * 100
