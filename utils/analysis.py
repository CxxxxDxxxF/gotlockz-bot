import openai
import os
from datetime import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_analysis(bet_info, game_stats):
    today = datetime.now().strftime("%m/%d/%y")
    matchup = bet_info['game']
    start_time = game_stats['start_time']
    pitcher_info = f"Probable Pitchers: {game_stats['away_pitcher']} vs {game_stats['home_pitcher']}"

    pick_lines = "\n".join([
        f"🏆 I {p['description']} ({p['odds']})" for p in bet_info['picks']
    ])

    prompt = (
        f"Write a confident, stat-backed, hype betting breakdown for this MLB matchup on {today}:\n"
        f"{matchup} at {start_time}\n"
        f"{pitcher_info}\n"
        f"Picks: {', '.join([p['description'] for p in bet_info['picks']])}\n"
        f"Tone should sound smart and fun, like a pro sports bettor hyping up a VIP play.\n"
        f"End it with an all caps rally line like LET'S CASH or LET’S PRINT 💰."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']
