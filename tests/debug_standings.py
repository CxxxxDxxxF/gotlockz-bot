#!/usr/bin/env python3
"""
Debug script to test MLB standings endpoint
"""
import asyncio
import aiohttp
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_standings():
    """Test the standings endpoint directly"""
    print("=== Testing MLB Standings Endpoint ===")
    
    try:
        async with aiohttp.ClientSession() as session:
            current_year = datetime.now().year
            
            # Test current year standings
            url = "https://statsapi.mlb.com/api/v1/standings"
            params = {
                'leagueId': '103,104',  # AL and NL
                'season': current_year,
                'standingsTypes': 'regularSeason',
                'fields': 'records,team,id,name,wins,losses,runDifferential,divisionRank,leagueRank,divisionGamesBack,leagueGamesBack,elimNumber,clinched,divisionRecord,leagueRecord,home,away'
            }
            
            print(f"Testing current year ({current_year}) standings...")
            async with session.get(url, params=params) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"Records found: {len(data.get('records', []))}")
                    
                    # Look for specific teams
                    for record in data.get('records', []):
                        print(f"Division: {record.get('division', {}).get('name', 'Unknown')}")
                        for teamrec in record.get('teamRecords', []):
                            team = teamrec.get('team', {})
                            name = team.get('name', 'Unknown')
                            if 'Angels' in name or 'Athletics' in name:
                                print(f"  {name}: {teamrec.get('wins', 0)}-{teamrec.get('losses', 0)}")
                else:
                    print(f"Error: {response.status}")
            
            # Test previous year standings
            print(f"\nTesting previous year ({current_year - 1}) standings...")
            params['season'] = current_year - 1
            async with session.get(url, params=params) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"Records found: {len(data.get('records', []))}")
                    
                    # Look for specific teams
                    for record in data.get('records', []):
                        print(f"Division: {record.get('division', {}).get('name', 'Unknown')}")
                        for teamrec in record.get('teamRecords', []):
                            team = teamrec.get('team', {})
                            name = team.get('name', 'Unknown')
                            if 'Angels' in name or 'Athletics' in name:
                                print(f"  {name}: {teamrec.get('wins', 0)}-{teamrec.get('losses', 0)}")
                else:
                    print(f"Error: {response.status}")
                    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

async def test_team_stats():
    """Test the team stats endpoint directly"""
    print("\n=== Testing MLB Team Stats Endpoint ===")
    
    try:
        async with aiohttp.ClientSession() as session:
            current_year = datetime.now().year
            
            # Test Angels team stats (ID: 108)
            team_id = 108  # Angels
            url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/stats"
            params = {
                'season': current_year,
                'group': 'hitting',
                'stats': 'season'
            }
            
            print(f"Testing Angels ({team_id}) current year ({current_year}) stats...")
            async with session.get(url, params=params) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    stats = data.get('stats', [])
                    print(f"Stats found: {len(stats)}")
                    
                    if stats:
                        stat = stats[0]
                        splits = stat.get('splits', [])
                        print(f"Splits found: {len(splits)}")
                        
                        if splits:
                            split = splits[0]
                            stat_data = split.get('stat', {})
                            print(f"Games played: {stat_data.get('gamesPlayed', 0)}")
                            print(f"Wins: {stat_data.get('wins', 0)}")
                            print(f"Losses: {stat_data.get('losses', 0)}")
                else:
                    print(f"Error: {response.status}")
            
            # Test previous year
            print(f"\nTesting Angels previous year ({current_year - 1}) stats...")
            params['season'] = current_year - 1
            async with session.get(url, params=params) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    stats = data.get('stats', [])
                    print(f"Stats found: {len(stats)}")
                    
                    if stats:
                        stat = stats[0]
                        splits = stat.get('splits', [])
                        print(f"Splits found: {len(splits)}")
                        
                        if splits:
                            split = splits[0]
                            stat_data = split.get('stat', {})
                            print(f"Games played: {stat_data.get('gamesPlayed', 0)}")
                            print(f"Wins: {stat_data.get('wins', 0)}")
                            print(f"Losses: {stat_data.get('losses', 0)}")
                else:
                    print(f"Error: {response.status}")
                    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all tests"""
    await test_standings()
    await test_team_stats()

if __name__ == "__main__":
    asyncio.run(main()) 