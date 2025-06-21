import discord
from discord.ext import commands
import os
import requests
import json
from datetime import datetime

class GotLockzBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix="!", intents=discord.Intents.all(), **kwargs)
        self.dashboard_url = os.getenv("DASHBOARD_URL", "http://localhost:8080")

    async def on_ready(self):
        print(f"Bot connected as {self.user}")
        print(f"Dashboard URL: {self.dashboard_url}")
        
        # Sync slash commands with Discord
        print("🔄 Syncing slash commands...")
        try:
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"❌ Command sync failed: {e}")
        
        # Test dashboard connection
        try:
            response = requests.get(f"{self.dashboard_url}/api/ping", timeout=5)
            if response.status_code == 200:
                print("✅ Dashboard connection successful")
            else:
                print("⚠️ Dashboard connection failed")
        except Exception as e:
            print(f"❌ Dashboard connection error: {e}")

    async def setup_hook(self):
        # Register slash commands
        @self.tree.command(name="ping", description="Test bot responsiveness")
        async def slash_ping(interaction: discord.Interaction):
            await interaction.response.send_message("🏓 Pong! Bot is online!")
        
        @self.tree.command(name="sync", description="Sync picks from Discord to dashboard")
        async def slash_sync(interaction: discord.Interaction):
            await interaction.response.defer()
            try:
                # Example: Send some test picks to dashboard
                test_picks = [
                    {
                        "pick_number": 1,
                        "pick_type": "vip",
                        "bet_details": "Lakers -5.5 vs Warriors",
                        "odds": "-110",
                        "analysis": "Strong home court advantage",
                        "posted_at": datetime.now().isoformat(),
                        "confidence_score": 8,
                        "edge_percentage": 5.2,
                        "result": "win",
                        "profit_loss": 50.0
                    }
                ]
                
                response = requests.post(
                    f"{self.dashboard_url}/api/sync-discord",
                    json=test_picks,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    await interaction.followup.send("✅ Picks synced to dashboard successfully!")
                else:
                    await interaction.followup.send(f"❌ Sync failed: {response.text}")
                    
            except Exception as e:
                await interaction.followup.send(f"❌ Sync error: {str(e)}")
        
        @self.tree.command(name="status", description="Check bot and dashboard status")
        async def slash_status(interaction: discord.Interaction):
            await interaction.response.defer()
            try:
                response = requests.get(f"{self.dashboard_url}/api/bot-status", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    status = "🟢 Online" if data.get('bot_running') else "🔴 Offline"
                    await interaction.followup.send(f"Bot Status: {status}")
                else:
                    await interaction.followup.send("❌ Dashboard not responding")
            except Exception as e:
                await interaction.followup.send(f"❌ Status check failed: {str(e)}")
        
        @self.tree.command(name="addpick", description="Add a new pick to the dashboard")
        async def slash_addpick(interaction: discord.Interaction, pick_type: str, pick_number: int, bet_details: str):
            await interaction.response.defer()
            try:
                pick_data = {
                    "pick_type": pick_type.lower(),
                    "pick_number": pick_number,
                    "bet_details": bet_details,
                    "odds": "-110",  # Default odds
                    "analysis": f"Added via Discord by {interaction.user.name}",
                    "confidence_score": 7,
                    "edge_percentage": 3.0
                }
                
                response = requests.post(
                    f"{self.dashboard_url}/api/picks/add",
                    json=pick_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    await interaction.followup.send(f"✅ Pick #{pick_number} added successfully!")
                else:
                    await interaction.followup.send(f"❌ Failed to add pick: {response.text}")
                    
            except Exception as e:
                await interaction.followup.send(f"❌ Error adding pick: {str(e)}")
        
        @self.tree.command(name="force_sync", description="Force sync all commands")
        async def slash_force_sync(interaction: discord.Interaction):
            await interaction.response.defer()
            try:
                # Sync commands globally
                synced = await self.tree.sync()
                await interaction.followup.send(f"✅ Force synced {len(synced)} command(s)! Commands may take up to 1 hour to update globally.")
            except Exception as e:
                await interaction.followup.send(f"❌ Force sync failed: {str(e)}")

        # Also keep the old prefix commands for compatibility
        @self.command()
        async def ping(ctx):
            """Test bot responsiveness"""
            await ctx.send("🏓 Pong! Bot is online!")
        
        @self.command()
        async def sync(ctx):
            """Sync picks from Discord to dashboard"""
            try:
                # Example: Send some test picks to dashboard
                test_picks = [
                    {
                        "pick_number": 1,
                        "pick_type": "vip",
                        "bet_details": "Lakers -5.5 vs Warriors",
                        "odds": "-110",
                        "analysis": "Strong home court advantage",
                        "posted_at": datetime.now().isoformat(),
                        "confidence_score": 8,
                        "edge_percentage": 5.2,
                        "result": "win",
                        "profit_loss": 50.0
                    }
                ]
                
                response = requests.post(
                    f"{self.dashboard_url}/api/sync-discord",
                    json=test_picks,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    await ctx.send("✅ Picks synced to dashboard successfully!")
                else:
                    await ctx.send(f"❌ Sync failed: {response.text}")
                    
            except Exception as e:
                await ctx.send(f"❌ Sync error: {str(e)}")
        
        @self.command()
        async def status(ctx):
            """Check bot and dashboard status"""
            try:
                response = requests.get(f"{self.dashboard_url}/api/bot-status", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    status = "🟢 Online" if data.get('bot_running') else "🔴 Offline"
                    await ctx.send(f"Bot Status: {status}")
                else:
                    await ctx.send("❌ Dashboard not responding")
            except Exception as e:
                await ctx.send(f"❌ Status check failed: {str(e)}")
        
        @self.command()
        async def addpick(ctx, pick_type: str, pick_number: int, *, bet_details: str):
            """Add a new pick to the dashboard"""
            try:
                pick_data = {
                    "pick_type": pick_type.lower(),
                    "pick_number": pick_number,
                    "bet_details": bet_details,
                    "odds": "-110",  # Default odds
                    "analysis": f"Added via Discord by {ctx.author.name}",
                    "confidence_score": 7,
                    "edge_percentage": 3.0
                }
                
                response = requests.post(
                    f"{self.dashboard_url}/api/picks/add",
                    json=pick_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    await ctx.send(f"✅ Pick #{pick_number} added successfully!")
                else:
                    await ctx.send(f"❌ Failed to add pick: {response.text}")
                    
            except Exception as e:
                await ctx.send(f"❌ Error adding pick: {str(e)}")

    async def on_message(self, message):
        # Don't respond to bot's own messages
        if message.author == self.user:
            return
        
        # Process commands
        await self.process_commands(message)
        
        # Auto-sync picks if message contains pick information
        if any(keyword in message.content.lower() for keyword in ['pick', 'bet', 'lock']):
            # You can add logic here to automatically parse and sync picks
            pass
