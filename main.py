# main.py
import os
import pandas as pd
from dotenv import load_dotenv
import requests
from auth import build_auth_url, exchange_code_for_tokens, refresh_access_token
from fantasy import (
    get_user_games,
    get_mlb_2025_game_key,
    get_league,
    get_teams,
    get_settings,
    get_stat_lookup,
    get_team_stats,
    map_stats,
    get_transactions,
    extract_team_info
)

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

def test_access_token():
    """Return True if ACCESS_TOKEN works, False if expired."""
    global ACCESS_TOKEN

    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    url = "https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1?format=json"
    r = requests.get(url, headers=headers)

    if r.status_code == 401:
        return False
    return True

def ensure_token():
    global ACCESS_TOKEN, REFRESH_TOKEN

    # 1️⃣ If access token exists, test if it works
    if ACCESS_TOKEN:
        if test_access_token():
            # Valid token
            return ACCESS_TOKEN
        else:
            print("Access token expired — refreshing...")
            tokens = refresh_access_token(REFRESH_TOKEN)
            ACCESS_TOKEN = tokens["access_token"]
            REFRESH_TOKEN = tokens["refresh_token"]
            return ACCESS_TOKEN

    # 2️⃣ If no access token → do the full OAuth flow
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
    # print("\n=== Your Games ===")
    # print(games)

    # 2️⃣ Pick your league (example)
    # You can extract league_key automatically:
    # game_key = (
    #     games["fantasy_content"]["users"]["0"]["user"][1]["games"]["0"]["game"][0]["game_key"]
    # )
    # print("\nUsing League:", league_key)

    # Extract mlb_2025_key
    mlb_2025_key = get_mlb_2025_game_key(games)
    # print(mlb_2025_key)

    # https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games;game_keys=<game_key>/leagues
    league_key = get_league(mlb_2025_key)
    # print(league_key)

    # 3️⃣ Get teams in league
    settings_json = get_settings(league_key)
    # print(settings_json)

    stat_lookup = get_stat_lookup(settings_json)
    # print(stat_lookup)

    # print(stat_lookup)
    # print(stats)

    teams_json = get_teams(league_key)

    teams = teams_json["fantasy_content"]["league"][1]["teams"]
    # print(teams)

    table = []
    # transactions_list = []

    # print("\n=== Team Innings Pitched for Week 1 ===")
    for _, team in teams.items():
        if not isinstance(team, dict):
            continue

        meta = team["team"][0]
        # Find the first dict in meta that contains "team_key" "team_name" and return its value.
        team_key = next(item["team_key"] for item in meta if "team_key" in item)
        team_name = next(item["name"] for item in meta if "name" in item)
        # print(team_name)

        # print(meta)

        stats_json = get_team_stats(team_key)
        print(stats_json)

        team_data = get_transactions(team_key)
        # print(team_data)

        transactions = extract_team_info(team_data, ["number_of_moves", "clinched_playoffs", "draft_position"])
        # print(transactions)

        stats = map_stats(stats_json, stat_lookup)

        row = {"team": team_name}

        for s in stats:
            row[s["stat_name"]] = s["value"]

        row["Transactions"] = transactions["number_of_moves"]
        row["Draft Position"] = transactions["draft_position"]

        if "clinched_playoffs" in transactions:
            row["Clinched Playoffs"] = "Yes"
        else:
            row["Clinched Playoffs"] = "No"


        table.append(row)

    df = pd.DataFrame(table)
    print(df)

    df.to_csv("2025_Yahoo_FB_stats.csv")


        

    # return mapped

        # print(stats_json)
        # ip = extract_team_stats(stat_lookup)

        # print(f"{team_name}: {ip} IP")


if __name__ == "__main__":
    main()
