import os
import re
import aiohttp
import tempfile

import discord
from discord.ext import commands

import statsapi                              # MLB-StatsAPI
from pybaseball import playerid_lookup       # pybaseball lookup
from utils.ocr import extract_text           # OCR helper
from utils.sheets import init_sheets, log_pick, get_play_number  # Sheets logging

# 1) Your Discord token
TOKEN = os.getenv("DISCORD_TOKEN")

# 2) Map user keys → actual channel names (with and without emoji)
CHANNEL_MAP = {
    "🔒vip-plays":  "🔒vip-plays",
    "vip-plays":    "🔒vip-plays",
    "🏆free-plays": "🏆free-plays",
    "free-plays":   "🏆free-plays",
}

# 3) Configure Discord intents (required in discord.py v2.x)
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

# 4) Define your bot (must come before any @bot.command)
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    init_sheets()

@bot.command(name="player")
async def fetch_player(ctx, first_name: str, last_name: str):
    """
    Fetch player info from MLB StatsAPI and PyBaseball.
    """
    mlb_players = statsapi.lookup_player(f"{first_name} {last_name}")
    pb_players = playerid_lookup(first_name, last_name)
    await ctx.send(
        f"StatsAPI results: {mlb_players}\n"
        f"PyBaseball results: {pb_players.to_dict(orient='records')}"
    )

@bot.command(name="schedule")
async def fetch_schedule(ctx, team_id: int, start: str, end: str):
    """
    Fetch schedule for a team between two dates.
    """
    schedule = statsapi.schedule(start_date=start, end_date=end, team=team_id)
    await ctx.send(f"Schedule for team {team_id} from {start} to {end}: {schedule}")

@bot.command(name="postpick")
async def postpick(ctx, units: float, channel_key: str):
    """
    OCR a betting slip image, parse the pick, log to Google Sheets, and post it to the specified channel.
    Usage: !postpick <units> <channel_key> (attach image)
    """
    # 1) Ensure an image is attached
    if not ctx.message.attachments:
        return await ctx.send("❌ Please attach the bet‑slip image to your command message.")

    attachment = ctx.message.attachments[0]

    # 2) Download it
    async with aiohttp.ClientSession() as sess:
        resp = await sess.get(attachment.url)
        data = await resp.read()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    # 3) OCR it
    raw_text = extract_text(tmp_path)

    # 4) Parse the pick (supports Run Line & Money Line)
    pattern = r"([A-Za-z .']+)\s+([+-]?\d+\.?\d*)\s+(?:Run Line|Money Line)\s+([+-]?\d+)"
    m = re.search(pattern, raw_text)
    if m:
        team, line, odds = m.groups()
        mm = re.search(r"([A-Za-z .']+)\s+at\s+([A-Za-z .']+)", raw_text)
        matchup = f" at {mm.group(2)}" if mm else ""
        pick = f"{team.strip()} {line} {odds}{matchup}"
    else:
        pick = raw_text.strip().replace("\n", " ")

    # 5) Resolve destination channel
    valid = ", ".join(CHANNEL_MAP.keys())
    key = channel_key.strip()
    chan_name = CHANNEL_MAP.get(key) or CHANNEL_MAP.get(key.lower())
    if not chan_name:
        return await ctx.send(f"❌ Unknown key `{channel_key}`. Valid keys: {valid}")

    dest = discord.utils.get(ctx.guild.channels, name=chan_name)
    if not dest:
        return await ctx.send(f"❌ I can’t find a channel named `{chan_name}` here.")

    # 6) Log & post the pick
    play_num = get_play_number()
    log_pick(pick)
    await dest.send(f"🎯 Pick #{play_num}: {units}U on **{pick}**")

    # 7) Acknowledge in the command channel
    await ctx.send(f"✅ Posted pick #{play_num} to {dest.mention}")
