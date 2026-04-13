"""
Google OAuth2 Authentication Module for FNX Talent Factory.

Handles OAuth2 flow for Google Forms API and Drive API.
Supports both interactive login (local dev) and service account (production).

Usage:
    from core.integrations.google_auth import get_google_credentials

    creds = get_google_credentials()
    # Use creds with googleapiclient.discovery.build(...)
"""

import os
import json
from pathlib import Path

# Required scopes for Forms + Drive
SCOPES = [
    "https://www.googleapis.com/auth/forms.body",       # Create & edit forms
    "https://www.googleapis.com/auth/drive.file",        # Manage files created by app
]

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
CREDENTIALS_DIR = PROJECT_ROOT / "credentials"
CLIENT_SECRETS_FILE = CREDENTIALS_DIR / "client_secrets.json"
TOKEN_FILE = CREDENTIALS_DIR / "token.json"
SERVICE_ACCOUNT_FILE = CREDENTIALS_DIR / "service_account.json"


def get_google_credentials():
    """
    Get valid Google OAuth2 credentials.

    Priority:
        1. Existing token.json (cached credentials)
        2. Service account (for production/Vercel)
        3. OAuth2 flow (interactive login for local dev)

    Returns:
        google.oauth2.credentials.Credentials
    
    Raises:
        FileNotFoundError: If no credentials file found
        RuntimeError: If authentication fails
    """
    # Try 1: Load cached token
    creds = _load_cached_token()
    if creds and creds.valid:
        return creds

    # Try 1b: Refresh expired token
    if creds and creds.expired and creds.refresh_token:
        try:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            _save_token(creds)
            print("[GoogleAuth] ✅ Token refreshed successfully")
            return creds
        except Exception as e:
            print(f"[GoogleAuth] ⚠️ Token refresh failed: {e}")

    # Try 2: Service account (production)
    creds = _load_service_account()
    if creds:
        return creds

    # Try 3: Interactive OAuth2 flow (local dev)
    creds = _run_oauth_flow()
    if creds:
        return creds

    raise RuntimeError(
        "No valid Google credentials found. Please either:\n"
        "1. Place client_secrets.json in /credentials/ and run auth flow\n"
        "2. Place service_account.json in /credentials/ for production\n"
        "See: https://console.cloud.google.com/apis/credentials"
    )


def _load_cached_token():
    """Load credentials from cached token.json."""
    if not TOKEN_FILE.exists():
        return None
    try:
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        print("[GoogleAuth] 📂 Loaded cached token")
        return creds
    except Exception as e:
        print(f"[GoogleAuth] ⚠️ Failed to load cached token: {e}")
        return None


def _load_service_account():
    """Load credentials from service account JSON."""
    if not SERVICE_ACCOUNT_FILE.exists():
        return None
    try:
        from google.oauth2.service_account import Credentials
        creds = Credentials.from_service_account_file(
            str(SERVICE_ACCOUNT_FILE),
            scopes=SCOPES,
        )
        print("[GoogleAuth] 🔑 Using service account credentials")
        return creds
    except Exception as e:
        print(f"[GoogleAuth] ⚠️ Service account failed: {e}")
        return None


def _run_oauth_flow():
    """Run interactive OAuth2 flow (local development only)."""
    if not CLIENT_SECRETS_FILE.exists():
        print(f"[GoogleAuth] ❌ No client_secrets.json found at {CLIENT_SECRETS_FILE}")
        return None

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow

        print("[GoogleAuth] 🌐 Starting OAuth2 flow... A browser window will open.")
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CLIENT_SECRETS_FILE),
            scopes=SCOPES,
        )
        creds = flow.run_local_server(
            port=8090,
            prompt="consent",
            success_message="✅ FNX Talent Factory authenticated! You can close this tab.",
        )
        _save_token(creds)
        print("[GoogleAuth] ✅ OAuth2 flow completed, token saved")
        return creds
    except Exception as e:
        print(f"[GoogleAuth] ❌ OAuth flow failed: {e}")
        return None


def _save_token(creds):
    """Save credentials to token.json for future use."""
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())
    print(f"[GoogleAuth] 💾 Token saved to {TOKEN_FILE}")


def check_auth_status():
    """Check if Google credentials are available and valid.
    
    Returns:
        dict with status information
    """
    status = {
        "authenticated": False,
        "method": None,
        "client_secrets_exists": CLIENT_SECRETS_FILE.exists(),
        "token_exists": TOKEN_FILE.exists(),
        "service_account_exists": SERVICE_ACCOUNT_FILE.exists(),
    }

    try:
        creds = get_google_credentials()
        status["authenticated"] = True
        if SERVICE_ACCOUNT_FILE.exists():
            status["method"] = "service_account"
        elif TOKEN_FILE.exists():
            status["method"] = "oauth2"
    except Exception:
        pass

    return status
