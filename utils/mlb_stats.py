import statsapi  # comes from the GitHub library

def get_game_stats(bet_info):
    """Fetch game or pitcher stats via the vendored statsapi."""
    # for example:
    game_id = statsapi.schedule(
        team=bet_info['team'], 
        date=bet_info['date_str']
    )[0]['game_id']
    boxscore = statsapi.boxscore_data(game_id)
    # …extract what you need, return as dict…
    return {
      'home_record': boxscore['home']['team_record'],
      'away_record': boxscore['away']['team_record'],
      # etc.
    }
