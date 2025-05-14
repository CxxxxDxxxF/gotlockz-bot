
from datetime import datetime, timezone, timedelta
import statsapi

def get_game_time(team, opp):
    today = datetime.now().strftime("%Y-%m-%d")
    for g in statsapi.schedule(sportId=1, date=today):
        if {g["home_name"], g["away_name"]} == {team, opp}:
            iso = g["game_datetime"].replace("Z","+00:00")
            dt = datetime.fromisoformat(iso)
            est = dt.astimezone(timezone(timedelta(hours=-4)))
            return est.strftime("%I:%M %p EST")
    return datetime.now().strftime("%I:%M %p EST")

def get_probable_pitchers(team, opp):
    today = datetime.now().strftime("%Y-%m-%d")
    games = statsapi.schedule(sportId=1, date=today, hydrate=["probablePitchers"])
    for g in games:
        home, away = g["home_team_name"], g["away_team_name"]
        if {home, away} == {team, opp}:
            if team == away:
                tp = g.get("away_probable_pitcher",{}) or {}
                op = g.get("home_probable_pitcher",{}) or {}
            else:
                tp = g.get("home_probable_pitcher",{}) or {}
                op = g.get("away_probable_pitcher",{}) or {}
            return tp.get("fullName","Unknown"), op.get("fullName","Unknown")
    return "Unknown", "Unknown"
