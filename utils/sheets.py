import os
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger(__name__)

CREDENTIALS_FILE = "credentials.json"
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SHEET = None

def init_sheets():
    global SHEET
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
        client = gspread.authorize(creds)
        sheet_id = os.getenv("SHEET_ID")
        if not sheet_id:
            raise ValueError("SHEET_ID not set")
        SHEET = client.open_by_key(sheet_id).sheet1
        logger.info("Google Sheets initialized.")
        return SHEET
    except Exception:
        logger.exception("Error initializing Google Sheets")
        raise

def log_pick(entry: dict):
    if not SHEET:
        logger.error("Sheets not initialized; cannot log pick")
        return
    try:
        SHEET.append_row(list(entry.values()))
        logger.info(f"Logged entry: {entry}")
    except Exception:
        logger.exception("Failed to append row to Google Sheet")

def get_play_number(play_type: str) -> int:
    if not SHEET:
        logger.error("Sheets not initialized; returning default play number")
        return 1
    try:
        records = SHEET.get_all_records()
        return sum(1 for r in records if r.get("type") == play_type) + 1
    except Exception:
        logger.exception("Failed to retrieve records from Google Sheet")
        return 1
