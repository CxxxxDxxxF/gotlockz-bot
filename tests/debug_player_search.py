#!/usr/bin/env python3
"""
Debug script to test player search functionality
"""
import asyncio
import logging

import aiohttp

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_player_search():
    """Test player search API."""
    url = "https://statsapi.mlb.com/api/v1/people/search?q=Mike%20Trout"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            logger.info(f"Status: {response.status}")
            text = await response.text()
            logger.info(f"Content: {text}")


if __name__ == "__main__":
    asyncio.run(test_player_search())
