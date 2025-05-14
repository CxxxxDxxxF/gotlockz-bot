import os
import re
import shutil
from io import BytesIO
from datetime import date

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from PIL import Image
import pytesseract
import openai
from mlb_statsapi import MLBStatsAPI
from pybaseball import statcast_pitcher_summary, statcast_batter_vs_pitcher, cache
from utils.sheets import log_pick, get_play_number

# Enable caching for pybaseball
cache.enable()

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Verify Tesseract is installed
if shutil.which("tesseract") is None:
    raise RuntimeError("Tesseract OCR not found on PATH. Install 'tesseract-ocr' on your host.")

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# MLB API client
mlb = MLBStatsAPI()

def extract_text(image_bytes):
    image = Image.open(image_bytes)
    raw = pytesseract.image_to_string(image)
    data = {"team": None, "line": None, "odds": None,
            "bet_type": None, "wager": None,
            "home_team": None, "away_team": None}

    for line in map(str.strip, raw.splitlines()):
        if not line:
            continue
        if "$" in line:
            m = re.search(r"\$(\d+\.\d{2})", line)
            if m:
                data["wager"] = m.group(1)
        if re.search(r"\b-?\d+\.?\d*\b.*\b-?\d{2,3}\b", line):
            parts = line.split()
            if len(parts) >= 3:
                data["team"] = " ".join(parts[:-2])
                data["line"], data["odds"] = parts[-2], parts[-1]
        if "line" in line.lower():
            data["bet_type"] = line
        if " at " in line.lower():
            a, h = re.split(r"\s+at\s+", line, flags=re.IGNORECASE)
            data["away_team"], data["home_team"] = a.title(), h.title()

    if not all([data["team"], data["home_team"], data["away_team"]]):
        raise ValueError("❌ OCR failed to extract key bet slip data.")
    return data

def get_stat_summary(home_team, away_team):
    today = date.today().isoformat()
    games = mlb.get_games_for_date(today)
    for g in games:
        if home_team.lower() in g['home_name'].lower() and away_team.lower() in g['away_name'].lower():
            hp, ap = g.get('home_probable_pitcher'), g.get('away_probable_pitcher')
            hs = mlb.get_team_stats_by_id(g['home_id'])
            as_ = mlb.get_team_stats_by_id(g['away_id'])
            summary = []
            if hp:
                summary.append(f"{hp['first_name']} {hp['last_name']} starts for {home_team} (ERA {hp['era']}, WHIP {hp['whip']}, K/9 {hp['k9']}).")
            if ap:
                summary.append(f"{ap['first_name']} {ap['last_name']} starts for {away_team} (ERA {ap['era']}, WHIP {ap['whip']}, K/9 {ap['k9']}).")
            summary.append(f"{home_team}: AVG .{hs['batting']['avg']}, R/G {hs['batting']['runs_per_game']}, Bullpen ERA {hs['pitching']['era']}.")
            summary.append(f"{away_team}: AVG .{as_['batting']['avg']}, R/G {as_['batting']['runs_per_game']}, Bullpen ERA {as_['pitching']['era']}.")
            return " ".join(summary)
    return "No stat summary available."

def generate_gpt_writeup(bet, units, num, kind, tone):
    stats = get_stat_summary(bet['home_team'], bet['away_team'])
    prompt = (
        f"Generate a {tone} {kind.upper()} sports betting write-up.\n"
        f"Team: {bet['team']}\nLine: {bet['line']}\nOdds: {bet['odds']}\nUnits: {units}\n"
        f"Bet Type: {bet['bet_type']}\nMatchup: {bet['away_team']} at {bet['home_team']}\n"
        f"Play Number: {num}\n\nStats: {stats}\n\nMake it persuasive, confident, and include emojis."
    )
    res = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return res.choices[0].message.content.strip()

async def handle_pick(inter, units, channel, kind, tone):
    if not inter.attachments:
        return await inter.response.send_message("❌ Please attach a bet slip image.", ephemeral=True)
    try:
        img = await inter.attachments[0].read()
        bet = extract_text(BytesIO(img))
        num = get_play_number(kind.upper()) + 1
        text = generate_gpt_writeup(bet, units, num, kind, tone)
        post = f"**{kind.upper()} PLAY #{num}**\n{text}\n\nChannel: {channel}"
        await inter.response.send_message(post)
        # offload Google Sheets write
        bot.loop.run_in_executor(None, log_pick, kind.upper(), bet["home_team"], bet["away_team"], units, bet["line"], bet["odds"])
    except Exception as e:
        await inter.response.send_message(f"❌ Error: {e}", ephemeral=True)

@tree.command(name="postpick", description="Post a VIP betting pick")
@app_commands.describe(units="Units risked", channel="Where it's posted", tone="Tone (default: hype)")
async def postpick(inter: discord.Interaction, units: float, channel: str, tone: str="hype"):
    await handle_pick(inter, units, channel, "VIP", tone)

@tree.command(name="freepick", description="Post a Free betting pick")
@app_commands.describe(units="Units risked", channel="Where it's posted", tone="Tone (default: hype)")
async def freepick(inter: discord.Interaction, units: float, channel: str, tone: str="hype"):
    await handle_pick(inter, units, channel, "Free", tone)

__all__ = ["bot"]
