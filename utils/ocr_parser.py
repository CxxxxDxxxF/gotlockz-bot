import pytesseract
from PIL import Image
import re
from datetime import datetime

def extract_bet_info(image_path):
    raw_text = pytesseract.image_to_string(Image.open(image_path))

    # Basic example parsing (expand with more patterns)
    game_match = re.search(r"(\w+\s@\s\w+)", raw_text)
    pick_match = re.findall(r"(Over|Under|\+\d+\.\d+|\-\d+\.\d+|\d\+\sHit).*?\((\-?\d+)\)", raw_text)

    game = game_match.group(1) if game_match else "Unknown Matchup"
    picks = [
        {"description": pm[0], "odds": int(pm[1])} for pm in pick_match
    ]

    return {
        "game": game,
        "picks": picks,
        "date": datetime.now().strftime("%Y-%m-%d")
    }
