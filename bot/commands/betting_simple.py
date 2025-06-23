#!/usr/bin/env python3
"""
betting_simple.py - Bulletproof Betting Commands

A simplified, reliable Discord bot command for posting betting picks
with minimal dependencies and maximum reliability.
"""

import logging
import discord
from discord import app_commands
from typing import Optional
from datetime import datetime
import os
import re
import asyncio
import json

# Import utilities
from utils.ocr import ocr_parser

logger = logging.getLogger(__name__)


class BettingCommands(app_commands.Group):
    """Simplified betting commands focused on reliability."""

    def __init__(self, bot):
        super().__init__(name="betting", description="Betting pick commands")
        self.bot = bot
        self.pick_counters = self._load_counters()

    def _load_counters(self):
        """Load pick counters from file."""
        try:
            counter_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'pick_counters.json')
            if os.path.exists(counter_file):
                with open(counter_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading counters: {e}")
        return {'vip': 0, 'free': 0, 'lotto': 0}

    def _save_counters(self):
        """Save pick counters to file."""
        try:
            counter_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'pick_counters.json')
            os.makedirs(os.path.dirname(counter_file), exist_ok=True)
            with open(counter_file, 'w') as f:
                json.dump(self.pick_counters, f)
        except Exception as e:
            logger.error(f"Error saving counters: {e}")

    @app_commands.command(name="postpick", description="Post a pick with custom units and channel")
    @app_commands.describe(
        unitsize="Number of units (optional - if 0, units won't be shown)",
        channel="Channel to post the pick in",
        image="Upload a betting slip image"
    )
    async def postpick_command(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        image: discord.Attachment,
        unitsize: int = 0
    ):
        """Post a pick with maximum reliability."""
        
        # Step 1: Immediately acknowledge Discord
        await interaction.response.defer(thinking=True)
        
        try:
            # Step 2: Quick validation
            if not image.content_type or not image.content_type.startswith('image/'):
                await interaction.followup.send("❌ Please provide a valid image file.", ephemeral=True)
                return

            # Step 3: Download image (with timeout)
            try:
                image_bytes = await asyncio.wait_for(image.read(), timeout=5.0)
                logger.info("Image downloaded successfully")
            except asyncio.TimeoutError:
                await interaction.followup.send("❌ Image download failed. Please try again.", ephemeral=True)
                return
            except Exception as e:
                logger.error(f"Image download error: {e}")
                await interaction.followup.send("❌ Failed to download image. Please try again.", ephemeral=True)
                return

            # Step 4: Extract text from image (with timeout)
            try:
                text = await asyncio.wait_for(
                    ocr_parser.extract_text_from_image(image_bytes), 
                    timeout=10.0
                )
                logger.info(f"OCR extracted text: {text[:100]}...")
            except asyncio.TimeoutError:
                await interaction.followup.send("❌ Image processing took too long. Please try with a clearer image.", ephemeral=True)
                return
            except Exception as e:
                logger.error(f"OCR error: {e}")
                await interaction.followup.send("❌ Failed to read image text. Please try with a clearer image.", ephemeral=True)
                return

            # Step 5: Parse bet data (simple parsing)
            bet_data = self._parse_bet_data_simple(text)
            logger.info(f"Parsed bet data: {bet_data}")

            # Step 6: Generate message (no external APIs)
            message_content = self._generate_simple_message(bet_data, unitsize, channel.id)
            
            # Step 7: Post message
            try:
                await channel.send(content=message_content)
                logger.info("Message posted successfully")
            except Exception as e:
                logger.error(f"Failed to post message: {e}")
                await interaction.followup.send("❌ Failed to post message. Please check channel permissions.", ephemeral=True)
                return

            # Step 8: Update counters
            channel_type = self._get_channel_type(channel.id)
            if channel_type:
                self.pick_counters[channel_type] += 1
                self._save_counters()

            # Step 9: Success confirmation
            await interaction.followup.send(f"✅ Pick posted successfully in {channel.mention}!", ephemeral=True)
            logger.info("Command completed successfully")

        except discord.errors.NotFound:
            logger.error("Interaction timed out")
            try:
                await interaction.followup.send("❌ Command timed out. Please try again.", ephemeral=True)
            except:
                pass
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            try:
                await interaction.followup.send("❌ An unexpected error occurred. Please try again.", ephemeral=True)
            except:
                pass

    def _parse_bet_data_simple(self, text: str) -> dict:
        """Simple bet data parsing without complex logic."""
        try:
            # Default data
            bet_data = {
                'teams': ['Unknown', 'Unknown'],
                'player': 'Unknown',
                'description': 'Unknown',
                'odds': 'Unknown',
                'units': '1',
                'sport': 'MLB'
            }

            # Extract teams (look for common patterns)
            team_patterns = [
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+@\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+vs\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
            ]

            for pattern in team_patterns:
                match = re.search(pattern, text)
                if match:
                    bet_data['teams'] = [match.group(1), match.group(2)]
                    break

            # Extract odds
            odds_match = re.search(r'([+-]\d+)', text)
            if odds_match:
                bet_data['odds'] = odds_match.group(1)

            # Extract player name (look for common patterns)
            player_patterns = [
                r'([A-Z][a-z]+\s+[A-z]+)\s+(?:to\s+)?(?:get|hit|score|record)',
                r'([A-Z][a-z]+\s+[A-z]+)\s+(?:over|under)',
                r'([A-Z][a-z]+\s+[A-z]+)\s+(?:money\s+line|ML)'
            ]

            for pattern in player_patterns:
                match = re.search(pattern, text)
                if match:
                    bet_data['player'] = match.group(1)
                    break

            # Extract description
            if 'over' in text.lower():
                bet_data['description'] = 'Over'
            elif 'under' in text.lower():
                bet_data['description'] = 'Under'
            elif 'money line' in text.lower() or 'ml' in text.lower():
                bet_data['description'] = 'Money Line'
            else:
                bet_data['description'] = 'Player Performance'

            return bet_data

        except Exception as e:
            logger.error(f"Error parsing bet data: {e}")
            return {
                'teams': ['Unknown', 'Unknown'],
                'player': 'Unknown',
                'description': 'Unknown',
                'odds': 'Unknown',
                'units': '1',
                'sport': 'MLB'
            }

    def _generate_simple_message(self, bet_data: dict, unitsize: int, channel_id: int) -> str:
        """Generate a simple, reliable message without external dependencies."""
        try:
            # Get current date/time
            current_date = datetime.now().strftime("%m/%d/%y")
            current_time = datetime.now().strftime("%I:%M %p")
            
            # Determine channel type
            channel_type = self._get_channel_type(channel_id)
            
            # Build header
            if channel_type == 'vip':
                header = f"**VIP PLAY – {current_date}**"
            elif channel_type == 'lotto':
                header = f"**LOTTO TICKET – {current_date}**"
            else:
                header = f"**FREE PLAY – {current_date}**"
            
            if unitsize > 0:
                header += f"  \n💰 **{unitsize} UNITS**"

            # Game info
            teams = bet_data.get('teams', ['Unknown', 'Unknown'])
            game_info = f"⚾ | Game: {teams[0]} @ {teams[1]} ({current_date} {current_time} EST)"

            # Bet details
            player = bet_data.get('player', 'Unknown')
            description = bet_data.get('description', 'Unknown')
            odds = bet_data.get('odds', 'Unknown')
            bet_details = f"🏆 | {player} – {description} ({odds})"

            # Analysis (simple)
            analysis = f"📊 | Analysis: {teams[0]} vs {teams[1]} - {description} bet on {player}"

            # Closing
            if channel_type == 'vip':
                closing = "🔒 VIP LOCK. 🔥"
            elif channel_type == 'lotto':
                closing = "🎰 HIT THE LOTTO! 🔥"
            else:
                closing = "LOCK IT. 🔒🔥"

            # Build complete message
            message_parts = [
                header,
                "",
                game_info,
                "",
                bet_details,
                "",
                "👇 | Analysis Below:",
                "",
                analysis,
                "",
                closing
            ]

            return "\n".join(message_parts)

        except Exception as e:
            logger.error(f"Error generating message: {e}")
            return f"**PICK POSTED**\n\nError generating detailed message. Basic info: {bet_data.get('teams', ['Unknown', 'Unknown'])}"

    def _get_channel_type(self, channel_id: int) -> Optional[str]:
        """Get channel type based on ID."""
        try:
            # Get channel IDs from bot config
            vip_id = getattr(self.bot, 'vip_channel_id', None)
            free_id = getattr(self.bot, 'free_channel_id', None)
            lotto_id = getattr(self.bot, 'lotto_channel_id', None)
            
            if vip_id and str(channel_id) == str(vip_id):
                return 'vip'
            elif free_id and str(channel_id) == str(free_id):
                return 'free'
            elif lotto_id and str(channel_id) == str(lotto_id):
                return 'lotto'
            else:
                return 'free'  # Default to free
        except Exception as e:
            logger.error(f"Error getting channel type: {e}")
            return 'free'


async def setup(bot):
    """Set up the betting commands."""
    await bot.add_cog(BettingCommands(bot)) 