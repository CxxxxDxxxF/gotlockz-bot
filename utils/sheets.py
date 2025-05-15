import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets config
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_JSON", "credentials.json")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

gc = None
sheet = None

def init_sheets():
    """
    Authenticate with Google Sheets and initialize the sheet.
    """
    global gc, sheet
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(SPREADSHEET_ID).sheet1

def get_play_number() -> int:
    """
    Return the next play number by counting existing rows.
    """
    values = sheet.get_all_values()
    return len(values)

def log_pick(pick: str):
    """
    Append the pick to the sheet.
    """
    sheet.append_row([pick])
