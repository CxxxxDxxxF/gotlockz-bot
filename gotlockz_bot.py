import os
from discord.ext import commands
import statsapi              # corrected import for MLB-StatsAPI
from pybaseball import playerid_lookup  # pybaseball as additional source
from utils.ocr import extract_text
from utils.sheets import init_sheets, log_pick, get_play_number

# Load Discord token from environment variable
TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    init_sheets()

@bot.command(name="player")
async def fetch_player(ctx, first_name: str, last_name: str):
    # Lookup via MLB-StatsAPI
    mlb_players = statsapi.lookup_player(f"{first_name} {last_name}")
    # Fallback via pybaseball
    pb_players = playerid_lookup(first_name, last_name)
    await ctx.send(f"StatsAPI results: {mlb_players}\nPybaseball results: {pb_players.to_dict(orient='records')}")

@bot.command(name="schedule")
async def fetch_schedule(ctx, team_id: int, start: str, end: str):
    schedule = statsapi.schedule(start_date=start, end_date=end, team=team_id)
    await ctx.send(f"Schedule for team {team_id} from {start} to {end}: {schedule}")

# Add more commands as needed...