#!/usr/bin/env python3
"""
Debug script to test exact string comparison for Oakland Athletics
"""
import asyncio

import aiohttp


async def debug_string_comparison():
    url = "https://statsapi.mlb.com/api/v1/teams?season=2024"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            teams = data.get("teams", [])

            # Find Oakland Athletics
            oakland = None
            for team in teams:
                if team.get("sport", {}).get("id") == 1 and team.get("id") == 133:
                    oakland = team
                    break

            if oakland:
                api_name = oakland.get("name")
                search_name = "Oakland Athletics"

                print(f"API name: '{api_name}' (length: {len(api_name)})")
                print(f"Search name: '{search_name}' (length: {len(search_name)})")
                print(
                    f"Lowercase comparison: '{api_name.lower()}' == '{search_name.lower()}' = {api_name.lower() == search_name.lower()}"
                )

                # Check each character
                print("\nCharacter by character comparison:")
                for i, (api_char, search_char) in enumerate(zip(api_name, search_name)):
                    if api_char != search_char:
                        print(
                            f"  Position {i}: API='{api_char}' (ord: {ord(api_char)}) vs Search='{search_char}' (ord: {ord(search_char)})"
                        )

                # Test the exact condition from the service
                condition = (
                    oakland.get("sport", {}).get("id") == 1 and oakland.get("name", "").lower() == search_name.lower()
                )
                print(f"\nExact condition result: {condition}")

            else:
                print("Oakland Athletics not found!")


if __name__ == "__main__":
    asyncio.run(debug_string_comparison())
