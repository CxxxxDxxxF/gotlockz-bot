
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import SHEET_NAME

def init_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    gs = gspread.authorize(creds)
    return gs.open(SHEET_NAME).sheet1

def log_pick(sheet, pick_data):
    sheet.append_row([
        datetime.now().isoformat(),
        pick_data["team"], pick_data["pick"], pick_data["odds"],
        pick_data["category"], pick_data["units"],
        pick_data["team_pitcher"], pick_data["opp_pitcher"],
        pick_data["date"], pick_data["time"],
        pick_data["analysis"], pick_data["author"]
    ])

def get_play_number(sheet, category):
    rows = sheet.get_all_values()[1:]
    return sum(1 for r in rows if r[4].lower() == category.lower()) + 1
