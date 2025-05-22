from datetime import datetime

def format_message(bet_info, analysis, units):
    today = datetime.now().strftime("%m/%d/%y")
    game = bet_info['game']
    start_time = bet_info.get('start_time', 'Unknown')

    pick_lines = "\n".join([
        f"🏆 I {p['description']} ({p['odds']})" for p in bet_info['picks']
    ])

    message = (
        f"🔒 I VIP PLAY # X - 🏆 - {today},\n"
        f"⚾️ I Game: {game} ({start_time})\n\n"
        f"{pick_lines}\n\n"
        f"💵 I Unit Size: {units}\n\n"
        f"👇 I Analysis Below:\n\n"
        f"{analysis}"
    )
    return message

