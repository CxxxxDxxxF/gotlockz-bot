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
-    "🔒vip-plays": "🔒vip-plays",
+    "🔒vip-plays": "🔒vip-plays",
+    "vip-plays":    "🔒vip-plays",     # ← add this line

-    "🏆free-plays": "🏆free-plays",
+    "🏆free-plays": "🏆free-plays",
+    "free-plays":   "🏆free-plays",    # ← and this line
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
    """
    Usage in Discord:
      !postpick 6 🔒vip-plays
      (attach your bet slip image to the same message)
    """
    # 1) Ensure an image is attached
    if not ctx.message.attachments:
        return await ctx.send("❌ Please attach the bet‑slip image to your command message.")

    attachment = ctx.message.attachments[0]

    # 2) Download the attachment to a temp file
    async with aiohttp.ClientSession() as sess:
        resp = await sess.get(attachment.url)
        data = await resp.read()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    # 3) OCR the image
    raw_text = extract_text(tmp_path)

    # 4) Parse out a simple pick string
    #    e.g. "Chicago Cubs -1.5 Run Line -120 Miami Marlins at Chicago Cubs"
    m = re.search(r"([A-Za-z ]+)\s+([-–]?\d+\.?\d*)\s+Run Line\s+([+-]?\d+)", raw_text)
    if not m:
        pick = raw_text.strip().replace("\n", " ")
    else:
        team, line, odds = m.groups()
        mm = re.search(r"([A-Za-z ]+ at [A-Za-z ]+)", raw_text)
        matchup = mm.group(1) if mm else ""
        pick = f"{team.strip()} {line} ({odds})  {matchup}"

    # 5) Determine destination channel
    chan_name = CHANNEL_MAP.get(channel_key)
    if not chan_name:
        valid = ", ".join(CHANNEL_MAP.keys())
        return await ctx.send(f"❌ Unknown key `{channel_key}`. Valid keys: {valid}")

    dest = discord.utils.get(ctx.guild.channels, name=chan_name)
    if not dest:
        return await ctx.send(f"❌ I can’t find a channel named `{chan_name}` here.")

    # 6) Log the pick
    play_num = get_play_number()
    log_pick(pick)

    # 7) Post to the target channel
    await dest.send(f"🎯 Pick #{play_num}: {units} U on **{pick}**")

    # 8) Acknowledge in the command channel
    await ctx.send(f"✅ Posted pick #{play_num} to {dest.mention}")


# Add more commands as needed...
