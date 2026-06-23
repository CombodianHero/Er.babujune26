"""
settings.py — Bot settings panel: caption style, file name, thumbnail,
              credit, tokens, watermark, video quality, topic mode, reset.
"""
import globals
from vars import CREDIT
from pyromod import listen
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

_SETTINGS_IMAGE = "https://envs.sh/GVI.jpg"
_PANEL_IMAGE    = "https://tinypic.host/images/2025/07/14/file_00000000fc2461fbbdd6bc500cecbff8_conversation_id6874702c-9760-800e-b0bf-8e0bcf8a3833message_id964012ce-7ef5-4ad4-88e0-1c41ed240c03-1-1.jpg"

_QUALITY_MAP = {
    "144":  ("256x144",   "144p"),
    "240":  ("426x240",   "240p"),
    "360":  ("640x360",   "360p"),
    "480":  ("854x480",   "480p"),
    "720":  ("1280x720",  "720p"),
    "1080": ("1920x1080", "1080p"),
}


def register_settings_handlers(bot: Client) -> None:

    # ── Settings root panel ───────────────────────────────────────────────────
    @bot.on_callback_query(filters.regex("^setttings$"))
    async def settings_panel(client, cq):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Caption Style",  callback_data="caption_style_command"),
             InlineKeyboardButton("🖋️ File Name",      callback_data="file_name_command")],
            [InlineKeyboardButton("🌅 Thumbnail",      callback_data="thummbnail_command")],
            [InlineKeyboardButton("✍️ Add Credit",     callback_data="add_credit_command"),
             InlineKeyboardButton("🔏 Set Token",      callback_data="set_token_command")],
            [InlineKeyboardButton("💧 Watermark",      callback_data="wattermark_command")],
            [InlineKeyboardButton("📽️ Video Quality",  callback_data="quality_command"),
             InlineKeyboardButton("🏷️ Topic",          callback_data="topic_command")],
            [InlineKeyboardButton("🔄 Reset All",      callback_data="resset_command")],
            [InlineKeyboardButton("🔙 Back to Main",   callback_data="back_to_main_menu")],
        ])
        await cq.message.edit_media(
            InputMediaPhoto(
                media=_SETTINGS_IMAGE,
                caption="✨ <b>Premium BOT Settings Panel</b> ✨\n\n"
                        f"<i>Current Quality: <b>{globals.quality}</b> | "
                        f"Caption: <b>{globals.caption}</b></i>"
            ),
            reply_markup=keyboard,
        )
        await cq.answer()

    # ── Thumbnail sub-menu ────────────────────────────────────────────────────
    @bot.on_callback_query(filters.regex("^thummbnail_command$"))
    async def thumbnail_menu(client, cq):
        name = cq.from_user.first_name
        uid  = cq.from_user.id
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎥 Video Thumb", callback_data="viideo_thumbnail_command"),
             InlineKeyboardButton("📑 PDF Thumb",   callback_data="pddf_thumbnail_command")],
            [InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")],
        ])
        await cq.message.edit_media(
            InputMediaPhoto(
                media=_PANEL_IMAGE,
                caption=f"✨ **[{name}](tg://user?id={uid}) — Choose Thumbnail type:**"
            ),
            reply_markup=keyboard,
        )
        await cq.answer()

    # ── Watermark sub-menu ────────────────────────────────────────────────────
    @bot.on_callback_query(filters.regex("^wattermark_command$"))
    async def watermark_menu(client, cq):
        name = cq.from_user.first_name
        uid  = cq.from_user.id
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎥 Video WM", callback_data="video_wateermark_command"),
             InlineKeyboardButton("📑 PDF WM",   callback_data="pdf_wateermark_command")],
            [InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")],
        ])
        await cq.message.edit_media(
            InputMediaPhoto(
                media=_PANEL_IMAGE,
                caption=f"✨ **[{name}](tg://user?id={uid}) — Choose Watermark type:**"
            ),
            reply_markup=keyboard,
        )
        await cq.answer()

    # ── Token sub-menu ────────────────────────────────────────────────────────
    @bot.on_callback_query(filters.regex("^set_token_command$"))
    async def token_menu(client, cq):
        name = cq.from_user.first_name
        uid  = cq.from_user.id
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Classplus",       callback_data="cp_token_command")],
            [InlineKeyboardButton("PhysicsWallah",   callback_data="pw_token_command"),
             InlineKeyboardButton("CareerWill",      callback_data="cw_token_command")],
            [InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")],
        ])
        await cq.message.edit_media(
            InputMediaPhoto(
                media=_PANEL_IMAGE,
                caption=f"✨ **[{name}](tg://user?id={uid}) — Choose platform to set token:**"
            ),
            reply_markup=keyboard,
        )
        await cq.answer()

    # ── Caption style ─────────────────────────────────────────────────────────
    @bot.on_callback_query(filters.regex("^caption_style_command$"))
    async def caption_style(client, cq):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]
        ])
        editable = await cq.message.edit(
            "**Caption Style Preview:**\n\n"
            "**Style /cc1:**\n"
            "<blockquote expandable><b>[🎥] Vid Id: 001\n"
            "Video Title: `Name [480p].mkv`\n"
            "Batch Name: Course Name\n\n"
            "Extracted by➤ Credit</b></blockquote>\n\n"
            "**Style /cc2:**\n"
            "<blockquote expandable><b>——— ✦ 001 ✦ ———\n\n"
            "🎞️ Title: Name\n"
            "├── Extension: .mkv\n"
            "├── Resolution: [854x480]\n"
            "📚 Course: Batch Name\n\n"
            "🌟 Extracted By: Credit</b></blockquote>\n\n"
            "**Style /cc3:**\n"
            "<blockquote expandable><b>001. Name [480p] .mkv</b></blockquote>\n\n"
            "**Send /cc1, /cc2, /cc3, or your own custom caption:**",
            reply_markup=keyboard,
        )
        input_msg = await bot.listen(editable.chat.id)
        try:
            choice = input_msg.text.lower().strip()
            if choice == "/cc1":
                globals.caption = "/cc1"
                await editable.edit("✅ **Caption Style 1 set!**", reply_markup=keyboard)
            elif choice == "/cc2":
                globals.caption = "/cc2"
                await editable.edit("✅ **Caption Style 2 set!**", reply_markup=keyboard)
            elif choice == "/cc3":
                globals.caption = "/cc3"
                await editable.edit("✅ **Caption Style 3 set!**", reply_markup=keyboard)
            else:
                globals.caption = input_msg.text
                await editable.edit(f"✅ **Custom caption saved!**", reply_markup=keyboard)
        except Exception as e:
            await editable.edit(
                f"<b>❌ Failed:</b>\n<blockquote expandable>{e}</blockquote>",
                reply_markup=keyboard,
            )
        finally:
            await input_msg.delete()

    # ── End file name ─────────────────────────────────────────────────────────
    @bot.on_callback_query(filters.regex("^file_name_command$"))
    async def file_name_setting(client, cq):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]
        ])
        editable = await cq.message.edit(
            "**Send the suffix to append to every file name.**\n"
            "_Example:_ `By Saini` → `001 Lecture By Saini.mp4`\n\n"
            "Send `/d` to disable.",
            reply_markup=keyboard,
        )
        input_msg = await bot.listen(editable.chat.id)
        try:
            val = input_msg.text.strip()
            globals.endfilename = "/d" if val.lower() == "/d" else val
            label = "Disabled" if globals.endfilename == "/d" else f"`{globals.endfilename}`"
            await editable.edit(f"✅ End File Name → {label}!", reply_markup=keyboard)
        except Exception as e:
            await editable.edit(
                f"<b>❌ Failed:</b>\n<blockquote expandable>{e}</blockquote>",
                reply_markup=keyboard,
            )
        finally:
            await input_msg.delete()

    # ── Video thumbnail ───────────────────────────────────────────────────────
    @bot.on_callback_query(filters.regex("^viideo_thumbnail_command$"))
    async def video_thumbnail(client, cq):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="thummbnail_command")]
        ])
        editable = await cq.message.edit(
            "**Send thumbnail URL (http/https) or send `/d` for auto-generated.**\n\n"
            "<blockquote><b>Note:</b> Send `No` to upload as document instead of video.</blockquote>",
            reply_markup=keyboard,
        )
        input_msg = await bot.listen(editable.chat.id)
        try:
            val = input_msg.text.strip()
            globals.thumb = val
            if val.lower() == "/d":
                msg = "✅ Thumbnail → Auto-generated from video!"
            elif val.lower() in ("no", "document"):
                msg = "✅ Videos will be sent as Documents!"
            else:
                msg = "✅ Custom thumbnail URL saved!"
            await editable.edit(msg, reply_markup=keyboard)
        except Exception as e:
            await editable.edit(
                f"<b>❌ Failed:</b>\n<blockquote expandable>{e}</blockquote>",
                reply_markup=keyboard,
            )
        finally:
            await input_msg.delete()

    # ── PDF thumbnail (not yet implemented) ───────────────────────────────────
    @bot.on_callback_query(filters.regex("^pddf_thumbnail_command$"))
    async def pdf_thumbnail(client, cq):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="thummbnail_command")]
        ])
        await cq.message.edit_media(
            InputMediaPhoto(
                media=_SETTINGS_IMAGE,
                caption="<b>⋅ PDF Thumbnail is not yet available. Coming soon! ⋅</b>"
            ),
            reply_markup=keyboard,
        )
        await cq.answer()

    # ── Add credit ────────────────────────────────────────────────────────────
    @bot.on_callback_query(filters.regex("^add_credit_command$"))
    async def add_credit(client, cq):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]
        ])
        editable = await cq.message.edit(
            f"**Send your credit/brand name.**\n_Current:_ `{globals.CR}`\n\nSend `/d` to reset.",
            reply_markup=keyboard,
        )
        input_msg = await bot.listen(editable.chat.id)
        try:
            val = input_msg.text.strip()
            globals.CR = CREDIT if val.lower() == "/d" else val
            await editable.edit(f"✅ Credit → `{globals.CR}`!", reply_markup=keyboard)
        except Exception as e:
            await editable.edit(
                f"<b>❌ Failed:</b>\n<blockquote expandable>{e}</blockquote>",
                reply_markup=keyboard,
            )
        finally:
            await input_msg.delete()

    # ── ClassPlus token ───────────────────────────────────────────────────────
    @bot.on_callback_query(filters.regex("^cp_token_command$"))
    async def cp_token(client, cq):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="set_token_command")]
        ])
        editable = await cq.message.edit("**Send your ClassPlus token:**", reply_markup=keyboard)
        input_msg = await bot.listen(editable.chat.id)
        try:
            globals.cptoken = input_msg.text.strip()
            await editable.edit(
                f"✅ ClassPlus Token saved!\n\n<blockquote expandable>`{globals.cptoken}`</blockquote>",
                reply_markup=keyboard,
            )
        except Exception as e:
            await editable.edit(
                f"<b>❌ Failed:</b>\n<blockquote expandable>{e}</blockquote>",
                reply_markup=keyboard,
            )
        finally:
            await input_msg.delete()

    # ── PhysicsWallah token ───────────────────────────────────────────────────
    @bot.on_callback_query(filters.regex("^pw_token_command$"))
    async def pw_token(client, cq):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="set_token_command")]
        ])
        editable = await cq.message.edit(
            "**Send your PhysicsWallah batch token:**", reply_markup=keyboard
        )
        input_msg = await bot.listen(editable.chat.id)
        try:
            globals.pwtoken = input_msg.text.strip()
            await editable.edit(
                f"✅ PhysicsWallah Token saved!\n\n<blockquote expandable>`{globals.pwtoken}`</blockquote>",
                reply_markup=keyboard,
            )
        except Exception as e:
            await editable.edit(
                f"<b>❌ Failed:</b>\n<blockquote expandable>{e}</blockquote>",
                reply_markup=keyboard,
            )
        finally:
            await input_msg.delete()

    # ── CareerWill token ──────────────────────────────────────────────────────
    @bot.on_callback_query(filters.regex("^cw_token_command$"))
    async def cw_token(client, cq):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="set_token_command")]
        ])
        editable = await cq.message.edit(
            "**Send your CareerWill token, or `/d` to reset to default:**",
            reply_markup=keyboard,
        )
        input_msg = await bot.listen(editable.chat.id)
        try:
            val = input_msg.text.strip()
            if val.lower() == "/d":
                globals.cwtoken = ""
                await editable.edit("✅ CareerWill Token reset to default!", reply_markup=keyboard)
            else:
                globals.cwtoken = val
                await editable.edit(
                    f"✅ CareerWill Token saved!\n\n<blockquote expandable>`{globals.cwtoken}`</blockquote>",
                    reply_markup=keyboard,
                )
        except Exception as e:
            await editable.edit(
                f"<b>❌ Failed:</b>\n<blockquote expandable>{e}</blockquote>",
                reply_markup=keyboard,
            )
        finally:
            await input_msg.delete()

    # ── Video watermark ───────────────────────────────────────────────────────
    @bot.on_callback_query(filters.regex("^video_wateermark_command$"))
    async def video_watermark(client, cq):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="wattermark_command")]
        ])
        editable = await cq.message.edit(
            "**Send watermark text to overlay on videos.**\nSend `/d` to disable.",
            reply_markup=keyboard,
        )
        input_msg = await bot.listen(editable.chat.id)
        try:
            val = input_msg.text.strip()
            globals.vidwatermark = "/d" if val.lower() == "/d" else val
            label = "Disabled" if globals.vidwatermark == "/d" else f"`{globals.vidwatermark}`"
            await editable.edit(f"✅ Video Watermark → {label}!", reply_markup=keyboard)
        except Exception as e:
            await editable.edit(
                f"<b>❌ Failed:</b>\n<blockquote expandable>{e}</blockquote>",
                reply_markup=keyboard,
            )
        finally:
            await input_msg.delete()

    # ── PDF watermark (not yet implemented) ───────────────────────────────────
    @bot.on_callback_query(filters.regex("^pdf_wateermark_command$"))
    async def pdf_watermark(client, cq):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="wattermark_command")]
        ])
        await cq.message.edit_media(
            InputMediaPhoto(
                media=_SETTINGS_IMAGE,
                caption="<b>⋅ PDF Watermark is not yet available. Coming soon! ⋅</b>"
            ),
            reply_markup=keyboard,
        )
        await cq.answer()

    # ── Video quality ─────────────────────────────────────────────────────────
    @bot.on_callback_query(filters.regex("^quality_command$"))
    async def set_quality(client, cq):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]
        ])
        editable = await cq.message.edit(
            f"**Select video quality (send the number):**\n\n"
            f"╭━━━━❰ Quality ❱━━━━━╮\n"
            f"┣━ `144`  → 144p\n"
            f"┣━ `240`  → 240p\n"
            f"┣━ `360`  → 360p\n"
            f"┣━ `480`  → 480p _(default)_\n"
            f"┣━ `720`  → 720p\n"
            f"┣━ `1080` → 1080p\n"
            f"╰━━━━━━━━━━━━━━━━━━━╯\n\n"
            f"_Current: **{globals.quality}**_\n"
            f"Send `/d` to reset to 480p.",
            reply_markup=keyboard,
        )
        input_msg = await bot.listen(editable.chat.id)
        try:
            val = input_msg.text.strip()
            if val.lower() == "/d":
                val = "480"
            if val in _QUALITY_MAP:
                globals.res, globals.quality = _QUALITY_MAP[val]
                globals.raw_text2 = val
                await editable.edit(
                    f"✅ Quality → **{globals.quality}** ({globals.res})!",
                    reply_markup=keyboard,
                )
            else:
                await editable.edit(
                    "⚠️ Invalid input. Quality reset to **480p**.", reply_markup=keyboard
                )
                globals.raw_text2, globals.quality, globals.res = "480", "480p", "854x480"
        except Exception as e:
            await editable.edit(
                f"<b>❌ Failed:</b>\n<blockquote expandable>{e}</blockquote>",
                reply_markup=keyboard,
            )
        finally:
            await input_msg.delete()

    # ── Topic mode ────────────────────────────────────────────────────────────
    @bot.on_callback_query(filters.regex("^topic_command$"))
    async def topic_setting(client, cq):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]
        ])
        editable = await cq.message.edit(
            "**Topic Mode** — parses chapter/topic from `(brackets)` in titles.\n\n"
            "Send `/yes` to enable, or `/d` to disable.\n\n"
            "<blockquote><b>Example title:</b> `(Chapter 1) Newton's Laws`\n"
            "→ Topic: `Chapter 1` | Title: `Newton's Laws`</blockquote>",
            reply_markup=keyboard,
        )
        input_msg = await bot.listen(editable.chat.id)
        try:
            val = input_msg.text.strip().lower()
            globals.topic = "/yes" if val == "/yes" else "/d"
            label = "Enabled ✅" if globals.topic == "/yes" else "Disabled ✅"
            await editable.edit(f"**Topic Mode → {label}!**", reply_markup=keyboard)
        except Exception as e:
            await editable.edit(
                f"<b>❌ Failed:</b>\n<blockquote expandable>{e}</blockquote>",
                reply_markup=keyboard,
            )
        finally:
            await input_msg.delete()

    # ── Reset all settings ────────────────────────────────────────────────────
    @bot.on_callback_query(filters.regex("^resset_command$"))
    async def reset_settings(client, cq):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]
        ])
        editable = await cq.message.edit(
            "⚠️ **Reset ALL settings to defaults?**\n\nSend `/yes` to confirm, or `/no` to cancel.",
            reply_markup=keyboard,
        )
        input_msg = await bot.listen(editable.chat.id)
        try:
            if input_msg.text.strip().lower() == "/yes":
                globals.caption      = "/cc1"
                globals.endfilename  = "/d"
                globals.thumb        = "/d"
                globals.CR           = CREDIT
                globals.cwtoken      = ""
                globals.cptoken      = ""
                globals.pwtoken      = ""
                globals.vidwatermark = "/d"
                globals.raw_text2    = "480"
                globals.quality      = "480p"
                globals.res          = "854x480"
                globals.topic        = "/d"
                await editable.edit("✅ **All settings reset to defaults!**", reply_markup=keyboard)
            else:
                await editable.edit("✅ **Settings unchanged.**", reply_markup=keyboard)
        except Exception as e:
            await editable.edit(
                f"<b>❌ Failed:</b>\n<blockquote expandable>{e}</blockquote>",
                reply_markup=keyboard,
            )
        finally:
            await input_msg.delete()
