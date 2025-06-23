#!/usr/bin/env python3
"""
Test script for improved OCR parsing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'bot'))

from bot.utils.ocr import ocr_parser

def test_ocr_parsing():
    """Test the improved OCR parsing with sample text."""
    
    # Sample text from the logs
    sample_text = """Fanatics Sportsbook
San Francisco Giants
San Francisco Giants
Money Line
Boston Red Sox at San Fra..."""
    
    print("Testing OCR parsing with sample text:")
    print("=" * 50)
    print(f"Input text:\n{sample_text}")
    print("=" * 50)
    
    # Parse the betting details
    bet_data = ocr_parser.parse_betting_details(sample_text)
    
    print("Parsed bet data:")
    print(f"Teams: {bet_data['teams']}")
    print(f"Player: {bet_data['player']}")
    print(f"Description: {bet_data['description']}")
    print(f"Odds: {bet_data['odds']}")
    print(f"Units: {bet_data['units']}")
    print(f"Game Time: {bet_data['game_time']}")
    print(f"Sport: {bet_data['sport']}")
    
    # Test with more complete text
    print("\n" + "=" * 50)
    print("Testing with more complete text:")
    
    complete_text = """Fanatics Sportsbook
San Francisco Giants
Money Line
Boston Red Sox at San Francisco Giants
-800
1 Unit"""
    
    print(f"Input text:\n{complete_text}")
    print("=" * 50)
    
    bet_data2 = ocr_parser.parse_betting_details(complete_text)
    
    print("Parsed bet data:")
    print(f"Teams: {bet_data2['teams']}")
    print(f"Player: {bet_data2['player']}")
    print(f"Description: {bet_data2['description']}")
    print(f"Odds: {bet_data2['odds']}")
    print(f"Units: {bet_data2['units']}")
    print(f"Game Time: {bet_data2['game_time']}")
    print(f"Sport: {bet_data2['sport']}")

def test_team_name_cleaning():
    """Test the improved team name cleaning."""
    print("\n" + "=" * 50)
    print("Testing team name cleaning:")
    print("=" * 50)
    
    test_cases = [
        "San Fra",
        "San Francisco",
        "Boston Red Sox",
        "Sox",
        "Giants",
        "SF",
        "BOS"
    ]
    
    for team_name in test_cases:
        cleaned = ocr_parser._clean_team_name(team_name)
        print(f"'{team_name}' -> '{cleaned}'")

if __name__ == "__main__":
    test_ocr_parsing()
    test_team_name_cleaning() 