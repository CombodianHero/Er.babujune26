"""
features.py — Feature info button callbacks.
"""
from vars import CREDIT
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

_FEAT_IMAGE = "https://tinypic.host/images/2025/07/14/file_000000002d44622f856a002a219cf27aconversation_id68747543-56d8-800e-ae47-bb6438a09851message_id8e8cbfb5-ea6c-4f59-974a-43bdf87130c0.png"
_BACK_FEAT  = [[InlineKeyboardButton("🔙 Back to Features", callback_data="feat_command")]]


def _feat_img(caption: str, back=True):
    kb = InlineKeyboardMarkup(_BACK_FEAT) if back else None
    return InputMediaPhoto(media=_FEAT_IMAGE, caption=caption), kb


def register_feature_handlers(bot: Client) -> None:

    # ── Features root ─────────────────────────────────────────────────────────
    @bot.on_callback_query(filters.regex("^feat_command$"))
    async def features_menu(client, cq):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📌 Auto Pin Batch",  callback_data="pin_command")],
            [InlineKeyboardButton("💧 Watermark",        callback_data="watermark_command"),
             InlineKeyboardButton("🔄 Reset Settings",  callback_data="reset_command")],
            [InlineKeyboardButton("🖨️ Bot Logs",         callback_data="logs_command")],
            [InlineKeyboardButton("🖋️ Custom File Name", callback_data="custom_command"),
             InlineKeyboardButton("🏷️ Title Mode",       callback_data="titlle_command")],
            [InlineKeyboardButton("🎥 YouTube Tools",    callback_data="yt_command")],
            [InlineKeyboardButton("🌐 HTML Converter",   callback_data="html_command")],
            [InlineKeyboardButton("📝 Text File Maker",  callback_data="txt_maker_command"),
             InlineKeyboardButton("📢 Broadcast",        callback_data="broadcast_command")],
            [InlineKeyboardButton("⚡ Ping",             callback_data="ping_feat_command")],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main_menu")],
        ])
        await cq.message.edit_media(
            InputMediaPhoto(media=_FEAT_IMAGE, caption="**✨ Premium BOT Features:**"),
            reply_markup=keyboard,
        )
        await cq.answer()

    # ── Individual feature info cards ─────────────────────────────────────────
    _cards = {
        "pin_command": (
            "📌 **Auto Pin Batch Name**\n\n"
            "Automatically pins the Batch Name in a Channel or Group "
            "when starting from the first link."
        ),
        "watermark_command": (
            "💧 **Custom Watermark**\n\n"
            "Set your own watermark text overlay on videos "
            "for added branding and personalization."
        ),
        "reset_command": (
            "🔄 **Reset Command**\n\n"
            "Use `/reset` to restart the bot if something goes wrong."
        ),
        "logs_command": (
            "🖨️ **Bot Working Logs**\n\n"
            "Use `/logs` to receive a `.txt` file with the bot's activity log."
        ),
        "custom_command": (
            "🖋️ **Custom File Name**\n\n"
            "Add a custom suffix to every file name before the extension.\n"
            "Set it via ⚙️ Settings → File Name."
        ),
        "titlle_command": (
            "🏷️ **Title Mode**\n\n"
            "Parses the topic/chapter name from `(brackets)` in the link title.\n"
            "**NOTE:** Title must be enclosed in `()` brackets.\n"
            "Enable via ⚙️ Settings → Topic."
        ),
        "broadcast_command": (
            "📢 **Broadcasting**\n\n"
            "• `/broadcast` — Send a message to all bot users.\n"
            "• `/broadusers` — View the list of all bot users."
        ),
        "txt_maker_command": (
            "📝 **Text File Maker**\n\n"
            "• `/t2t` — Convert any text block into a `.txt` file."
        ),
        "ping_feat_command": (
            "⚡ **Ping Command**\n\n"
            "• `/ping` — Check the bot's response time and uptime."
        ),
        "yt_command": (
            "🎥 **YouTube Tools**\n\n"
            "• `/y2t` — Convert a YouTube Playlist into a `.txt` link file.\n"
            "• `/ytm` — Download YouTube videos as `.mp3` audio.\n\n"
            "<blockquote><b>For /ytm:</b>\n"
            "Send a YouTube playlist `.txt` file, or paste one or more links:\n"
            "`https://www.youtube.com/watch?v=xxxxx`</blockquote>"
        ),
        "html_command": (
            "🌐 **HTML Converter**\n\n"
            "• `/t2h` — Convert a `.txt` link file into a beautiful HTML player page."
        ),
    }

    for cb_key, text in _cards.items():
        # Use a closure to capture the text correctly in the loop
        def make_handler(t):
            async def handler(client, cq):
                await cq.message.edit_media(
                    InputMediaPhoto(media=_FEAT_IMAGE, caption=t),
                    reply_markup=InlineKeyboardMarkup(_BACK_FEAT),
                )
                await cq.answer()
            return handler

        bot.on_callback_query(filters.regex(f"^{cb_key}$"))(make_handler(text))
