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

        print(meta)
        
        if meta.get("code") == SPORT and meta.get("season") == SEASON:
            return meta.get("game_key")

    return None

def get_league(game_key):
    # This returns all leagues
    url = f"{BASE}/users;use_login=1/games;game_keys={game_key}/leagues?format=json"
    r = requests.get(url, headers=auth_header())
    r.raise_for_status()
    response_json = r.json()
    print(response_json)
    league_id = response_json["fantasy_content"]["users"]["0"]["user"][1]["games"]["0"]["game"][1]["leagues"]["0"]["league"][0]["league_key"]
    print(league_id)
    return league_id


def get_teams(league_key):
    url = f"{BASE}/league/{league_key}/teams?format=json"
    r = requests.get(url, headers=auth_header())
    r.raise_for_status()
    return r.json()


# def get_team_stats_week(team_key, week_number):
#     """
#     Retrieves weekly stats for a given team & week.
#     """
#     url = f"{BASE}/team/{team_key}/stats;type=week;week={week_number}?format=json"
#     r = requests.get(url, headers=auth_header())
#     r.raise_for_status()
#     return r.json()

def get_team_stats(team_key):
    """
    Retrieves weekly stats for a given team & week.
    """
    url = f"{BASE}/team/{team_key}/stats?format=json"
    r = requests.get(url, headers=auth_header())
    r.raise_for_status()
    return r.json()


def extract_innings_pitched(stats_json):
    """
    Extracts 'IP' (innings pitched) from Yahoo team stats response.
    """
    stats = stats_json["fantasy_content"]["team"][1]["team_stats"]["stats"]
    
    for item in stats:
        if item["stat"]["stat_id"] == "50":  # Yahoo stat_id 50 = IP in baseball
            return item["stat"]["value"]

    return None

