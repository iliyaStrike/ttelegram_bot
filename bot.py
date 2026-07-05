import asyncio
import random

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_TOKEN, CHANNEL_1, CHANNEL_2, ADMIN_ID
from database import add_file, get_file

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

waiting = {}


# =====================
# CHECK JOIN
# =====================
async def check_user(user_id: int):
    for ch in [CHANNEL_1, CHANNEL_2]:
        member = await bot.get_chat_member(ch, user_id)
        if member.status not in ["member", "administrator", "creator"]:
            return False
    return True


# =====================
# KEYBOARD
# =====================
join_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📢 کانال 1", url=f"https://t.me/{CHANNEL_1.replace('@','')}")],
        [InlineKeyboardButton(text="📢 کانال 2", url=f"https://t.me/{CHANNEL_2.replace('@','')}")],
        [InlineKeyboardButton(text="✅ بررسی عضویت", callback_data="check")]
    ]
)


# =====================
# START
# =====================
@dp.message(CommandStart())
async def start(message: Message):

    args = message.text.split()

    if len(args) > 1:
        code = args[1]
        file_id = get_file(code)

        if not file_id:
            await message.answer("❌ فایل پیدا نشد")
            return

        if await check_user(message.from_user.id):
            await message.answer_document(file_id, caption="📁 فایل شما")
        else:
            await message.answer("❌ اول عضو شو", reply_markup=join_kb)
        return

    await message.answer("👋 خوش آمدی", reply_markup=join_kb)


# =====================
# CHECK BUTTON
# =====================
@dp.callback_query(F.data == "check")
async def check(callback: CallbackQuery):

    if await check_user(callback.from_user.id):
        await callback.message.edit_text("✅ تایید شد")
    else:
        await callback.answer("❌ هنوز عضو نیستی", show_alert=True)


# =====================
# ADMIN ADD FILE
# =====================
@dp.message(Command("add"))
async def add(message: Message):

    if str(message.from_user.id) != str(ADMIN_ID):
        return

    waiting[message.from_user.id] = True
    await message.answer("📁 فایل بفرست")


# =====================
# SAVE FILE
# =====================
@dp.message(F.document)
async def save(message: Message):

    if str(message.from_user.id) != str(ADMIN_ID):
        return

    if not waiting.get(message.from_user.id):
        return

    file_id = message.document.file_id
    name = message.document.file_name

    code = str(random.randint(1000, 9999))

    add_file(code, file_id, name)

    waiting[message.from_user.id] = False

    await message.answer(
        f"✅ ذخیره شد\n\n🔗 لینک:\nhttps://t.me/@dylan_channel_bot?start={code}"
    )


# =====================
# RUN
# =====================
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())