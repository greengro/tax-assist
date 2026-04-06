#!/usr/bin/env python3
"""One-time OAuth2 helper to obtain a refresh token for Gmail + Google Docs.

Usage:
  1. Enable Gmail API and Google Docs API in your GCP project
  2. Create OAuth2 credentials (Desktop app) at
     https://console.cloud.google.com/apis/credentials
  3. Set env vars GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET (or paste when prompted)
  4. Run:  python scripts/gmail_auth.py
  5. Open the URL in your browser, approve, and copy the code= value from
     the redirect URL (the page won't load — that's expected).
  6. Paste the authorization code when prompted.
  7. The script prints the refresh token to store as GMAIL_REFRESH_TOKEN.

The resulting refresh token grants access to:
  - Gmail (send emails)
  - Google Docs (create/edit documents)
  - Google Drive (manage files in shared folders)
"""

import os
import urllib.parse

import httpx

TOKEN_URL = "https://oauth2.googleapis.com/token"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
SCOPES = " ".join([
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
])
REDIRECT_PORT = 8085
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}"


def main() -> None:
    client_id = os.getenv("GMAIL_CLIENT_ID", "") or input("Paste your OAuth2 Client ID: ").strip()
    client_secret = os.getenv("GMAIL_CLIENT_SECRET", "") or input("Paste your OAuth2 Client Secret: ").strip()

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
    print("After approving, your browser will redirect to a page that won't load.")
    print("Copy the 'code=' value from the URL bar and paste it below.\n")
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
    print("This token covers Gmail, Google Docs, and Google Drive scopes.")
    print(f"Access Token (temporary): {data.get('access_token', 'N/A')}")


if __name__ == "__main__":
    main()
