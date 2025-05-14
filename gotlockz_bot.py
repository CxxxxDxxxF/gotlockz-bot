import discord
from discord.ext import commands
from io import BytesIO
import pytesseract
from PIL import Image
import re
import openai

from utils.sheets import log_pick, get_play_number

# ------------------ CONFIG ------------------
DISCORD_TOKEN = "YOUR_DISCORD_BOT_TOKEN"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
openai.api_key = OPENAI_API_KEY
# -------------------------------------------

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot is live as {bot.user}")

# ------------------ OCR PARSER ------------------
def extract_text(image_bytes):
    image = Image.open(image_bytes)
    raw_text = pytesseract.image_to_string(image)

    data = {
        "team": None,
        "line": None,
        "odds": None,
        "bet_type": None,
        "wager": None,
        "home_team": None,
        "away_team": None
    }

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
        raise ValueError("❌ Could not parse teams — check image quality.")

    return data

# ------------------ FAKE STATS FUNCTION ------------------
def get_stat_summary(home_team, away_team):
    return (
        f"{home_team} has won 6 of their last 8 home games and ranks top 5 in bullpen ERA. "
        f"{away_team}, on the other hand, is hitting just .210 over their last 7 and has lost 4 straight road games. "
        f"Look for the pitching edge to be huge in this matchup."
    )

# ------------------ GPT WRITE-UP ------------------
def generate_gpt_writeup(bet, units, play_number, pick_type):
    stats = get_stat_summary(bet['home_team'], bet['away_team'])
    prompt = (
        f"Write a confident, hype-driven {pick_type.upper()} betting preview.\n\n"
        f"Team: {bet['team']}\n"
        f"Line: {bet['line']}\n"
        f"Bet Type: {bet['bet_type']}\n"
        f"Matchup: {bet['away_team']} at {bet['home_team']}\n"
        f"Odds: {bet['odds']}\n"
        f"Units: {units}\n"
        f"Stats: {stats}\n"
        f"This is {pick_type.upper()} PLAY #{play_number}. Use an energetic tone with confidence and emojis."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=350
    )

    return response['choices'][0]['message']['content'].strip()

# ------------------ POST FUNCTION ------------------
async def handle_pick(ctx, units, channel_name, pick_type):
    if not ctx.message.attachments:
        await ctx.send("❌ Please attach a bet slip image.")
        return

    try:
        attachment = ctx.message.attachments[0]
        image_bytes = await attachment.read()
        bet = extract_text(BytesIO(image_bytes))

        play_number = get_play_number(pick_type.upper()) + 1
        writeup = generate_gpt_writeup(bet, units, play_number, pick_type)

        # Post
        title = f"**{pick_type.upper()} PLAY #{play_number}**"
        post = f"{title}\n{writeup}\n\nChannel: {channel_name}"
        await ctx.send(post)

        # Log to Google Sheet
        log_pick(pick_type.upper(), bet["home_team"], bet["away_team"], units, bet["line"], bet["odds"])

    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

# ------------------ BOT COMMANDS ------------------
@bot.command()
async def postpick(ctx, units: float, channel_name: str):
    await handle_pick(ctx, units, channel_name, pick_type="VIP")

@bot.command()
async def freepick(ctx, units: float, channel_name: str):
    await handle_pick(ctx, units, channel_name, pick_type="Free")

# ------------------ RUN ------------------
bot.run(DISCORD_TOKEN)
