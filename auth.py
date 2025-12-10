# auth.py
# Handles:
# building auth URL
# exchanging an authorization code for tokens
# refreshing expired tokens
# saving tokens back to .env

import os
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv() # reads .env into environment variables

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

AUTH_BASE = "https://api.login.yahoo.com/oauth2/request_auth"
TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"


def build_auth_url():
    """
    Step 1: Generate the login URL to authorize your Yahoo app.
    """
    # Define params that will go into the login request
    params = {
        "client_id": CLIENT_ID, # This identifies your app to Yahoo.
        "redirect_uri": REDIRECT_URI, # The URL Yahoo will redirect to after login.
        "response_type": "code", # Ensures we get a code after logging in - later used for getting tokens
        "language": "en-us", # Ensure sign in is in english
    }
    # Form the full login url
    return AUTH_BASE + "?" + urllib.parse.urlencode(params)


def exchange_code_for_tokens(code):
    """
    Step 2: Exchange the 'code' from Yahoo for access+refresh tokens.
    """
    data = {
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code": code, # The code yahoo sent us
    }

    auth = (CLIENT_ID, CLIENT_SECRET)
    # Send the post request to get the token using authentication and correct url/data
    r = requests.post(TOKEN_URL, data=data, auth=auth)
    r.raise_for_status()
    tokens = r.json()

    # Save tokens to .env file
    # print("Before saving tokens:")
    save_tokens(tokens)
    # print("After saving tokens:")
    return tokens


def refresh_access_token(refresh_token):
    """
    Step 3: Use your refresh token to get a new access token.
    """
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    
    auth = (CLIENT_ID, CLIENT_SECRET)
    # Send refresh token to yahoo
    r = requests.post(TOKEN_URL, data=data, auth=auth)
    r.raise_for_status()
    tokens = r.json()

    # Save tokens to .env file
    save_tokens(tokens)
    return tokens


def save_tokens(tokens):
    """
    Saves tokens back to your .env file.
    """
    with open(".env", "r") as f:
        lines = f.readlines()
        print(lines)

    with open(".env", "w") as f:
        for line in lines:
            print(line)
            if line.startswith("ACCESS_TOKEN="):
                print(tokens.get('access_token'))
                f.write(f"ACCESS_TOKEN={tokens.get('access_token')}\n")
            elif line.startswith("REFRESH_TOKEN="):
                print(tokens.get('refresh_token'))
                f.write(f"REFRESH_TOKEN={tokens.get('refresh_token')}\n")
            else:
                f.write(line)

# refresh_access_token(REFRESH_TOKEN)
