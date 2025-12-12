# fantasy.py
import requests
# from auth import refresh_access_token
import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

BASE = "https://fantasysports.yahooapis.com/fantasy/v2"
# Must be all lower case
SPORT="mlb"
SEASON="2025"

def auth_header():
    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }


def get_user_games():
    url = f"{BASE}/users;use_login=1/games?format=json"
    r = requests.get(url, headers=auth_header())
    r.raise_for_status()
    return r.json()

def get_mlb_2025_game_key(data):
    games = data["fantasy_content"]["users"]["0"]["user"][1]["games"]
    # print("games: ", games)

    for _, game_wrapper in games.items():
        # print("game_wrapper: ", game_wrapper)
        if not isinstance(game_wrapper, dict):
            continue
        
        game = game_wrapper["game"]

        # Handle if game is a list or a dict
        if isinstance(game, list):
            meta = game[0]  # metadata block
        elif isinstance(game, dict):
            meta = game
        else:
            continue

        # print(meta)
        
        if meta.get("code") == SPORT and meta.get("season") == SEASON:
            return meta.get("game_key")

    return None

def get_league(game_key):
    # This returns all leagues
    url = f"{BASE}/users;use_login=1/games;game_keys={game_key}/leagues?format=json"
    r = requests.get(url, headers=auth_header())
    r.raise_for_status()
    response_json = r.json()
    # print(response_json)
    league_id = response_json["fantasy_content"]["users"]["0"]["user"][1]["games"]["0"]["game"][1]["leagues"]["0"]["league"][0]["league_key"]
    print(league_id)
    return league_id


def get_teams(league_key):
    url = f"{BASE}/league/{league_key}/teams?format=json"
    r = requests.get(url, headers=auth_header())
    r.raise_for_status()
    return r.json()

def get_settings(league_key):
    url = f"{BASE}/league/{league_key}/settings?format=json"
    r = requests.get(url, headers=auth_header())
    r.raise_for_status()
    return r.json()

def get_team_stats(team_key):
    """
    Retrieves weekly stats for a given team & week.
    """
    url = f"{BASE}/team/{team_key}/stats?format=json"
    r = requests.get(url, headers=auth_header())
    r.raise_for_status()
    return r.json()

def get_transactions(team_key):
    """
    Retrieves weekly stats for a given team & week.
    """
    url = f"{BASE}/team/{team_key}?format=json"
    r = requests.get(url, headers=auth_header())
    r.raise_for_status()
    return r.json()

def extract_team_info(team_json, keys):
    """
    Returns number of roster moves (add/drops) for a team.
    """
    meta = team_json["fantasy_content"]["team"][0]

    result = {}

    for d in meta:
        if isinstance(d, dict):
            for k in keys:
                if k in d:
                    result[k] = d[k]

    return result

#     return None
def get_stat_lookup(settings_json):
    stats = (
        settings_json["fantasy_content"]["league"][1]["settings"][0]["stat_categories"]["stats"]
    )
    # print(stats)
    stat_lookup = {}

    for stat in stats:
        # print(stat)
        if not isinstance(stat, dict):
            continue

        s = stat["stat"]
        # print(s)
        stat_id = s["stat_id"]
        name = s.get("display_name") or s.get("name") or "UNKNOWN"

        stat_lookup[str(stat_id)] = name

    return stat_lookup

def extract_team_moves(team_json):
    """
    Returns number of roster moves (add/drops) for a team.
    """
    meta = team_json["fantasy_content"]["team"][0]

    for item in meta:
        if isinstance(item, dict):
            if "number_of_moves" in item:
                return int(item["number_of_moves"])

    return 0  # fallback if Yahoo doesn't provide it


def map_stats(stats_json, stat_lookup):
    stat_list = (
        stats_json["fantasy_content"]["team"][1]["team_stats"]["stats"]
    )

    mapped = []

    for s in stat_list:
        stat_id = s["stat"]["stat_id"]
        value = s["stat"].get("value", "0")

        stat_name = stat_lookup.get(stat_id, f"Unknown({stat_id})")

        mapped.append({
            "stat_id": stat_id,
            "stat_name": stat_name,
            "value": value
        })

    return mapped


