import os

if not os.path.exists("credentials.json") and os.getenv("GOOGLE_SHEETS_CREDS"):
    with open("credentials.json", "w") as f:
        f.write(os.environ["GOOGLE_SHEETS_CREDS"])

from gotlockz_bot import bot, TOKEN

if __name__ == "__main__":
    bot.run(TOKEN)
