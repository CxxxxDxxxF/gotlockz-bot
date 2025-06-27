#!/usr/bin/env python3
"""
Debug script to specifically test Oakland Athletics lookup
"""
import aiohttp
import asyncio

async def debug_oakland():
    url = 'https://statsapi.mlb.com/api/v1/teams?season=2024'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            teams = data.get('teams', [])
            
            # Find Oakland Athletics specifically
            oakland = None
            for team in teams:
                if team.get('sport', {}).get('id') == 1 and 'Oakland' in team.get('name', ''):
                    oakland = team
                    break
            
            if oakland:
                print(f"Found Oakland: ID {oakland.get('id')}, Name: '{oakland.get('name')}'")
                print(f"Sport: {oakland.get('sport')}")
                print(f"League: {oakland.get('league')}")
            else:
                print("Oakland Athletics not found!")
                
            # Show all teams with "Oakland" in the name
            oakland_teams = [t for t in teams if 'Oakland' in t.get('name', '')]
            print(f"\nAll teams with 'Oakland' in name: {len(oakland_teams)}")
            for team in oakland_teams:
                print(f"  {team.get('id')}: '{team.get('name')}' (sport: {team.get('sport', {}).get('id')})")

if __name__ == "__main__":
    asyncio.run(debug_oakland()) 