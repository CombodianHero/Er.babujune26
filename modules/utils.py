"""
utils.py — Shared utility functions: progress bar, size/time formatters, download helpers.
"""
import os
import time
import random
import logging
import asyncio
import datetime
import subprocess
import concurrent.futures
import aiohttp
import aiofiles
import requests

from math import ceil
from pathlib import Path
from io import BytesIO
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait

logger = logging.getLogger(__name__)

# ── Timer helper ──────────────────────────────────────────────────────────────

class Timer:
    """Rate-limiter: allow an action only once every N seconds."""

    def __init__(self, interval: float = 5.0):
        self._last = time.time()
        self._interval = interval

    def can_send(self) -> bool:
        now = time.time()
        if now - self._last >= self._interval:
            self._last = now
            return True
        return False


_timer = Timer(interval=5)


# ── Human-readable formatters ─────────────────────────────────────────────────

def human_readable_bytes(value: float, digits: int = 2) -> str:
    """Return a human-readable file size string."""
    if value is None:
        return "N/A"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024.0:
            return f"{value:.{digits}f} {unit}"
        value /= 1024.0
    return f"{value:.{digits}f} PB"


def human_readable_time(seconds: float, precision: int = 1) -> str:
    """Return a human-readable time delta string."""
    delta = datetime.timedelta(seconds=max(0, int(seconds)))
    parts = []
    if delta.days:
        parts.append(f"{delta.days}d")
    remaining = delta.seconds
    if remaining >= 3600:
        h = remaining // 3600
        parts.append(f"{h}h")
        remaining -= h * 3600
    if remaining >= 60:
        m = remaining // 60
        parts.append(f"{m}m")
        remaining -= m * 60
    if remaining or not parts:
        parts.append(f"{remaining}s")
    return "".join(parts[:precision] if precision else parts)


# ── Progress bar ──────────────────────────────────────────────────────────────

_BAR_FILLED  = "🟩"
_BAR_EMPTY   = "⬜"
_BAR_LENGTH  = 10


async def progress_bar(current: int, total: int, reply: Message, start: float) -> None:
    """Pyrogram upload/download progress callback."""
    if not _timer.can_send():
        return
    elapsed = time.time() - start
    if elapsed < 1 or total == 0:
        return

    speed = current / elapsed
    eta   = (total - current) / speed if speed > 0 else 0
    pct   = current * 100 / total
    filled = int(current * _BAR_LENGTH / total)

    bar  = _BAR_FILLED * filled + _BAR_EMPTY * (_BAR_LENGTH - filled)
    from vars import CREDIT
    text = (
        f"<blockquote>`╭──⌯═════𝐁𝐨𝐭 𝐒𝐭𝐚𝐭𝐢𝐜𝐬══════⌯──╮\n"
        f"├⚡ {bar}\n"
        f"├⚙️ Progress ➤ | {pct:.1f}% |\n"
        f"├🚀 Speed   ➤ | {human_readable_bytes(speed)}/s |\n"
        f"├📟 Done    ➤ | {human_readable_bytes(current)} |\n"
        f"├🧲 Size    ➤ | {human_readable_bytes(total)} |\n"
        f"├🕑 ETA     ➤ | {human_readable_time(eta)} |\n"
        f"╰─═══✨🦋{CREDIT}🦋✨═══─╯`</blockquote>"
    )
    try:
        await reply.edit(text)
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception:
        pass


# ── Video / file helpers ──────────────────────────────────────────────────────

def get_video_duration(filepath: str) -> float:
    """Return video duration in seconds via ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", filepath],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def get_mps_and_keys(api_url: str):
    """Fetch MPD URL and decryption keys from the key-resolver API."""
    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("url"), data.get("keys")
    except Exception as e:
        logger.error(f"get_mps_and_keys failed: {e}")
        return None, None


def run_cmd(cmd: str) -> str:
    """Run a shell command synchronously and return stdout."""
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = result.stdout.decode(errors="replace")
    logger.info(f"CMD: {cmd}\n{out}")
    return out


def run_parallel(cmds: list, workers: int = 4) -> None:
    """Run multiple shell commands in a thread pool."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(run_cmd, cmds))


async def async_run(cmd: str) -> tuple:
    """Run a shell command asynchronously."""
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return proc.returncode, stdout.decode(errors="replace"), stderr.decode(errors="replace")


# ── Async download helpers ────────────────────────────────────────────────────

async def aio_download_pdf(url: str, filename: str) -> str:
    """Download a file asynchronously and save it; return the saved path."""
    path = f"{filename}.pdf"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=120)) as resp:
            resp.raise_for_status()
            async with aiofiles.open(path, "wb") as f:
                async for chunk in resp.content.iter_chunked(65536):
                    await f.write(chunk)
    return path


# Keep backward-compatible aliases used in saini.py / drm_handler.py
async def aio(url: str, name: str) -> str:
    return await aio_download_pdf(url, name)


async def download(url: str, name: str) -> str:
    return await aio_download_pdf(url, name)


def old_download(url: str, file_name: str, chunk_size: int = 1024 * 64) -> str:
    """Synchronous chunked download via requests."""
    if os.path.exists(file_name):
        os.remove(file_name)
    with requests.get(url, stream=True, timeout=60, allow_redirects=True) as r:
        r.raise_for_status()
        with open(file_name, "wb") as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
    return file_name


# ── yt-dlp video download ─────────────────────────────────────────────────────

_failed_counter = 0


async def download_video(url: str, cmd: str, name: str) -> str:
    """Download a video using yt-dlp (cmd) and return the output file path."""
    global _failed_counter
    full_cmd = f"{cmd} -R 25 --fragment-retries 25 --external-downloader aria2c --downloader-args 'aria2c: -x 16 -j 32'"
    logger.info(f"download_video: {full_cmd}")
    proc = subprocess.run(full_cmd, shell=True)

    if "visionias" in cmd and proc.returncode != 0 and _failed_counter <= 10:
        _failed_counter += 1
        await asyncio.sleep(5)
        return await download_video(url, cmd, name)
    _failed_counter = 0

    for candidate in [name, f"{name}.mp4", f"{name}.mkv", f"{name}.webm", f"{name}.mp4.webm"]:
        if os.path.isfile(candidate):
            return candidate
    base = os.path.splitext(name)[0]
    for ext in ("mp4", "mkv", "webm"):
        if os.path.isfile(f"{base}.{ext}"):
            return f"{base}.{ext}"
    return name


# ── DRM decrypt + merge ───────────────────────────────────────────────────────

async def decrypt_and_merge_video(
    mpd_url: str, keys_string: str, output_path: str, output_name: str, quality: str = "720"
) -> str:
    """Download encrypted MPD, decrypt with mp4decrypt, merge with ffmpeg."""
    out_dir = Path(output_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Download
    dl_cmd = (
        f'yt-dlp -f "bv[height<={quality}]+ba/b" -o "{out_dir}/file.%(ext)s" '
        f'--allow-unplayable-format --no-check-certificate '
        f'--external-downloader aria2c "{mpd_url}"'
    )
    logger.info(f"MPD download: {dl_cmd}")
    await async_run(dl_cmd)

    files = list(out_dir.iterdir())
    video_ok = audio_ok = False

    for f in files:
        if f.suffix == ".mp4" and not video_ok:
            cmd = f'mp4decrypt {keys_string} --show-progress "{f}" "{out_dir}/video.mp4"'
            os.system(cmd)
            video_ok = (out_dir / "video.mp4").exists()
            f.unlink(missing_ok=True)
        elif f.suffix == ".m4a" and not audio_ok:
            cmd = f'mp4decrypt {keys_string} --show-progress "{f}" "{out_dir}/audio.m4a"'
            os.system(cmd)
            audio_ok = (out_dir / "audio.m4a").exists()
            f.unlink(missing_ok=True)

    if not video_ok or not audio_ok:
        raise FileNotFoundError("Decryption failed: video or audio file missing.")

    merged = out_dir / f"{output_name}.mp4"
    merge_cmd = f'ffmpeg -y -i "{out_dir}/video.mp4" -i "{out_dir}/audio.m4a" -c copy "{merged}"'
    os.system(merge_cmd)

    for tmp in ("video.mp4", "audio.m4a"):
        p = out_dir / tmp
        if p.exists():
            p.unlink()

    if not merged.exists():
        raise FileNotFoundError("Merged output file not found.")
    return str(merged)


# ── Decryption for AES-XOR encrypted files (APPX) ────────────────────────────

import mmap


def decrypt_file(file_path: str, key: str) -> bool:
    """XOR-decrypt the first 28 bytes of a file in-place."""
    if not os.path.exists(file_path):
        return False
    with open(file_path, "r+b") as f:
        n = min(28, os.path.getsize(file_path))
        with mmap.mmap(f.fileno(), length=n, access=mmap.ACCESS_WRITE) as mm:
            for i in range(n):
                mm[i] ^= ord(key[i]) if i < len(key) else i
    return True


async def download_and_decrypt_video(url: str, cmd: str, name: str, key: str):
    """Download video then decrypt it in-place."""
    path = await download_video(url, cmd, name)
    if path and decrypt_file(path, key):
        logger.info(f"Decrypted: {path}")
        return path
    logger.error(f"Decrypt failed for: {path}")
    return None


# ── Send helpers used by drm_handler ─────────────────────────────────────────

async def send_vid(
    bot: Client, m: Message, cc: str, filename: str,
    vidwatermark: str, thumb: str, name: str, prog: Message, channel_id
) -> None:
    """Generate thumbnail, apply watermark if needed, upload video."""
    thumb_path = f"{filename}.jpg"
    subprocess.run(
        f'ffmpeg -y -i "{filename}" -ss 00:00:10 -vframes 1 "{thumb_path}"',
        shell=True, stderr=subprocess.DEVNULL,
    )
    await prog.delete(True)
    reply1 = await bot.send_message(channel_id, f"**📩 Uploading:**\n<blockquote><b>{name}</b></blockquote>")
    reply  = await m.reply_text(f"**📤 Uploading:**\n<blockquote><b>{name}</b></blockquote>")

    thumbnail = thumb_path if thumb == "/d" else thumb
    w_filename = filename

    if vidwatermark != "/d":
        w_filename = f"w_{filename}"
        font = "vidwater.ttf"
        subprocess.run(
            f'ffmpeg -y -i "{filename}" '
            f'-vf "drawtext=fontfile={font}:text=\'{vidwatermark}\':'
            f'fontcolor=white@0.3:fontsize=h/6:x=(w-text_w)/2:y=(h-text_h)/2" '
            f'-codec:a copy "{w_filename}"',
            shell=True, stderr=subprocess.DEVNULL,
        )

    dur = int(get_video_duration(w_filename))
    start_time = time.time()
    try:
        await bot.send_video(
            channel_id, w_filename, caption=cc,
            supports_streaming=True, height=720, width=1280,
            thumb=thumbnail, duration=dur,
            progress=progress_bar, progress_args=(reply, start_time),
        )
    except Exception:
        await bot.send_document(
            channel_id, w_filename, caption=cc,
            progress=progress_bar, progress_args=(reply, start_time),
        )

    # Cleanup
    for p in [w_filename, thumb_path]:
        try:
            os.remove(p)
        except FileNotFoundError:
            pass
    try:
        await reply.delete(True)
        await reply1.delete(True)
    except Exception:
        pass


# ── Misc helpers ──────────────────────────────────────────────────────────────

def parse_vid_info(info: str) -> list:
    """Parse yt-dlp format list into [(format_id, label), ...]."""
    result, seen = [], []
    for line in info.strip().splitlines():
        if "[" in line or "---" in line:
            continue
        while "  " in line:
            line = line.replace("  ", " ")
        parts = line.split("|")[0].split(" ", 3)
        try:
            label = parts[2]
            if "RESOLUTION" not in label and label not in seen and "audio" not in label:
                seen.append(label)
                result.append((parts[0], label))
        except IndexError:
            pass
    return result


def vid_info(info: str) -> dict:
    """Parse yt-dlp format list into {label: format_id}."""
    result, seen = {}, []
    for line in info.strip().splitlines():
        if "[" in line or "---" in line:
            continue
        while "  " in line:
            line = line.replace("  ", " ")
        parts = line.split("|")[0].split(" ", 3)
        try:
            label = parts[2]
            if "RESOLUTION" not in label and label not in seen and "audio" not in label:
                seen.append(label)
                result[label] = parts[0]
        except IndexError:
            pass
    return result


def time_name() -> str:
    now = datetime.datetime.now()
    return f"{datetime.date.today()} {now.strftime('%H%M%S')}.mp4"
