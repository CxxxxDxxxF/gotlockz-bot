import os
import json
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from utils.ocr_parser import extract_bet_info
from utils.mlb_stats import get_game_stats
from utils.gpt_analysis import generate_analysis

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Counter file for play numbers
COUNTER_FILE = 'play_counter.json'

def load_counter():
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'r') as f:
            return json.load(f)
    else:
        return {'VIP': 0, 'FREE': 0}

def save_counter(counter):
    with open(COUNTER_FILE, 'w') as f:
        json.dump(counter, f)

def format_message(bet_info, analysis, units, play_type, play_number):
    date = bet_info.get('date_str', '')
    time = bet_info.get('time_str', '')
    away = bet_info.get('away', '')
    home = bet_info.get('home', '')
    team = bet_info.get('team', '')
    wager = bet_info.get('wager', '')
    odds = bet_info.get('odds', '')

    if play_type == 'VIP':
        header = f"🔒 **I VIP PLAY # {play_number} 🏆 — {date}**"
    else:
        header = f"**FREE PLAY {date}**"

    game_line = f"⚾️ | Game: {away} @ {home} ({date} {time})"
    bet_line = f"🏆 | {team} – {wager} ({odds})"
    unit_line = f"💵 | Unit Size: {units}" if play_type == 'VIP' else ""
    analysis_header = "👇 | Analysis Below:"

    parts = [header, game_line, bet_line]
    if unit_line:
        parts.append(unit_line)
    parts.extend([analysis_header, analysis])
    return "\n\n".join(parts)

# Discord bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)
tree = app_commands.CommandTree(bot)

@tree.command(name="postpick", description="Post an MLB betting pick")
@app_commands.describe(units="Units risked", channel="Target channel", slip="Bet slip image")
async def postpick(interaction: discord.Interaction, units: float, channel: discord.TextChannel, slip: discord.Attachment):
    await interaction.response.defer()
    temp_file = f"temp_{interaction.id}.jpg"
    # Save the attached slip image
    await slip.save(temp_file)

    counter = load_counter()
    play_type = 'VIP' if 'vip' in channel.name.lower() else 'FREE'
    counter[play_type] += 1
    play_number = counter[play_type]
    save_counter(counter)

    try:
        # Pipeline
        bet_info = extract_bet_info(temp_file)
        game_stats = get_game_stats(bet_info)
        analysis = generate_analysis(bet_info, game_stats)

        # Format and send
        message_text = format_message(bet_info, analysis, units, play_type, play_number)
        file = discord.File(temp_file)
        await channel.send(content=message_text, file=file)
        await interaction.followup.send("✅ Pick posted!", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {e}", ephemeral=True)
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Bot connected as {bot.user}")

if __name__ == "__main__":
    bot.run(TOKEN)
