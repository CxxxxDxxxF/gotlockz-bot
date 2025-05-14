# gotlockz_bot.py
import discord
from discord.ext import commands
from discord import app_commands
from io import BytesIO
from PIL import Image
import pytesseract
import re
import os
import openai
from dotenv import load_dotenv
from datetime import date
from mlbstatsapi import MLBStatsAPI
from pybaseball import playerid_lookup, statcast_batter_vs_pitcher, cache
from utils.sheets import log_pick, get_play_number

# Enable caching for pybaseball
cache.enable()

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up Discord bot with slash command support
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# MLB API
mlb = MLBStatsAPI()

# Extract slip text using OCR
def extract_text(image_bytes):
    image = Image.open(image_bytes)
    raw_text = pytesseract.image_to_string(image)
    data = {"team": None, "line": None, "odds": None, "bet_type": None, "wager": None, "home_team": None, "away_team": None}
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    for line in lines:
        if "$" in line:
            match = re.search(r"\$(\d+\.\d{2})", line)
            if match:
                data["wager"] = match.group(1)
        if re.search(r"\b-?\d+\.?\d*\b.*\b-?\d{2,3}\b", line):
            parts = line.split()
            if len(parts) >= 3:
                data["team"] = " ".join(parts[:-2])
                data["line"] = parts[-2]
                data["odds"] = parts[-1]
        if "line" in line.lower():
            data["bet_type"] = line.strip()
        if " at " in line.lower():
            matchup = re.split(r"\s+at\s+", line, flags=re.IGNORECASE)
            if len(matchup) == 2:
                data["away_team"] = matchup[0].title()
                data["home_team"] = matchup[1].title()
    if not data["home_team"] or not data["away_team"] or not data["team"]:
        raise ValueError("❌ OCR failed to extract key bet slip data.")
    return data

# Get matchup stats summary
def get_stat_summary(home_team, away_team):
    today = date.today().isoformat()
    games = mlb.get_games_for_date(today)
    for game in games:
        if home_team.lower() in game['home_name'].lower() and away_team.lower() in game['away_name'].lower():
            home_pitcher = game.get('home_probable_pitcher')
            away_pitcher = game.get('away_probable_pitcher')
            home_stats = mlb.get_team_stats_by_id(game['home_id'])
            away_stats = mlb.get_team_stats_by_id(game['away_id'])
            summary = []
            if home_pitcher:
                summary.append(f"{home_pitcher['first_name']} {home_pitcher['last_name']} starts for {home_team} (ERA {home_pitcher['era']}, WHIP {home_pitcher['whip']}, K/9 {home_pitcher['k9']}).")
            if away_pitcher:
                summary.append(f"{away_pitcher['first_name']} {away_pitcher['last_name']} starts for {away_team} (ERA {away_pitcher['era']}, WHIP {away_pitcher['whip']}, K/9 {away_pitcher['k9']}).")
            summary.append(f"{home_team}: AVG .{home_stats['batting']['avg']}, R/G {home_stats['batting']['runs_per_game']}, Bullpen ERA {home_stats['pitching']['era']}.")
            summary.append(f"{away_team}: AVG .{away_stats['batting']['avg']}, R/G {away_stats['batting']['runs_per_game']}, Bullpen ERA {away_stats['pitching']['era']}.")
            return " ".join(summary)
    return "No stat summary available."

# Generate GPT writeup
def generate_gpt_writeup(bet, units, play_number, pick_type, tone):
    stats = get_stat_summary(bet['home_team'], bet['away_team'])
    prompt = (
        f"Generate a {tone} {pick_type.upper()} sports betting write-up.\n"
        f"Team: {bet['team']}\nLine: {bet['line']}\nOdds: {bet['odds']}\nUnits: {units}\nBet Type: {bet['bet_type']}\nMatchup: {bet['away_team']} at {bet['home_team']}\nPlay Number: {play_number}\n\nStats: {stats}\n\nMake it persuasive, confident, and include emojis."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return response['choices'][0]['message']['content']

# Core handler
async def handle_pick(interaction, units, channel_name, pick_type, tone):
    if not interaction.attachments:
        await interaction.response.send_message("❌ Please attach a bet slip image.", ephemeral=True)
        return
    try:
        attachment = interaction.attachments[0]
        image_bytes = await attachment.read()
        bet = extract_text(BytesIO(image_bytes))
        play_number = get_play_number(pick_type.upper()) + 1
        writeup = generate_gpt_writeup(bet, units, play_number, pick_type, tone)
        post = f"**{pick_type.upper()} PLAY #{play_number}**\n{writeup}\n\nChannel: {channel_name}"
        await interaction.response.send_message(post)
        log_pick(pick_type.upper(), bet["home_team"], bet["away_team"], units, bet["line"], bet["odds"])
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

# Slash command: /postpick
@tree.command(name="postpick", description="Post a VIP betting pick")
@app_commands.describe(units="Units risked", channel_name="Where it's being posted", tone="Tone (default: hype)")
async def postpick(interaction: discord.Interaction, units: float, channel_name: str, tone: str = "hype"):
    await handle_pick(interaction, units, channel_name, "VIP", tone)

# Slash command: /freepick
@tree.command(name="freepick", description="Post a Free betting pick")
@app_commands.describe(units="Units risked", channel_name="Where it's being posted", tone="Tone (default: hype)")
async def freepick(interaction: discord.Interaction, units: float, channel_name: str, tone: str = "hype"):
    await handle_pick(interaction, units, channel_name, "Free", tone)

# Expose bot to main
__all__ = ["bot"]
