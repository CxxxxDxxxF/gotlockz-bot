import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

VIP_SHEET = client.open("GotLockz Picks").worksheet("VIP")
FREE_SHEET = client.open("GotLockz Picks").worksheet("Free")

def log_pick(pick_type, home_team, away_team, units, line, odds):
    row = [home_team, away_team, units, line, odds]
    if pick_type == "VIP":
        VIP_SHEET.append_row(row)
    else:
        FREE_SHEET.append_row(row)

def get_play_number(pick_type):
    sheet = VIP_SHEET if pick_type=="VIP" else FREE_SHEET
    return len(sheet.get_all_values())
