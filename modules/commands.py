"""
commands.py — Bot command menu callbacks (User & Owner command lists).
"""
from vars import CREDIT
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Message

_MENU_IMAGE = "https://tinypic.host/images/2025/07/14/file_00000000fc2461fbbdd6bc500cecbff8_conversation_id6874702c-9760-800e-b0bf-8e0bcf8a3833message_id964012ce-7ef5-4ad4-88e0-1c41ed240c03-1-1.jpg"


def register_commands_handlers(bot: Client) -> None:

    # ── Commands root menu ────────────────────────────────────────────────────
    @bot.on_callback_query(filters.regex("^cmd_command$"))
    async def cmd_menu(client, cq):
        name = cq.from_user.first_name
        uid  = cq.from_user.id
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚻 User Commands",  callback_data="user_command"),
             InlineKeyboardButton("🚹 Owner Commands", callback_data="owner_command")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_main_menu")],
        ])
        await cq.message.edit_media(
            InputMediaPhoto(
                media=_MENU_IMAGE,
                caption=f"✨ **[{name}](tg://user?id={uid}) — Choose a command group:**"
            ),
            reply_markup=keyboard,
        )
        await cq.answer()

    # ── User commands ─────────────────────────────────────────────────────────
    @bot.on_callback_query(filters.regex("^user_command$"))
    async def user_commands(client, cq):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Commands", callback_data="cmd_command")]
        ])
        text = (
            f"💥 **BOT USER COMMANDS**\n"
            f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
            f"📌 **Main Features:**\n\n"
            f"➥ /start — Bot Status Check\n"
            f"➥ /ping  — Check bot response time\n"
            f"➥ /id    — Get Chat / User ID\n"
            f"➥ /info  — Your Telegram Info\n"
            f"➥ /stop  — Cancel Running Task\n"
            f"➥ /logs  — View Bot Activity Logs\n"
            f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
            f"⚙️ **Tools & Converters:**\n\n"
            f"➥ /y2t   — YouTube Playlist → .txt\n"
            f"➥ /ytm   — YouTube → .mp3 Downloader\n"
            f"➥ /t2t   — Text → .txt Generator\n"
            f"➥ /t2h   — .txt → .html Converter\n"
            f"➥ /cookies — Update YT Cookies\n"
            f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
            f"💡 **Tips:**\n\n"
            f"• Send a .txt file → auto batch download\n"
            f"• Send a direct link → instant download\n"
            f"• Supports PDF, images, video & more\n\n"
            f"╭────────⊰◆⊱────────╮\n"
            f" ➠ 𝐌𝐚𝐝𝐞 𝐁𝐲 : {CREDIT} 💻\n"
            f"╰────────⊰◆⊱────────╯"
        )
        await cq.message.edit_media(
            InputMediaPhoto(media=_MENU_IMAGE, caption=text),
            reply_markup=keyboard,
        )
        await cq.answer()

    # ── Owner commands ────────────────────────────────────────────────────────
    @bot.on_callback_query(filters.regex("^owner_command$"))
    async def owner_commands(client, cq):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Commands", callback_data="cmd_command")]
        ])
        text = (
            f"👤 **Bot Owner Commands**\n\n"
            f"➥ /addauth `<id>`  — Add Premium User\n"
            f"➥ /rmauth  `<id>`  — Remove Premium User\n"
            f"➥ /users           — List All Premium Users\n"
            f"➥ /broadcast       — Send Message to All Users\n"
            f"➥ /broadusers      — List All Bot Users\n"
            f"➥ /reset           — Restart the Bot\n"
            f"➥ /getcookies      — Get Current YT Cookies\n"
            f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
            f"╭────────⊰◆⊱────────╮\n"
            f" ➠ 𝐌𝐚𝐝𝐞 𝐁𝐲 : {CREDIT} 💻\n"
            f"╰────────⊰◆⊱────────╯"
        )
        await cq.message.edit_media(
            InputMediaPhoto(media=_MENU_IMAGE, caption=text),
            reply_markup=keyboard,
        )
        await cq.answer()
