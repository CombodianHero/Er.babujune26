# 🤖 Saini DRM Bot

A premium Telegram bot for batch downloading educational content — videos, PDFs, audio, images and more — with full settings panel, YouTube tools, HTML converter, and multi-platform deployment support.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📁 Batch `.txt` download | Send a `.txt` file with `Name:URL` lines to batch download |
| 🎥 Video downloader | HLS, MP4, MKV, APPX, DRM, M3U8, MPD |
| 📄 PDF downloader | Direct PDF, CareerWill, Google Drive |
| 🎵 Audio downloader | MP3, M4A, WAV |
| 🖼️ Image downloader | JPG, PNG, JPEG |
| 🎬 YouTube → .txt | Extract full playlist into a `Name:URL` text file |
| 🎶 YouTube → .mp3 | Batch convert YouTube links to MP3 audio |
| 🌐 .txt → .html | Convert link files into a beautiful HTML video player |
| 📝 Text → .txt | Save any text as a `.txt` file |
| 💧 Video watermark | Overlay custom text on all downloaded videos |
| 🏷️ Topic mode | Parse chapter names from `(brackets)` in titles |
| 📢 Broadcast | Send messages to all bot users |
| ⚙️ Settings panel | Caption style, quality, thumbnail, credit, tokens |
| ⚡ Ping + Uptime | Check bot health and uptime |
| 👥 Premium users | Add/remove authorized users via commands |

---

## 🚀 Deployment

### Prerequisites

- Python 3.12+
- `ffmpeg` installed
- `mp4decrypt` (Bento4) installed
- `aria2c` installed

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|---|---|---|
| `API_ID` | ✅ | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | ✅ | Telegram API Hash |
| `BOT_TOKEN` | ✅ | Bot token from [@BotFather](https://t.me/BotFather) |
| `OWNER` | ✅ | Your Telegram user ID |
| `CREDIT` | ✅ | Bot branding name shown in captions |
| `AUTH_USERS` | ❌ | Comma-separated premium user IDs |
| `API_URL` | ❌ | External DRM key resolver API base URL |
| `API_TOKEN` | ❌ | Key resolver API token |

### Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python modules/main.py
```

### Docker

```bash
docker build -t saini-bot .
docker run --env-file .env saini-bot
```

### Render / Railway

Push to GitHub and connect your repo. All env vars are defined in `render.yaml`.

### Heroku

```bash
heroku create
heroku stack:set container
heroku config:set API_ID=xxx API_HASH=xxx BOT_TOKEN=xxx OWNER=xxx CREDIT="Saini Bots"
git push heroku main
```

---

## 📋 Commands

### User Commands

| Command | Description |
|---|---|
| `/start` | Start the bot / main menu |
| `/ping` | Check bot response time and uptime |
| `/id` | Get your Telegram user/chat ID |
| `/info` | Your account info and premium status |
| `/stop` | Cancel the currently running task |
| `/logs` | Download the bot activity log file |
| `/y2t` | YouTube playlist → `.txt` link file |
| `/ytm` | YouTube links / `.txt` → `.mp3` downloader |
| `/t2t` | Convert text to a `.txt` file |
| `/t2h` | Convert `.txt` link file to HTML player |
| `/cookies` | Upload new YouTube cookies file |

### Owner Commands

| Command | Description |
|---|---|
| `/addauth <id>` | Add a user to premium |
| `/rmauth <id>` | Remove a user from premium |
| `/users` | List all premium users |
| `/broadcast` | Broadcast a message to all users |
| `/broadusers` | List all users who started the bot |
| `/reset` | Reset bot state |
| `/getcookies` | Download current YouTube cookies file |

---

## 📁 Project Structure

```
SainiBot/
├── modules/
│   ├── vars.py           # Environment variable config
│   ├── globals.py        # Runtime state store
│   ├── logs.py           # Rotating logger
│   ├── utils.py          # Shared helpers: progress bar, download, ffmpeg
│   ├── saini.py          # Backward-compatible aliases → utils.py
│   ├── main.py           # Bot startup + core commands (/start /ping /id etc.)
│   ├── authorisation.py  # /addauth /rmauth /users
│   ├── broadcast.py      # /broadcast /broadusers
│   ├── commands.py       # Command list menu callbacks
│   ├── features.py       # Features info menu callbacks
│   ├── upgrade.py        # Upgrade/plans menu callback
│   ├── settings.py       # Full settings panel callbacks
│   ├── text_handler.py   # /t2t — text → .txt
│   ├── html_handler.py   # /t2h — .txt → HTML player
│   ├── youtube_handler.py# /y2t /ytm /cookies /getcookies
│   └── drm_handler.py    # Core batch downloader (original)
├── app.py                # Flask keep-alive server
├── requirements.txt
├── Dockerfile
├── render.yaml
├── heroku.yml
├── Procfile
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚠️ Important Notes

- **Never commit** `.env`, `*.session`, `device_private_key.txt`, `device_client_id_blob`, or `youtube_cookies.txt` to git — all are in `.gitignore`
- The `downloads/` folder is used as temporary storage; files are deleted after upload
- Set your bot's commands list in [@BotFather](https://t.me/BotFather) using `/setcommands`

---

## 🛡️ Bot BotFather Command List

Paste this into BotFather → `/setcommands`:

```
start - Start the bot
ping - Check bot response time
id - Get your Telegram ID
info - Your account info
stop - Cancel running task
logs - Download activity logs
y2t - YouTube playlist to txt file
ytm - YouTube links to mp3
t2t - Text to txt file
t2h - txt file to HTML player
cookies - Update YouTube cookies
addauth - Add premium user (owner only)
rmauth - Remove premium user (owner only)
users - List premium users (owner only)
broadcast - Broadcast to all users (owner only)
broadusers - List all bot users (owner only)
reset - Reset bot state (owner only)
getcookies - Get cookies file (owner only)
```

---

Made with ❤️ by **Saini Bots**
