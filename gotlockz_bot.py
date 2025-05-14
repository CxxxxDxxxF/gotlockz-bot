import aiohttp
import tempfile
import re
import discord
from discord.ext import commands
from utils.ocr import extract_text
from utils.sheets import init_sheets, log_pick, get_play_number

# your CHANNEL_MAP up near the top of the file
CHANNEL_MAP = {
    "🔒vip-plays":  "vip-plays",
    "🏆free-plays": "free-plays",
}

@bot.command(name="postpick")
async def postpick(ctx, units: float, channel_key: str):
    """
    Usage in Discord:
       !postpick 6 🔒vip-plays
    (attach your bet slip image to the same message)
    """

    # 1) Ensure an image is attached
    if not ctx.message.attachments:
        return await ctx.send("✖ Please attach the bet‑slip image to your command message.")

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
    pattern = r"([A-Za-z .']+)\s+([+-]?\d+\.?\d*)\s+(?:Run Line|Money Line)\s+([+-]?\d+)"
    m = re.search(pattern, raw_text)
    if m:
        team, line, odds = m.groups()
        # try to capture “Team at Opponent”
        mm = re.search(r"([A-Za-z .']+)\s+at\s+([A-Za-z .']+)", raw_text)
        matchup = f" at {mm.group(2)}" if mm else ""
        pick = f"{team.strip()} {line} {odds}{matchup}"
    else:
        # fallback to raw OCR text
        pick = raw_text.strip().replace("\n", " ")

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

