# utils/sheets.py
import os
import json
import base64
import logging
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# where we'll write/read the service‑account JSON
CREDENTIALS_FILE = "credentials.json"
# Google Sheets scopes
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# ——— inject from env if missing or empty ———
if not os.path.exists(CREDENTIALS_FILE) or os.path.getsize(CREDENTIALS_FILE) == 0:
    raw = None
    if os.getenv("GOOGLE_SHEETS_CREDS"):
        raw = os.environ["GOOGLE_SHEETS_CREDS"]
    elif os.getenv("GOOGLE_SHEETS_CREDS_B64"):
        raw = base64.b64decode(os.environ["GOOGLE_SHEETS_CREDS_B64"])
    if raw:
        mode = "wb" if isinstance(raw, bytes) else "w"
        with open(CREDENTIALS_FILE, mode) as f:
            f.write(raw)
        logging.info(f"Wrote {len(raw)} bytes to {CREDENTIALS_FILE} from env")
    else:
        logging.error("No GOOGLE_SHEETS_CREDS or _B64 env var set — credentials.json is empty")

# ——— debug output ———
try:
    size = os.path.getsize(CREDENTIALS_FILE)
    with open(CREDENTIALS_FILE, "r") as f:
        snippet = f.read(80).replace("\n", " ")
    logging.info(f"[DEBUG] {CREDENTIALS_FILE} size={size}, starts with: {snippet!r}")
except Exception as e:
    logging.error(f"Failed to inspect {CREDENTIALS_FILE}: {e}")

def init_sheets():
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
        client = gspread.authorize(creds)
        # replace os.getenv("SHEET_ID") with however you're passing your sheet ID
        sheet = client.open_by_key(os.environ["SHEET_ID"])
        logging.info("Google Sheets initialized.")
        return sheet
    except Exception as e:
        logging.error("Error initializing Google Sheets", exc_info=e)
        raise
