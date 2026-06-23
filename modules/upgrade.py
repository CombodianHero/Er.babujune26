"""
upgrade.py — Plans / upgrade info button callback.
"""
from vars import CREDIT, OWNER
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

_UPGRADE_IMAGE = "https://envs.sh/GVI.jpg"


def register_upgrade_handlers(bot: Client) -> None:

    @bot.on_callback_query(filters.regex("^upgrade_command$"))
    async def upgrade_button(client, cq):
        name = cq.from_user.first_name
        uid  = cq.from_user.id
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                f"💬 Contact {CREDIT}",
                url=f"tg://openmessage?user_id={OWNER}"
            )],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main_menu")],
        ])
        text = (
            f"🎉 **Welcome [{name}](tg://user?id={uid})!**\n\n"
            f"Upgrade to **Premium** and unlock full download access:\n\n"
            f"<blockquote>"
            f"• 📚 Appx Zip + Encrypted URLs\n"
            f"• 🎓 Classplus DRM & Non-DRM\n"
            f"• 🧑‍🏫 PhysicsWallah DRM\n"
            f"• 📚 CareerWill + PDF\n"
            f"• 🎓 Khan GS\n"
            f"• 🎓 Study IQ DRM\n"
            f"• 🚀 APPX + Encrypted PDF\n"
            f"• 🎓 Vimeo Protected\n"
            f"• 🎓 Brightcove Protected\n"
            f"• 🎓 VisionIAS Protected\n"
            f"• 🎓 Zoom Video\n"
            f"• 🎓 Utkarsh (Video + PDF)\n"
            f"• 🎓 All Non-DRM / AES Encrypted URLs\n"
            f"• 🎓 MPD URLs with known key\n"
            f"</blockquote>\n\n"
            f"<b>💵 Monthly Plan: ₹100 / month</b>\n\n"
            f"Contact [{CREDIT}](tg://openmessage?user_id={OWNER}) to get started! 🚀"
        )
        await cq.message.edit_media(
            InputMediaPhoto(media=_UPGRADE_IMAGE, caption=text),
            reply_markup=keyboard,
        )
        await cq.answer()
