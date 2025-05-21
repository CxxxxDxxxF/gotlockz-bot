import json
import os
import asyncio

os.makedirs("data", exist_ok=True)
_FILE = os.path.join("data", "picks.json")
_LOCK = asyncio.Lock()

async def add_pick(rec: dict):
    async with _LOCK:
        try:
            with open(_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = []
        data.append(rec)
        with open(_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

async def get_all_picks():
    async with _LOCK:
        try:
            with open(_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
