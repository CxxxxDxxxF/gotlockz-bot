import re
from io import BytesIO
from PIL import Image
import pytesseract
import openai
import mlb_statsapi as mlb

TEAM_MAP = {
    "yankees":"New York Yankees","red sox":"Boston Red Sox",
    # truncated for brevity; include other teams as needed
}

def extract_text_from_image(b: bytes) -> str:
    img = Image.open(BytesIO(b))
    if img.mode not in ("RGB","L","RGBA"):
        img = img.convert("RGB")
    return pytesseract.image_to_string(img)

def parse_pick_text(txt: str):
    clean = txt.replace("\n"," ").lower()
    teams = [v for k,v in TEAM_MAP.items() if k in clean]
    desc = clean.strip()
    return desc, teams

async def generate_analysis_message(desc: str, teams: list, model: str):
    sys = "You are an MLB betting expert..."
    usr = f"Pick: {desc}"
    if teams:
        usr += f" Teams: {', '.join(teams)}"
    msgs=[{"role":"system","content":sys},{"role":"user","content":usr}]
    def call():
        r = openai.ChatCompletion.create(model=model,messages=msgs,temperature=0.7,max_tokens=250)
        return r.choices[0].message.content
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, call)
