"""
text_handler.py — /t2t command: convert plain text into a .txt file.
"""
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen


async def text_to_txt(bot: Client, message: Message) -> None:
    editable = await message.reply_text(
        "<blockquote><b>📝 Text → .txt Converter\n\n"
        "Send the text you want to save as a .txt file:</b></blockquote>"
    )

    # 1. Get text content
    input_msg: Message = await bot.listen(message.chat.id)
    if not input_msg.text:
        await editable.edit("❌ **Please send valid text.**")
        await input_msg.delete()
        return
    text_data = input_msg.text.strip()
    await input_msg.delete()

    # 2. Get desired filename
    await editable.edit("**Send a file name (without extension), or /d for default:**")
    name_msg: Message = await bot.listen(message.chat.id)
    raw_name = name_msg.text.strip()
    await name_msg.delete()
    await editable.delete()

    file_name = "txt_file" if raw_name.lower() == "/d" else raw_name
    # Sanitize filename
    for ch in r'\/:*?"<>|':
        file_name = file_name.replace(ch, "")
    file_name = file_name.strip() or "txt_file"

    # 3. Write and send
    os.makedirs("downloads", exist_ok=True)
    path = os.path.join("downloads", f"{file_name}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text_data)

    await message.reply_document(
        document=path,
        caption=(
            f"`{file_name}.txt`\n\n"
            "<blockquote>✅ Your .txt file is ready! Download it below.</blockquote>"
        ),
    )
    os.remove(path)


def register_text_handlers(bot: Client) -> None:

    @bot.on_message(filters.command("t2t") & filters.private)
    async def call_text_to_txt(client: Client, m: Message) -> None:
        await text_to_txt(client, m)
