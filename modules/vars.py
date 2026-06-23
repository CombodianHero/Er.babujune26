"""
vars.py — Load all configuration from environment variables.
Never hardcode API keys, tokens, or credentials here.
Set them as environment variables before running the bot.
"""
import os
from typing import List


def _int_env(key: str, default: int = 0) -> int:
    try:
        return int(os.environ.get(key, default))
    except (ValueError, TypeError):
        return default


def _list_int_env(key: str, default: str = "") -> List[int]:
    raw = os.environ.get(key, default)
    result = []
    for x in raw.split(","):
        x = x.strip()
        if x.isdigit() or (x.startswith("-") and x[1:].isdigit()):
            result.append(int(x))
    return result


# ── Telegram API credentials ──────────────────────────────────────────────────
API_ID: int    = _int_env("API_ID")
API_HASH: str  = os.environ.get("API_HASH", "")
BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "")

# ── Owner / Access control ────────────────────────────────────────────────────
OWNER: int    = _int_env("OWNER")
CREDIT: str   = os.environ.get("CREDIT", "Saini Bots")

AUTH_USERS: List[int]  = _list_int_env("AUTH_USERS", str(OWNER))
TOTAL_USERS: List[int] = _list_int_env("TOTAL_USERS", str(OWNER))

# Always ensure OWNER is in AUTH_USERS
if OWNER and OWNER not in AUTH_USERS:
    AUTH_USERS.append(OWNER)

# ── External API (key resolver) ───────────────────────────────────────────────
api_url: str   = os.environ.get("API_URL", "")
api_token: str = os.environ.get("API_TOKEN", "")

# ── File paths ────────────────────────────────────────────────────────────────
cookies_file_path: str = os.environ.get("COOKIES_FILE", "youtube_cookies.txt")
DOWNLOADS_DIR: str     = os.environ.get("DOWNLOADS_DIR", "downloads")

os.makedirs(DOWNLOADS_DIR, exist_ok=True)
