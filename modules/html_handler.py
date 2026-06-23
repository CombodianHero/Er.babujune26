"""
html_handler.py — /t2h command: convert a .txt link file into an HTML player page.
"""
import os
import re
from vars import CREDIT
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen


# ── URL categorisation ────────────────────────────────────────────────────────

def _extract_entries(content: str) -> list[tuple[str, str]]:
    """Parse 'Name:URL' lines from .txt content."""
    entries = []
    for line in content.strip().splitlines():
        line = line.strip()
        if not line or "://" not in line:
            continue
        if ":" in line:
            name, url = line.split(":", 1)
            entries.append((name.strip(), url.strip()))
    return entries


def _categorise(entries: list[tuple[str, str]]):
    videos, pdfs, others = [], [], []
    for name, url in entries:
        low = url.lower()
        if any(ext in low for ext in (".m3u8", ".mp4", ".mkv", ".webm")) or "youtu" in low:
            # Normalise YouTube embed links
            if "youtube.com/embed/" in url:
                vid_id = url.split("/")[-1].split("?")[0]
                url = f"https://www.youtube.com/watch?v={vid_id}"
            videos.append((name, url))
        elif ".pdf" in low or "pdf" in low:
            pdfs.append((name, url))
        else:
            others.append((name, url))
    return videos, pdfs, others


# ── HTML generator ────────────────────────────────────────────────────────────

def _build_html(title: str, videos: list, pdfs: list, others: list) -> str:
    def _vid_links(items):
        return "\n".join(
            f'<li><a href="#" class="vid-link" data-src="{url}" onclick="playVideo(this)">'
            f'▶ {name}</a></li>'
            for name, url in items
        )

    def _doc_links(items, icon="📄"):
        return "\n".join(
            f'<li><a href="{url}" target="_blank" rel="noopener">{icon} {name}</a></li>'
            for name, url in items
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{title}</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/video.js/8.6.1/video-js.min.css"/>
  <style>
    :root {{
      --bg: #0d0d0d; --card: #161616; --accent: #00d4ff;
      --text: #e0e0e0; --muted: #888; --radius: 10px;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; min-height: 100vh; }}
    header {{ background: linear-gradient(135deg,#1a1a2e,#16213e); padding: 18px 24px;
              display: flex; align-items: center; gap: 12px; border-bottom: 2px solid var(--accent); }}
    header h1 {{ font-size: 1.25rem; color: var(--accent); }}
    .layout {{ display: flex; min-height: calc(100vh - 60px); }}
    .sidebar {{ width: 320px; min-width: 240px; background: var(--card); overflow-y: auto;
                border-right: 1px solid #222; padding: 12px; }}
    .main {{ flex: 1; padding: 20px; }}
    .player-wrap {{ background: #000; border-radius: var(--radius); overflow: hidden; margin-bottom: 16px; }}
    video {{ width: 100%; max-height: 60vh; }}
    section {{ margin-bottom: 20px; }}
    section h2 {{ font-size: .85rem; text-transform: uppercase; color: var(--accent);
                  letter-spacing: 1px; margin-bottom: 8px; padding-bottom: 4px;
                  border-bottom: 1px solid #222; }}
    ul {{ list-style: none; }}
    ul li {{ padding: 6px 4px; border-bottom: 1px solid #1e1e1e; font-size: .9rem; }}
    ul li a {{ color: var(--text); text-decoration: none; transition: color .2s; display: block; }}
    ul li a:hover, ul li a.active {{ color: var(--accent); }}
    .vid-link {{ cursor: pointer; }}
    #now-playing {{ font-size: .85rem; color: var(--muted); margin-bottom: 8px; }}
    .empty {{ color: var(--muted); font-size: .85rem; padding: 8px 4px; }}
    footer {{ text-align: center; padding: 14px; color: var(--muted); font-size: .8rem;
              border-top: 1px solid #1e1e1e; }}
    @media(max-width:700px){{
      .layout {{ flex-direction: column; }}
      .sidebar {{ width: 100%; border-right: none; border-bottom: 1px solid #222; max-height: 40vh; }}
    }}
  </style>
</head>
<body>
<header>
  <span style="font-size:1.5rem">🎬</span>
  <h1>{title}</h1>
</header>
<div class="layout">
  <aside class="sidebar">
    {'<section><h2>🎥 Videos (' + str(len(videos)) + ')</h2><ul>' + _vid_links(videos) + '</ul></section>' if videos else ''}
    {'<section><h2>📄 PDFs (' + str(len(pdfs)) + ')</h2><ul>' + _doc_links(pdfs, "📕") + '</ul></section>' if pdfs else ''}
    {'<section><h2>🔗 Others (' + str(len(others)) + ')</h2><ul>' + _doc_links(others, "🔗") + '</ul></section>' if others else ''}
    {'<p class="empty">No links found.</p>' if not videos and not pdfs and not others else ''}
  </aside>
  <main class="main">
    <div id="now-playing">Click a video to play ▶</div>
    <div class="player-wrap">
      <video id="player" class="video-js vjs-big-play-centered" controls preload="auto"
             data-setup='{{"fluid": true}}'></video>
    </div>
    <p style="color:var(--muted);font-size:.8rem">
      Supports HLS (.m3u8), MP4, and direct stream URLs.
    </p>
  </main>
</div>
<footer>Made with ❤️ by <b>{CREDIT}</b> | Saini DRM Bot</footer>

<script src="https://cdnjs.cloudflare.com/ajax/libs/video.js/8.6.1/video.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/videojs-contrib-hls/5.15.0/videojs-contrib-hls.min.js"></script>
<script>
  const player = videojs('player');

  function playVideo(el) {{
    document.querySelectorAll('.vid-link').forEach(a => a.classList.remove('active'));
    el.classList.add('active');
    const src = el.dataset.src;
    const isHls = src.includes('.m3u8');
    player.src({{ type: isHls ? 'application/x-mpegURL' : 'video/mp4', src }});
    player.play();
    document.getElementById('now-playing').textContent = '▶ Now Playing: ' + el.textContent.trim();
  }}
</script>
</body>
</html>"""


# ── Handler ───────────────────────────────────────────────────────────────────

async def txt_to_html(bot: Client, message: Message) -> None:
    editable = await message.reply_text(
        "<blockquote><b>🌐 .txt → .html Converter\n\n"
        "Upload your .txt file containing links in format:\n"
        "<code>Name:URL</code>\n"
        "One entry per line.</b></blockquote>"
    )

    input_msg: Message = await bot.listen(message.chat.id)

    if not input_msg.document or not input_msg.document.file_name.endswith(".txt"):
        await editable.edit("❌ **Please send a valid .txt file.**")
        await input_msg.delete()
        return

    dl_path = await input_msg.download()
    await input_msg.delete()

    with open(dl_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    os.remove(dl_path)

    base_name = os.path.splitext(input_msg.document.file_name)[0]
    title = base_name.replace("_", " ").strip()

    entries = _extract_entries(content)
    if not entries:
        await editable.edit(
            "❌ **No valid `Name:URL` entries found in the file.**\n\n"
            "Make sure each line is formatted as:\n`Lecture Name:https://example.com/video.m3u8`"
        )
        return

    videos, pdfs, others = _categorise(entries)

    os.makedirs("downloads", exist_ok=True)
    html_path = os.path.join("downloads", f"{base_name}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(_build_html(title, videos, pdfs, others))

    await editable.delete()
    await message.reply_document(
        document=html_path,
        caption=(
            f"🌐 **{title}.html** is ready!\n\n"
            f"<blockquote>"
            f"🎥 Videos : <b>{len(videos)}</b>\n"
            f"📄 PDFs   : <b>{len(pdfs)}</b>\n"
            f"🔗 Others : <b>{len(others)}</b>\n"
            f"📎 Total  : <b>{len(entries)}</b>"
            f"</blockquote>\n\n"
            f"Open the file in any browser to watch/download content."
        ),
    )
    os.remove(html_path)


def register_html_handlers(bot: Client) -> None:

    @bot.on_message(filters.command("t2h") & filters.private)
    async def call_txt_to_html(client: Client, m: Message) -> None:
        await txt_to_html(client, m)
