#!/usr/bin/env python3
"""One-time OAuth2 helper to obtain a Gmail API refresh token.

Usage:
  1. Enable Gmail API in your GCP project
  2. Create OAuth2 credentials (Desktop app) at
     https://console.cloud.google.com/apis/credentials
  3. Run:  python scripts/gmail_auth.py
  4. Follow the prompts — paste client ID, client secret, then open the URL
     in your browser, approve, and paste the authorization code back.
  5. The script prints the refresh token to store as GMAIL_REFRESH_TOKEN.
"""

import urllib.parse

import httpx

TOKEN_URL = "https://oauth2.googleapis.com/token"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
SCOPES = "https://www.googleapis.com/auth/gmail.send"
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"


def main() -> None:
    client_id = input("Paste your OAuth2 Client ID: ").strip()
    client_secret = input("Paste your OAuth2 Client Secret: ").strip()

    params = urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
    })
    auth_url = f"{AUTH_URL}?{params}"

    print(f"\nOpen this URL in your browser:\n\n{auth_url}\n")
    code = input("Paste the authorization code here: ").strip()

    resp = httpx.post(TOKEN_URL, data={
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    })
    resp.raise_for_status()
    data = resp.json()

    print("\n--- Success! ---")
    print(f"Refresh Token: {data['refresh_token']}")
    print("\nStore this as GMAIL_REFRESH_TOKEN in your environment.")
    print(f"Access Token (temporary): {data.get('access_token', 'N/A')}")


if __name__ == "__main__":
    main()
