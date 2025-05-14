import discord
from discord.ext import commands
import requests
import openai
import re
from io import BytesIO
from PIL import Image
from datetime import datetime
from utils.ocr import extract_text
from utils.sheets import init_sheets, log_pick, get_play_number
from utils.stats import get_game_time, get_probable_pitchers
from config import DISCORD_TOKEN, OPENAI_API_KEY, COMMAND_CHANNEL, VIP_CHANNEL_DEFAULT, FREE_CHANNEL_DEFAULT

def chunk_text(text, limit=2000):
    chunks = []
    while text:
        cut = text.rfind("\n", 0, limit)
        cut = cut if cut > 0 else limit
        chunks.append(text[:cut])
        text = text[cut:]
    return chunks

def generate_analysis(team, opp, tp, op, pick, odds):
    prompt = f"""
Write a hype‑driven, stat‑backed analysis:
– The {team} are facing {opp}'s starter {op} today with {tp} on the mound.
– Pick: {team} {pick} at {odds}
Include:
1) {tp}'s ERA, WHIP, K/9.
2) {op}'s weaknesses.
3) Team trends (home/away, vs RHP/LHP).
4) Close with: make us some money tonight 💰
"""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        timeout=15, max_tokens=650
    )
    return resp.choices[0].message.content.strip()

class BettingBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        intents.guilds = True
        intents.messages = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)
        self.sheet = init_sheets()

    async def on_ready(self):
        print(f"✅ Logged in as {self.user}")

bot = BettingBot()

@bot.command(name="postpick")
async def postpick(ctx, units: float = None, channel: str = None):
    if ctx.channel.name != COMMAND_CHANNEL:
        return await ctx.send(f"⛔ Please run this in #{COMMAND_CHANNEL} only.")
    if not ctx.message.attachments:
        return await ctx.send("❌ Attach your bet slip image.")

    res = requests.get(ctx.message.attachments[0].url)
    img = Image.open(BytesIO(res.content))
    lines = extract_text(img)
    text = "\n".join(lines)
    await ctx.send(f"📋 OCR text:\n```{text[:1900]}```")  # Debug

    team = opp = od = pick = None

    team_patterns = [
        r"([A-Za-z\s]{3,})\s*(?:vs\.?|\?|@|at)\s*([A-Za-z\s]{3,})",
        r"([A-Z][a-z]{2,4})\s*(vs\.?|@|at)\s*([A-Z][a-z]{2,4})"
    ]

    text = text.lower()
    for pattern in team_patterns:
        if match := re.search(pattern, text, re.I):
            team, opp = match.group(1).strip(), match.group(2).strip()
            break
    if not (team and opp):
        return await ctx.send("❌ Could not parse teams—please check image quality or try again.")

    # Parse odds
    if not od:
        for pattern in [r'([+-]\d+)', r'(\d+\s*[+-]\d+)', r'odds?\s*[:=]?\s*([+-]\d+)']:
            if match := re.search(pattern, text, re.I):
                od = match.group(1)
                break
        if not od:
            od = "N/A"

    # Parse pick
    pick_patterns = {
        r'\brun\s*line\b': "Run Line",
        r'\btotal\b': "Total",
        r'\bover\b|\bunder\b': "Over/Under",
        r'\bspread\b': "Spread"
    }
    pick = "Money Line"
    for pattern, pick_type in pick_patterns.items():
        if re.search(pattern, text, re.I):
            pick = pick_type
            break

    # Units and Channel
    unit_size = units or 1.0
    chan_name = channel.lstrip("#") if channel else (VIP_CHANNEL_DEFAULT if "vip" in text else FREE_CHANNEL_DEFAULT)
    cat = "VIP" if "vip" in chan_name.lower() else "Free"
    target = discord.utils.get(ctx.guild.text_channels, name=chan_name)
    if not target:
        return await ctx.send(f"❌ Channel `{chan_name}` not found.")

    # Stats & GPT
    date = datetime.now().strftime("%m/%d/%y")
    time_str = get_game_time(team, opp)
    tp, op = get_probable_pitchers(team, opp)
    analysis = generate_analysis(team, opp, tp, op, pick, od)
    num = get_play_number(bot.sheet, cat)
    emoji = "🔐" if cat == "VIP" else "💸"

    # Build message
    header = f"# {emoji} I {cat.upper()} PLAY # {num} - 🏆 - {date}"
    body = (
        f"⚾️ I Game: {team} @ {opp}  ({date} {time_str})\n\n"
        f"🏆 I {team} - {pick} ( {od} )\n\n"
        f"💵 I Unit Size: {unit_size}\n\n"
        f"👇 I Analysis Below:\n\n{analysis}"
    )
    full = f"**{header}**\n\n{body}\n\nmake us some money tonight 💰 **"

    file = discord.File(BytesIO(res.content), filename="pick.png")
    chunks = chunk_text(full)
    await target.send(content=chunks[0], file=file)
    for c in chunks[1:]:
        await target.send(content=c)

    log_pick(bot.sheet, {
        "team": team, "pick": pick, "odds": od,
        "category": cat, "units": unit_size,
        "team_pitcher": tp, "opp_pitcher": op,
        "date": date, "time": time_str,
        "analysis": analysis, "author": ctx.author.display_name
    })

    await ctx.send(f"✅ {cat} pick posted in **#{chan_name}** and logged.")

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise RuntimeError("❌ DISCORD_TOKEN not set in environment!")
    bot.run(DISCORD_TOKEN)
