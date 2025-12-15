# scripts/get_token.py
from src.utils.google_auth import get_credentials

if __name__ == "__main__":
    creds = get_credentials()
    print("Credentials saved. Expiry:", creds.expiry)
