"""
broadcast.py — Owner-only broadcast commands.
"""
import asyncio
from vars import OWNER, TOTAL_USERS
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, PeerIdInvalid, UserIsBlocked, InputUserDeactivated


def register_broadcast_handlers(bot: Client) -> None:

    # ── /broadcast (reply to any message) ────────────────────────────────────
    @bot.on_message(filters.command("broadcast") & filters.private)
    async def broadcast_handler(client: Client, message: Message) -> None:
        if message.chat.id != OWNER:
            return
        if not message.reply_to_message:
            await message.reply_text(
                "**Reply to any message with /broadcast to send it to all users.**"
            )
            return

        status = await message.reply_text("📢 **Broadcasting... please wait.**")
        success = fail = 0
        msg = message.reply_to_message

        for user_id in list(set(TOTAL_USERS)):
            try:
                if msg.text:
                    await client.send_message(user_id, msg.text)
                elif msg.photo:
                    await client.send_photo(user_id, msg.photo.file_id, caption=msg.caption or "")
                elif msg.video:
                    await client.send_video(user_id, msg.video.file_id, caption=msg.caption or "")
                elif msg.document:
                    await client.send_document(user_id, msg.document.file_id, caption=msg.caption or "")
                elif msg.sticker:
                    await client.send_sticker(user_id, msg.sticker.file_id)
                else:
                    await client.forward_messages(user_id, message.chat.id, msg.id)
                success += 1
                await asyncio.sleep(0.05)   # stay well under 30 msg/s Telegram limit
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except (PeerIdInvalid, UserIsBlocked, InputUserDeactivated):
                fail += 1
            except Exception:
                fail += 1

        await status.edit(
            f"<b>✅ Broadcast Complete!</b>\n"
            f"<blockquote>"
            f"✅ Sent: <b>{success}</b>\n"
            f"❌ Failed: <b>{fail}</b>\n"
            f"👥 Total: <b>{success + fail}</b>"
            f"</blockquote>"
        )

    # ── /broadusers ───────────────────────────────────────────────────────────
    @bot.on_message(filters.command("broadusers") & filters.private)
    async def broadusers_handler(client: Client, message: Message) -> None:
        if message.chat.id != OWNER:
            return

        unique = list(set(TOTAL_USERS))
        if not unique:
            await message.reply_text("**No users have started the bot yet.**")
            return

        fetching = await message.reply_text(f"⏳ Fetching info for **{len(unique)}** users...")
        lines = []
        for uid in unique:
            try:
                user = await client.get_users(uid)
                name = user.first_name or "Unknown"
                lines.append(f"• [{uid}](tg://openmessage?user_id={uid}) — `{name}`")
            except Exception:
                lines.append(f"• `{uid}` — _unavailable_")

        text = f"<b>👥 Bot Users ({len(lines)}):</b>\n\n" + "\n".join(lines)

        # Telegram message limit ~4096 chars — split if needed
        if len(text) <= 4000:
            await fetching.edit(text, disable_web_page_preview=True)
        else:
            await fetching.delete()
            chunk = ""
            for line in lines:
                if len(chunk) + len(line) + 1 > 3900:
                    await message.reply_text(chunk, disable_web_page_preview=True)
                    chunk = ""
                chunk += line + "\n"
            if chunk:
                await message.reply_text(chunk, disable_web_page_preview=True)
