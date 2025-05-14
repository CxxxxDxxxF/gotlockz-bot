import os
import re
import tempfile
import aiohttp
import discord
from discord.ext import commands
import statsapi                  # MLB-StatsAPI
from pybaseball import playerid_lookup
from utils.ocr import extract_text
from utils.sheets import init_sheets, log_pick, get_play_number

CHANNEL_MAP = {
"🔒vip-plays": "🔒vip-plays",
"🔒vip-plays": "🔒vip-plays",
"vip-plays":    "🔒vip-plays",     # ← add this line

"🏆free-plays": "🏆free-plays",
"🏆free-plays": "🏆free-plays",
"free-plays":   "🏆free-plays",    # ← and this line
 }

# Load your Discord token
TOKEN = os.getenv("DISCORD_TOKEN")

# Configure Discord intents (required in discord.py v2.x)
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    init_sheets()


@bot.command(name="player")
async def fetch_player(ctx, first_name: str, last_name: str):
    mlb_players = statsapi.lookup_player(f"{first_name} {last_name}")
    pb_players = playerid_lookup(first_name, last_name)
    await ctx.send(
        f"StatsAPI results: {mlb_players}\n"
        f"Pybaseball results: {pb_players.to_dict(orient='records')}"
    )


@bot.command(name="schedule")
async def fetch_schedule(ctx, team_id: int, start: str, end: str):
    schedule = statsapi.schedule(start_date=start, end_date=end, team=team_id)
    await ctx.send(f"Schedule for team {team_id} from {start} to {end}: {schedule}")


@bot.command(name="postpick")
async def postpick(ctx, units: float, channel_key: str):
    # … your OCR + parsing code above …

    # 5) Determine destination channel
    valid = ", ".join(CHANNEL_MAP.keys())
    chan_name = CHANNEL_MAP.get(channel_key)
    if not chan_name:
        return await ctx.send(
            f"✖ Unknown key `{channel_key}`. Valid keys: {valid}"
        )

    dest = discord.utils.get(ctx.guild.channels, name=chan_name)
    if not dest:
        return await ctx.send(
            f"✖ I can’t find a channel named `{chan_name}` here."
        )

    # 6) Log the pick
    play_num = get_play_number()
    log_pick(pick)

    # 7) Post to the target channel
    await dest.send(f"🎯 Pick #{play_num}: {units}U on **{pick}**")

    # 8) Acknowledge in the command channel
    await ctx.send(f"✅ Posted pick #{play_num} to {dest.mention}")
