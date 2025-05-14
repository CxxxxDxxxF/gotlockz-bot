import re
import time
import discord
import requests
import openai
from io import BytesIO
from PIL import Image
from datetime import datetime
from discord.ext import commands

from config import *
from utils.ocr import extract_text
from utils.sheets import init_sheets, log_pick, get_play_number
from utils.stats import get_game_time, get_probable_pitchers

def fetch_with_retries(url, attempts=3, timeout=5):
    for _ in range(attempts):
        try:
            return requests.get(url, timeout=timeout)
        except:
            time.sleep(1)
    raise RuntimeError(f"Failed to fetch {url}")

def chunk_text(text, limit=2000):
    chunks = []
    while text:
        cut = text.rfind("\n", 0, limit)
        cut = cut if cut>0 else limit
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
        messages=[{"role":"user","content":prompt}],
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

    @commands.command(name="postpick")
    async def postpick(self, ctx, units: float=None, channel: str=None, *, manual: str=None):
        if ctx.channel.name != COMMAND_CHANNEL:
            return await ctx.send(f"⛔ Please run this in #{COMMAND_CHANNEL} only.")
        if not ctx.message.attachments:
            return await ctx.send("❌ Attach your bet slip image.")

        # Process image and extract text
        res = fetch_with_retries(ctx.message.attachments[0].url)
        img = Image.open(BytesIO(res.content))
        lines = extract_text(img)
        text = "\n".join(lines)

        # Parse bet information
        team = opp = od = pick = None
        if manual:
            for part in manual.split(";"):
                k, v = part.split("=", 1)
                k, v = k.strip().lower(), v.strip()
                if k == "team": team = v
                if k == "opponent": opp = v
                if k == "odds": od = v
                if k in ("type", "pick"): pick = v
            await ctx.send("⚠️ Manual override applied.")

        # Parse odds and pick type
        if not od:
            for pattern in [r'([+-]\d+)', r'(\d+\s*[+-]\d+)', r'odds?\s*[:=]?\s*([+-]\d+)']:
                if match := re.search(pattern, text, re.I):
                    od = match.group(1)
                    break
            if not od: od = "N/A"

        if not pick:
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

        # Parse teams
        if not (team and opp):
            team_patterns = [
                r'(\w+[\w\s]+?)\s+(?:vs\.?|@|at)\s+(\w+[\w\s]+)',
                r'(\w+[\w\s]+?)\s*[-@]\s*(\w+[\w\s]+)',
                r'(\w+[\w\s]+?)\s+and\s+(\w+[\w\s]+)'
            ]
            for pattern in team_patterns:
                for line in lines:
                    if match := re.search(pattern, line, re.I):
                        team, opp = match.group(1).strip(), match.group(2).strip()
                        team = re.sub(r'\s+', ' ', team)
                        opp = re.sub(r'\s+', ' ', opp)
                        break
                if team and opp: break

        if not (team and opp):
            return await ctx.send("❌ Could not parse teams—please check image quality or try again.")

        # Get units and channel
        if units is None:
            m = re.search(r'\$(\d+(\.\d+)?)', text)
            unit_size = float(m.group(1)) if m else 0
        else:
            unit_size = units

        if channel:
            chan_name = channel.lstrip("#")
            cat = "VIP" if "vip" in chan_name.lower() else "Free"
        else:
            cat = "VIP" if "vip" in text.lower() else "Free"
            chan_name = VIP_CHANNEL_DEFAULT if cat=="VIP" else FREE_CHANNEL_DEFAULT

        target = discord.utils.get(ctx.guild.text_channels, name=chan_name)
        if not target:
            return await ctx.send(f"❌ Channel `{chan_name}` not found.")

        # Generate pick details
        date = datetime.now().strftime("%m/%d/%y")
        time_str = get_game_time(team, opp)
        tp, op = get_probable_pitchers(team, opp)
        analysis = generate_analysis(team, opp, tp, op, pick, od)
        num = get_play_number(self.sheet, cat)
        emoji = "🔒" if cat=="VIP" else "💸"

        # Format message
        header = f"# {emoji} I {cat.upper()} PLAY # {num} - 🏆 - {date}"
        body = (
            f"⚾️ I Game: {team} @ {opp}  ({date} {time_str})\n\n"
            f"🏆 I {team} - {pick} ( {od} )\n\n"
            f"💵 I Unit Size: {unit_size}\n\n"
            f"👇 I Analysis Below:\n\n{analysis}"
        )
        full = f"**{header}**\n\n{body}\n\nmake us some money tonight 💰 **"

        # Send message and log pick
        file = discord.File(BytesIO(res.content), filename="pick.png")
        chunks = chunk_text(full)
        await target.send(content=chunks[0], file=file)
        for c in chunks[1:]:
            await target.send(content=c)

        log_pick(self.sheet, {
            "team": team, "pick": pick, "odds": od,
            "category": cat, "units": unit_size,
            "team_pitcher": tp, "opp_pitcher": op,
            "date": date, "time": time_str,
            "analysis": analysis, "author": ctx.author.display_name
        })

        await ctx.send(f"✅ {cat} pick posted in **#{chan_name}** and logged.")

bot = BettingBot()

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise RuntimeError("❌ DISCORD_TOKEN not set in environment!")
    bot.run(DISCORD_TOKEN)