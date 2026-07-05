import asyncio
import random

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_TOKEN, CHANNEL_1, CHANNEL_2, ADMIN_ID, BOT_USERNAME
from database import add_file, get_file

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

waiting = {}


# ======================
# CHECK JOIN
# ======================
async def check_user(user_id: int):
    for ch in [CHANNEL_1, CHANNEL_2]:
        member = await bot.get_chat_member(ch, user_id)
        if member.status not in ["member", "administrator", "creator"]:
            return False
    return True


# ======================
# KEYBOARD
# ======================
join_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📢 کانال 1", url=f"https://t.me/{CHANNEL_1.replace('@','')}")],
        [InlineKeyboardButton(text="📢 کانال 2", url=f"https://t.me/{CHANNEL_2.replace('@','')}")],
        [InlineKeyboardButton(text="✅ بررسی عضویت", callback_data="check")]
    ]
)


# ======================
# START
# ======================
@dp.message(CommandStart())
async def start(message: Message):

    args = message.text.split()

    if len(args) > 1:
        code = args[1]

        file = get_file(code)

        if not file:
            await message.answer("❌ فایل پیدا نشد")
            return

        if await check_user(message.from_user.id):
            await message.answer_document(file[0], caption=f"📁 {file[1]}")
        else:
            await message.answer("❌ اول عضو کانال‌ها شو", reply_markup=join_kb)
        return

    await message.answer("👋 خوش آمدی", reply_markup=join_kb)


# ======================
# CHECK BUTTON
# ======================
@dp.callback_query(F.data == "check")
async def check(callback: CallbackQuery):

    if await check_user(callback.from_user.id):
        await callback.message.edit_text("✅ تایید شد")
    else:
        await callback.answer("❌ هنوز عضو نیستی", show_alert=True)


# ======================
# ADMIN - ADD FILE
# ======================
@dp.message(Command("add"))
async def add(message: Message):

    if str(message.from_user.id) != str(ADMIN_ID):
        return

    waiting[message.from_user.id] = True
    await message.answer("📁 فایل بفرست")


# ======================
# SAVE FILE + LINK
# ======================
@dp.message(F.document)
async def save(message: Message):

    if str(message.from_user.id) != str(ADMIN_ID):
        return

    if not waiting.get(message.from_user.id):
        return

    file_id = message.document.file_id
    name = message.document.file_name

    # 🔥 لینک حرفه‌ای
    code = f"file_{random.randint(1000, 9999)}"

    add_file(code, file_id, name)

    waiting[message.from_user.id] = False

    link = f"https://t.me/{BOT_USERNAME}?start={code}"

    await message.answer(
        f"✅ فایل ذخیره شد\n\n🔗 لینک دانلود:\n{link}"
    )


# ======================
# RUN BOT
# ======================
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())