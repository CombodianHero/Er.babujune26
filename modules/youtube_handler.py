"""
youtube_handler.py — YouTube tools:
  /cookies   — upload new youtube_cookies.txt
  /getcookies — download current cookies file
  /y2t        — YouTube playlist → .txt link file
  /ytm        — YouTube links / playlist.txt → .mp3 audio
"""
import os
import asyncio
import yt_dlp
from pyromod import listen
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from vars import CREDIT, cookies_file_path, AUTH_USERS
import globals


# ── Shared yt-dlp base options ────────────────────────────────────────────────

def _ydl_base(cookies: str | None = None) -> dict:
    opts = {
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
    }
    if cookies and os.path.exists(cookies):
        opts["cookiefile"] = cookies
    return opts


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sanitise(name: str) -> str:
    """Remove characters that are unsafe in file/channel names."""
    for ch in r'\/:*?"<>|#@+':
        name = name.replace(ch, "")
    return name.strip()


async def _collect_links_from_msg(bot: Client, m: Message, editable: Message):
    """
    Prompt the user to send a .txt file or raw YouTube links,
    then return a list of (title, url) tuples.
    """
    inp: Message = await bot.listen(editable.chat.id)

    if inp.document and inp.document.file_name.endswith(".txt"):
        path = await inp.download()
        fname = os.path.splitext(inp.document.file_name)[0]
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = [l.strip() for l in f if l.strip()]
        os.remove(path)
        await inp.delete()
        return fname, lines

    elif inp.text:
        lines = [l.strip() for l in inp.text.splitlines() if l.strip()]
        await inp.delete()
        return "YouTube_Links", lines

    await inp.delete()
    return None, []


# ── register ──────────────────────────────────────────────────────────────────

def register_youtube_handlers(bot: Client) -> None:

    # ── /cookies — upload new cookie file ────────────────────────────────────
    @bot.on_message(filters.command("cookies") & filters.private)
    async def cookies_handler(client: Client, m: Message) -> None:
        editable = await m.reply_text(
            "📁 **Please upload your YouTube cookies .txt file.**\n"
            "<blockquote>Export it from your browser using the "
            "<i>Get cookies.txt LOCALLY</i> extension.</blockquote>"
        )
        try:
            inp: Message = await client.listen(m.chat.id)
            if not inp.document or not inp.document.file_name.endswith(".txt"):
                await editable.edit("❌ Invalid file. Please send a `.txt` file.")
                await inp.delete()
                return
            dl = await inp.download()
            with open(dl, "r", encoding="utf-8") as f:
                data = f.read()
            os.remove(dl)
            with open(cookies_file_path, "w", encoding="utf-8") as f:
                f.write(data)
            await editable.delete()
            await inp.delete()
            await m.reply_text(
                f"✅ **Cookies updated!**\n"
                f"Saved as `{cookies_file_path}`."
            )
        except Exception as e:
            await editable.edit(f"❌ Failed:\n<blockquote>{e}</blockquote>")

    # ── /getcookies — send current cookie file ────────────────────────────────
    @bot.on_message(filters.command("getcookies") & filters.private)
    async def getcookies_handler(client: Client, m: Message) -> None:
        if not os.path.exists(cookies_file_path):
            await m.reply_text("❌ No cookies file found.")
            return
        try:
            await client.send_document(
                m.chat.id,
                document=cookies_file_path,
                caption=f"📁 Current `{cookies_file_path}`",
            )
        except Exception as e:
            await m.reply_text(f"❌ Error: {e}")

    # ── /y2t — YouTube Playlist → .txt ───────────────────────────────────────
    @bot.on_message(filters.command("y2t") & filters.private)
    async def y2t_handler(client: Client, m: Message) -> None:
        editable = await m.reply_text(
            "🔪 **YouTube → .txt Converter**\n\n"
            "<blockquote>Send a YouTube Playlist URL to extract all video titles and links "
            "into a `.txt` file.</blockquote>"
        )
        inp: Message = await bot.listen(editable.chat.id)
        url = inp.text.strip() if inp.text else ""
        await inp.delete()

        if not url or "youtu" not in url:
            await editable.edit("❌ Please send a valid YouTube playlist URL.")
            return

        await editable.edit("⏳ **Fetching playlist info...**")

        ydl_opts = {
            **_ydl_base(cookies_file_path),
            "extract_flat": True,
            "playlistend": 5000,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as e:
            await editable.edit(f"❌ Failed to fetch playlist:\n<blockquote>{e}</blockquote>")
            return

        if not info or "entries" not in info:
            await editable.edit("❌ No videos found or invalid playlist.")
            return

        playlist_name = _sanitise(info.get("title", "YouTube_Playlist"))
        lines = []
        for entry in info["entries"]:
            if not entry:
                continue
            title = _sanitise(entry.get("title", "Untitled"))
            vid_url = entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id','')}"
            lines.append(f"{title}:{vid_url}")

        if not lines:
            await editable.edit("❌ No valid entries found.")
            return

        os.makedirs("downloads", exist_ok=True)
        txt_path = os.path.join("downloads", f"{playlist_name}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        await editable.delete()
        await m.reply_document(
            document=txt_path,
            caption=(
                f"🎬 **{playlist_name}.txt**\n\n"
                f"<blockquote>✅ {len(lines)} video(s) extracted.</blockquote>"
            ),
        )
        os.remove(txt_path)

    # ── /ytm — YouTube → .mp3 downloader ────────────────────────────────────
    @bot.on_message(filters.command("ytm") & filters.private)
    async def ytm_handler(client: Client, m: Message) -> None:
        globals.processing_request = True
        globals.cancel_requested = False

        editable = await m.reply_text(
            "🎶 **YouTube → .mp3 Downloader**\n\n"
            "<blockquote>"
            "01 • Send a `.txt` file with YouTube links\n"
            "02 • Or paste one or more YouTube URLs (one per line)"
            "</blockquote>"
        )

        playlist_name, lines = await _collect_links_from_msg(bot, m, editable)
        if not lines:
            await editable.edit("❌ No links received.")
            globals.processing_request = False
            return

        yt_lines = [l for l in lines if "youtu" in l]
        if not yt_lines:
            await editable.edit("❌ No YouTube links found.")
            globals.processing_request = False
            return

        await editable.edit(
            f"✅ **{len(yt_lines)} YouTube link(s) found.**\n"
            f"Send the starting index (e.g. `1`) or wait 10s to start from beginning."
        )

        try:
            start_msg: Message = await bot.listen(editable.chat.id, timeout=10)
            start = max(1, int(start_msg.text.strip()))
            await start_msg.delete()
        except (asyncio.TimeoutError, ValueError):
            start = 1

        await editable.delete()

        ydl_opts = {
            **_ydl_base(cookies_file_path),
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "outtmpl": "downloads/%(title)s.%(ext)s",
        }

        count = start
        for raw in yt_lines[start - 1:]:
            if globals.cancel_requested:
                await m.reply_text("🚦 **Stopped by user.**")
                break

            # Support both raw URLs and "Name:URL" format
            url = raw.split(":", 1)[1].strip() if "://" in raw and ":" in raw.split("://")[0] else raw

            status = await m.reply_text(
                f"⬇️ **Downloading [{count}]:**\n<blockquote>{url}</blockquote>"
            )
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = _sanitise(info.get("title", f"audio_{count}"))

                mp3_path = f"downloads/{title}.mp3"
                if os.path.exists(mp3_path):
                    await status.edit(
                        f"📤 **Uploading [{count}]:**\n<blockquote>{title}</blockquote>"
                    )
                    await m.reply_document(
                        document=mp3_path,
                        caption=f"🎵 **{title}.mp3**\n\n<b>Credit: {CREDIT}</b>",
                    )
                    os.remove(mp3_path)
                else:
                    await status.edit(
                        f"⚠️ **Could not find output for [{count}]:** `{title}`"
                    )
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                await status.edit(
                    f"❌ **Failed [{count}]:**\n<blockquote>{e}</blockquote>"
                )
            finally:
                count += 1
                await asyncio.sleep(1)

        globals.processing_request = False
        if not globals.cancel_requested:
            await m.reply_text(
                f"✅ **Done!** Processed {count - start} track(s)."
            )
        globals.cancel_requested = False
