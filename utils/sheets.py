# utils/sheets.py

import os
import json
import base64
import logging

import gspread
from oauth2client.service_account import ServiceAccountCredentials

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
        mode = "wb" if isinstance(raw, (bytes, bytearray)) else "w"
        with open(CREDENTIALS_FILE, mode) as f:
            f.write(raw)
        logging.info(f"Wrote {len(raw)} bytes to {CREDENTIALS_FILE} from env")
    else:
        logging.error("No GOOGLE_SHEETS_CREDS or _B64 env var set — credentials.json is empty")

# ——— debug dump of the first few bytes ———
try:
    size = os.path.getsize(CREDENTIALS_FILE)
    with open(CREDENTIALS_FILE, "r") as f:
        snippet = f.read(80).replace("\n", " ")
    logging.info(f"[DEBUG] {CREDENTIALS_FILE} size={size}, starts with: {snippet!r}")
except Exception as e:
    logging.error(f"Failed to inspect {CREDENTIALS_FILE}: {e}", exc_info=True)


def init_sheets():
    """
    Authorize with the service account JSON and return
    a gspread.Spreadsheet object opened by SHEET_ID env var.
    """
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
    client = gspread.authorize(creds)
    sheet_id = os.environ.get("SHEET_ID")
    if not sheet_id:
        raise RuntimeError("Environment variable SHEET_ID is not set")
    return client.open_by_key(sheet_id)


def get_play_number() -> int:
    """
    Returns the next play number by counting existing rows.
    Always returns at least 1.
    """
    sheet = init_sheets().sheet1
    values = sheet.get_all_values()
    # next row index = existing rows + 1
    return len(values) + 1


def log_pick(play_number: int, pick: str) -> None:
    """
    Appends a new row [play_number, pick] to the bottom of the sheet.
    """
    sheet = init_sheets().sheet1
    sheet.append_row([play_number, pick])
    logging.info(f"Logged pick #{play_number}: {pick!r}")

