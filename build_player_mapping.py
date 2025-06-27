#!/usr/bin/env python3
"""
Build a mapping of all active MLB player names to their MLB person IDs.
"""
import aiohttp
import asyncio
import json

MLB_TEAM_IDS = [
    108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 158
]

async def fetch_roster(session, team_id):
    url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster"
    async with session.get(url) as response:
        data = await response.json()
        return data.get('roster', [])

async def build_player_mapping():
    player_map = {}
    async with aiohttp.ClientSession() as session:
        for team_id in MLB_TEAM_IDS:
            roster = await fetch_roster(session, team_id)
            for player in roster:
                person = player.get('person', {})
                name = person.get('fullName')
                player_id = person.get('id')
                if name and player_id:
                    player_map[name] = player_id
    # Save to file
    with open('mlb_player_map.json', 'w') as f:
        json.dump(player_map, f, indent=2)
    print(f"Saved {len(player_map)} players to mlb_player_map.json")

if __name__ == "__main__":
    asyncio.run(build_player_mapping()) 