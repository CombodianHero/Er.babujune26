"""
globals.py — Runtime state shared across all modules.
These values are modified at runtime via /settings commands.
"""
from vars import OWNER, CREDIT

# ── Processing flags ──────────────────────────────────────────────────────────
processing_request: bool = False
cancel_requested: bool = False

# ── Bot start time (for /ping uptime) ────────────────────────────────────────
import time
BOT_START_TIME: float = time.time()

# ── Caption / file settings ───────────────────────────────────────────────────
caption: str      = "/cc1"   # /cc1 | /cc2 | /cc3 | custom text
endfilename: str  = "/d"     # suffix appended to file names, /d = disabled
thumb: str        = "/d"     # thumbnail URL or /d for auto
CR: str           = CREDIT   # credit name shown in captions
vidwatermark: str = "/d"     # watermark text on videos, /d = disabled
topic: str        = "/d"     # /yes = parse topic from (brackets) in title

# ── Platform tokens (set via /settings → Set Token) ──────────────────────────
cwtoken: str  = ""   # CareerWill JWT
cptoken: str  = ""   # ClassPlus token
pwtoken: str  = ""   # PhysicsWallah token

# ── Video quality defaults ────────────────────────────────────────────────────
raw_text2: str = "480"
quality: str   = "480p"
res: str       = "854x480"
