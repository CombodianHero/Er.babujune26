"""
main.py — Bot startup: registers all handlers and starts Pyrogram.
"""
import time
import asyncio
import globals

from logs import logger
from vars import API_ID, API_HASH, BOT_TOKEN, OWNER, CREDIT, AUTH_USERS, TOTAL_USERS
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto, Message, CallbackQuery,
)
from pyrogram.errors import FloodWait

# ── Import all handler modules ────────────────────────────────────────────────
from authorisation   import register_authorisation_handlers
from broadcast       import register_broadcast_handlers
from commands        import register_commands_handlers
from features        import register_feature_handlers
from upgrade         import register_upgrade_handlers
from settings        import register_settings_handlers
from text_handler    import register_text_handlers
from html_handler    import register_html_handlers
from youtube_handler import register_youtube_handlers
from drm_handler     import register_drm_handlers

# ── Bot images ────────────────────────────────────────────────────────────────
_START_IMAGE = "https://envs.sh/GVI.jpg"

# ── Client ────────────────────────────────────────────────────────────────────
bot = Client(
    "SainiBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)


# ── /start ────────────────────────────────────────────────────────────────────
@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, m: Message) -> None:
    uid  = m.from_user.id
    name = m.from_user.first_name

    if uid not in TOTAL_USERS:
        TOTAL_USERS.append(uid)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Features",  callback_data="feat_command"),
         InlineKeyboardButton("💎 Upgrade",   callback_data="upgrade_command")],
        [InlineKeyboardButton("⚙️ Settings",  callback_data="setttings"),
         InlineKeyboardButton("📋 Commands",  callback_data="cmd_command")],
    ])
    await m.reply_photo(
        photo=_START_IMAGE,
        caption=(
            f"<b>Hey [{name}](tg://user?id={uid}) 👋\n\n"
            f"Welcome to <u>{CREDIT} BOT</u>! 🤖\n\n"
            f"I'm a premium downloader bot supporting\n"
            f"PDF, Videos, Audio and much more.\n\n"
            f"Use the buttons below to explore my features.</b>"
        ),
        reply_markup=keyboard,
    )


# ── /ping ─────────────────────────────────────────────────────────────────────
@bot.on_message(filters.command("ping") & filters.private)
async def ping_handler(client: Client, m: Message) -> None:
    start = time.time()
    reply = await m.reply_text("⚡ Pinging...")
    elapsed_ms = (time.time() - start) * 1000

    uptime_secs = int(time.time() - globals.BOT_START_TIME)
    days, rem   = divmod(uptime_secs, 86400)
    hours, rem  = divmod(rem, 3600)
    mins, secs  = divmod(rem, 60)
    uptime_str  = f"{days}d {hours}h {mins}m {secs}s"

    await reply.edit(
        f"<blockquote>"
        f"🏓 <b>Pong!</b>\n"
        f"⚡ Response : <b>{elapsed_ms:.2f} ms</b>\n"
        f"🕑 Uptime   : <b>{uptime_str}</b>\n"
        f"👥 Users    : <b>{len(TOTAL_USERS)}</b>"
        f"</blockquote>"
    )


# ── /id ───────────────────────────────────────────────────────────────────────
@bot.on_message(filters.command("id") & filters.private)
async def id_handler(client: Client, m: Message) -> None:
    await m.reply_text(
        f"<blockquote>"
        f"👤 <b>Your ID   :</b> <code>{m.from_user.id}</code>\n"
        f"💬 <b>Chat ID   :</b> <code>{m.chat.id}</code>\n"
        f"🌐 <b>Username  :</b> @{m.from_user.username or 'N/A'}"
        f"</blockquote>"
    )


# ── /info ─────────────────────────────────────────────────────────────────────
@bot.on_message(filters.command("info") & filters.private)
async def info_handler(client: Client, m: Message) -> None:
    u = m.from_user
    premium_status = "✅ Premium" if u.id in AUTH_USERS else "❌ Free"
    await m.reply_photo(
        photo=_START_IMAGE,
        caption=(
            f"<b>👤 User Info</b>\n\n"
            f"<blockquote>"
            f"🪪 <b>Name     :</b> {u.first_name} {u.last_name or ''}\n"
            f"🆔 <b>User ID  :</b> <code>{u.id}</code>\n"
            f"🌐 <b>Username :</b> @{u.username or 'N/A'}\n"
            f"💎 <b>Status   :</b> {premium_status}"
            f"</blockquote>"
        ),
    )


# ── /stop ─────────────────────────────────────────────────────────────────────
@bot.on_message(filters.command("stop") & filters.private)
async def stop_handler(client: Client, m: Message) -> None:
    if not globals.processing_request:
        await m.reply_text("⚠️ No active task to stop.")
        return
    globals.cancel_requested = True
    await m.reply_text("🚦 **Stop signal sent. Task will halt after current file.**")


# ── /reset ────────────────────────────────────────────────────────────────────
@bot.on_message(filters.command("reset") & filters.private)
async def reset_handler(client: Client, m: Message) -> None:
    if m.chat.id != OWNER:
        return
    globals.processing_request = False
    globals.cancel_requested   = False
    await m.reply_text("✅ **Bot state reset successfully.**")


# ── /logs ─────────────────────────────────────────────────────────────────────
@bot.on_message(filters.command("logs") & filters.private)
async def logs_handler(client: Client, m: Message) -> None:
    import os
    log_file = "logs.txt"
    if not os.path.exists(log_file) or os.path.getsize(log_file) == 0:
        await m.reply_text("📭 **Log file is empty or not found.**")
        return
    await m.reply_document(
        document=log_file,
        caption="📋 **Bot Activity Logs**",
    )


# ── Back to main menu callback ────────────────────────────────────────────────
@bot.on_callback_query(filters.regex("^back_to_main_menu$"))
async def back_main(client: Client, cq: CallbackQuery) -> None:
    uid  = cq.from_user.id
    name = cq.from_user.first_name
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Features",  callback_data="feat_command"),
         InlineKeyboardButton("💎 Upgrade",   callback_data="upgrade_command")],
        [InlineKeyboardButton("⚙️ Settings",  callback_data="setttings"),
         InlineKeyboardButton("📋 Commands",  callback_data="cmd_command")],
    ])
    await cq.message.edit_media(
        InputMediaPhoto(
            media=_START_IMAGE,
            caption=(
                f"<b>Hey [{name}](tg://user?id={uid}) 👋\n\n"
                f"Welcome to <u>{CREDIT} BOT</u>! 🤖\n\n"
                f"I'm a premium downloader bot supporting\n"
                f"PDF, Videos, Audio and much more.\n\n"
                f"Use the buttons below to explore my features.</b>"
            ),
        ),
        reply_markup=keyboard,
    )
    await cq.answer()


# ── Register all module handlers ──────────────────────────────────────────────
def register_all(bot: Client) -> None:
    register_authorisation_handlers(bot)
    register_broadcast_handlers(bot)
    register_commands_handlers(bot)
    register_feature_handlers(bot)
    register_upgrade_handlers(bot)
    register_settings_handlers(bot)
    register_text_handlers(bot)
    register_html_handlers(bot)
    register_youtube_handlers(bot)
    register_drm_handlers(bot)
    logger.info("All handlers registered.")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info(f"Starting {CREDIT} Bot...")
    register_all(bot)
    bot.run()
