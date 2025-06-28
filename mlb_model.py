import os

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

OPENWEATHERMAP_KEY = os.getenv("OPENWEATHERMAP_KEY")
ODDS_API_KEY = os.getenv("The_Odds_API")  # Updated to match your Render env var


# --- Mapping helpers ---
def map_city_to_team():
    # Example: expand as needed
    return {
        "New York": "NYY",
        "Los Angeles": "LAD",
        "Chicago": "CHC",
        "Boston": "BOS",
        "Atlanta": "ATL",
        # ... add more as needed
    }


def map_name_to_team_code():
    # Example: expand as needed
    return {
        "New York Yankees": "NYY",
        "Los Angeles Dodgers": "LAD",
        "Chicago Cubs": "CHC",
        "Boston Red Sox": "BOS",
        "Atlanta Braves": "ATL",
        # ... add more as needed
    }


# --- Weather ---
def get_weather_for_city(city):
    """Query OpenWeatherMap for a single city, return (temp, wind) or None if error."""
    url = f"https://api.openweathermap.org/data/2.5/weather" f"?q={city}&appid={OPENWEATHERMAP_KEY}&units=imperial"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        temp = data["main"]["temp"]
        wind = data["wind"]["speed"]
        return temp, wind
    except Exception as e:
        print(f"Weather API error for {city}: {e}")
        return None


def get_weather():
    """Get weather for all mapped MLB cities, return DataFrame with team, temp, wind."""
    city_team = map_city_to_team()
    records = []
    for city, team in city_team.items():
        result = get_weather_for_city(city)
        if result:
            temp, wind = result
            records.append({"team": team, "temp": temp, "wind": wind})
    return pd.DataFrame(records)


# --- Odds ---
def get_odds():
    """Get Vegas totals from The Odds API, return DataFrame with team, vegas_total."""
    url = (
        "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/" f"?apiKey={ODDS_API_KEY}&regions=us&markets=totals"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        games = resp.json()
    except Exception as e:
        print(f"Odds API error: {e}")
        return pd.DataFrame([])

    name_to_code = map_name_to_team_code()
    records = []
    for game in games:
        # Each game has 'home_team', 'away_team', and 'bookmakers'
        # home = game.get("home_team")
        # away = game.get("away_team")
        # Find the first bookmaker with totals
        for bookmaker in game.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                if market.get("key") == "totals":
                    for outcome in market.get("outcomes", []):
                        # Each outcome is for a team or the game
                        # We'll use the 'name' field to map to team code
                        team_name = outcome.get("name")
                        total = outcome.get("point")
                        team_code = name_to_code.get(team_name)
                        if team_code and total is not None:
                            records.append({"team": team_code, "vegas_total": float(total)})
                    break  # Only use first totals market
            if records:
                break  # Only use first bookmaker with totals
    return pd.DataFrame(records)


# --- Merge ---
def merge_data(batting, pitching, statcast, weather, odds):
    df = batting.merge(pitching, on="team", suffixes=("_bat", "_pit"))
    df = df.merge(weather, on="team", how="left")
    df = df.merge(odds, on="team", how="left")
    # Drop any rows missing vegas_total or temp (no dummy fallback)
    df = df.dropna(subset=["vegas_total", "temp"])
    return df
