from mlbstatsapi import MLBStatsAPI
from datetime import datetime

api = MLBStatsAPI()

def get_game_stats(bet_info):
    team1, team2 = [team.strip() for team in bet_info['game'].split('@')]
    today = datetime.now().strftime('%Y-%m-%d')

    schedule = api.get_schedule(date=today, sportId=1)

    for game in schedule['dates'][0]['games']:
        if team1 in game['teams']['away']['team']['name'] and team2 in game['teams']['home']['team']['name']:
            return {
                "start_time": game['gameDate'],
                "away_pitcher": game['teams']['away'].get('probablePitcher', {}).get('fullName', 'TBD'),
                "home_pitcher": game['teams']['home'].get('probablePitcher', {}).get('fullName', 'TBD')
            }

    return {"start_time": "Unknown", "away_pitcher": "TBD", "home_pitcher": "TBD"}
