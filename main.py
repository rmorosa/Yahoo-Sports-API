# main.py
import os
from dotenv import load_dotenv
from auth import build_auth_url, exchange_code_for_tokens, refresh_access_token
from fantasy import (
    get_user_games,
    get_mlb_2025_game_key,
    get_league,
    get_teams,
    # get_team_stats_week,
    get_team_stats,
    extract_innings_pitched
)

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

def ensure_token():
    global ACCESS_TOKEN, REFRESH_TOKEN

    if ACCESS_TOKEN:
        return ACCESS_TOKEN

    print("No access token found! Visit this URL to authorize your app:\n")
    print(build_auth_url())
    code = input("\nPaste the code from Yahoo here: ").strip()

    tokens = exchange_code_for_tokens(code)
    ACCESS_TOKEN = tokens["access_token"]
    REFRESH_TOKEN = tokens["refresh_token"]
    return ACCESS_TOKEN


def main():
    ensure_token()

    # # 1️⃣ List your games
    games = get_user_games()
    print("\n=== Your Games ===")
    # print(games)

    # 2️⃣ Pick your league (example)
    # You can extract league_key automatically:
    # game_key = (
    #     games["fantasy_content"]["users"]["0"]["user"][1]["games"]["0"]["game"][0]["game_key"]
    # )
    # print("\nUsing League:", league_key)

    # Extract mlb_2025_key
    mlb_2025_key = get_mlb_2025_game_key(games)
    print(mlb_2025_key)

    # https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games;game_keys=<game_key>/leagues
    league_key = get_league(mlb_2025_key)
    print(league_key)

    # 3️⃣ Get teams in league
    teams_json = get_teams(league_key)
    # print(teams_json)
    teams = teams_json["fantasy_content"]["league"][1]["teams"]
    # print(teams)

    # print("\n=== Team Innings Pitched for Week 1 ===")
    for _, team in teams.items():
        if not isinstance(team, dict):
            continue

        meta = team["team"][0]
        # Find the first dict in meta that contains "team_key" "team_name" and return its value.
        team_key = next(item["team_key"] for item in meta if "team_key" in item)
        team_name = next(item["name"] for item in meta if "name" in item)

        # stats_json = get_team_stats_week(team_key, week_number=1)
        stats_json = get_team_stats(team_key)
        # print(stats_json)
        ip = extract_innings_pitched(stats_json)

        print(f"{team_name}: {ip} IP")


if __name__ == "__main__":
    main()
