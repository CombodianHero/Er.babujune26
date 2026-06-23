"""
authorisation.py — Owner-only commands to manage premium users.
"""
from vars import OWNER, AUTH_USERS
from pyrogram import Client, filters
from pyrogram.types import Message


def register_authorisation_handlers(bot: Client) -> None:

    # ── /addauth <user_id> ────────────────────────────────────────────────────
    @bot.on_message(filters.command("addauth") & filters.private)
    async def add_auth_user(client: Client, message: Message) -> None:
        if message.chat.id != OWNER:
            return
        try:
            new_id = int(message.command[1])
        except (IndexError, ValueError):
            await message.reply_text("**Usage:** `/addauth <user_id>`")
            return

        if new_id in AUTH_USERS:
            await message.reply_text(f"**User `{new_id}` is already authorized.**")
            return

        AUTH_USERS.append(new_id)
        await message.reply_text(f"✅ **User `{new_id}` added to Premium.**")
        try:
            await client.send_message(
                new_id,
                "🎉 <b>Congratulations! You have been added to Premium Membership!</b>\n"
                "You now have full access to the bot. Use /start to begin."
            )
        except Exception:
            pass  # User may have blocked the bot

    # ── /rmauth <user_id> ─────────────────────────────────────────────────────
    @bot.on_message(filters.command("rmauth") & filters.private)
    async def remove_auth_user(client: Client, message: Message) -> None:
        if message.chat.id != OWNER:
            return
        try:
            rm_id = int(message.command[1])
        except (IndexError, ValueError):
            await message.reply_text("**Usage:** `/rmauth <user_id>`")
            return

        if rm_id == OWNER:
            await message.reply_text("**Cannot remove the owner.**")
            return

        if rm_id not in AUTH_USERS:
            await message.reply_text(f"**User `{rm_id}` is not in the authorized list.**")
            return

        AUTH_USERS.remove(rm_id)
        await message.reply_text(f"✅ **User `{rm_id}` removed from Premium.**")
        try:
            await client.send_message(
                rm_id,
                "⚠️ <b>Your Premium Membership has been removed.</b>\n"
                "Contact the owner to renew your subscription."
            )
        except Exception:
            pass

    # ── /users ────────────────────────────────────────────────────────────────
    @bot.on_message(filters.command("users") & filters.private)
    async def list_auth_users(client: Client, message: Message) -> None:
        if message.chat.id != OWNER:
            return
        if not AUTH_USERS:
            await message.reply_text("**No authorized users.**")
            return
        lines = "\n".join(
            f"• `{uid}`" + (" 👑 _(Owner)_" if uid == OWNER else "")
            for uid in AUTH_USERS
        )
        await message.reply_text(
            f"<b>🔐 Premium Users ({len(AUTH_USERS)}):</b>\n\n{lines}"
        )
